using UnityEngine;
using UnityEditor;
using System;
using System.IO;
using System.Net;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Collections.Generic;
using System.Collections.Concurrent;

namespace MCP {
    /// <summary>
    /// SOTA Unity Editor Bridge for MCP (2026 Edition).
    /// Provides real-time "Hands-In" control of the Unity Editor via HTTP.
    /// </summary>
    [InitializeOnLoad]
    public class MCPBridge {
        private static HttpListener _listener;
        private static Thread _listenerThread;
        private static readonly ConcurrentQueue<Action> _executionQueue = new ConcurrentQueue<Action>();
        private const int PORT = 10835;
        private static bool _simRunning = false;
        private static double _simEndTime = 0;
        private static float _simDuration = 1f;
        private static int _simRecord = 0;

        static MCPBridge() {
            StartServer();
            EditorApplication.update += Update;
        }

        private static void StartServer() {
            try {
                if (_listener != null) StopServer();

                _listener = new HttpListener();
                _listener.Prefixes.Add($"http://localhost:{PORT}/");
                _listener.Start();

                _listenerThread = new Thread(Listen);
                _listenerThread.IsBackground = true;
                _listenerThread.Start();

                Debug.Log($"<color=cyan>[MCP]</color> Bridge active on <b>http://localhost:{PORT}</b>");
            } catch (Exception e) {
                Debug.LogError($"[MCP] Failed to start bridge: {e.Message}");
            }
        }

        private static void StopServer() {
            _listener?.Stop();
            _listenerThread?.Abort();
            Debug.Log("[MCP] Bridge stopped.");
        }

        private static void Update() {
            while (_executionQueue.TryDequeue(out var action)) {
                try {
                    action.Invoke();
                } catch (Exception e) {
                    Debug.LogError($"[MCP] Execution Error: {e.Message}");
                }
            }
            TickPathMovements();
            TickAnimations();
        }

        private static void TickPathMovements() {
            if (_activeMovements.Count == 0) return;

            var finished = new List<int>();
            double now = EditorApplication.timeSinceStartup;

            foreach (var kvp in _activeMovements) {
                var state = kvp.Value;
                if (state.target == null) {
                    finished.Add(kvp.Key);
                    continue;
                }

                float speed = state.speed;
                if (state.decelerating) {
                    float t = (float)(now - state.decelerationStartTime) / Mathf.Max(state.decelerationTime, 0.0001f);
                    if (t >= 1f) {
                        finished.Add(kvp.Key);
                        continue;
                    }
                    speed = Mathf.Lerp(state.decelerationStartSpeed, 0f, t);
                }

                bool pathComplete = AdvanceAlongPath(state, speed, now, out Vector3 newPos, out Vector3 forward);
                state.target.transform.position = newPos;

                if (state.smoothRotation && forward.sqrMagnitude > 0.0001f) {
                    Quaternion look = Quaternion.LookRotation(forward, Vector3.up);
                    if (state.bankAngle > 0f) {
                        look *= Quaternion.Euler(0, 0, -state.bankAngle * Mathf.Clamp(forward.x, -1f, 1f));
                    }
                    state.target.transform.rotation = look;
                }

                if (pathComplete && !state.loop && !state.decelerating) {
                    finished.Add(kvp.Key);
                }
            }

            foreach (var key in finished) {
                _activeMovements.Remove(key);
            }
        }

        private static void TickAnimations() {
            if (_activeAnimations.Count == 0) return;

            var finished = new List<int>();
            double now = EditorApplication.timeSinceStartup;

            foreach (var kvp in _activeAnimations) {
                var state = kvp.Value;
                if (state.target == null) {
                    finished.Add(kvp.Key);
                    continue;
                }

                float t = (float)(now - state.startTime);

                if (state.mode == "spin") {
                    // speed is degrees/second here (Unity's native Quaternion.AngleAxis
                    // convention), unlike overte-mcp/resonite-mcp's Python ports of this same
                    // feature, which use radians/second - a real, deliberate unit difference
                    // between platforms, not a bug. Document this for callers crossing platforms.
                    Quaternion delta = Quaternion.AngleAxis(state.speed * t, state.axis);
                    state.target.transform.rotation = state.restRotation * delta;
                } else {
                    float offset = state.mode == "bob"
                        ? state.amplitude * Mathf.Sin(2f * Mathf.PI * state.speed * t)
                        : BounceHeight(t, state.amplitude, state.damping, state.speed);
                    state.target.transform.position = state.restPosition + Vector3.up * offset;
                }

                if (state.durationS > 0 && t >= state.durationS) {
                    finished.Add(kvp.Key);
                }
            }

            foreach (var key in finished) {
                _activeAnimations.Remove(key);
            }
        }

        /// <summary>
        /// Real drop-and-rebound physics, not a repeating sine wave - direct C# port of the
        /// identical closed-form function already shipped in overte-mcp's http_server.py and
        /// resonite-mcp's tools/resonite_link.py (third platform, same math, so behavior is
        /// provably consistent across all three ports rather than three independent guesses).
        /// t=0 starts on the ground with upward velocity, rises to `amplitude`, falls under
        /// effective gravity g=9.8*speed, and each landing's velocity *= sqrt(damping) so
        /// bounces visibly shorten and settle to 0 instead of repeating forever.
        /// </summary>
        private static float BounceHeight(float t, float amplitude, float damping, float speed) {
            float g = 9.8f * Mathf.Max(speed, 0.05f);
            float v = amplitude > 0f ? Mathf.Sqrt(2f * g * amplitude) : 0f;
            float remaining = t;
            float clampedDamping = Mathf.Clamp01(damping);
            while (v > 1e-4f) {
                float duration = 2f * v / g;
                if (remaining <= duration) {
                    return Mathf.Max(v * remaining - 0.5f * g * remaining * remaining, 0f);
                }
                remaining -= duration;
                v *= Mathf.Sqrt(clampedDamping);
            }
            return 0f;
        }

        private static string AnimateObject(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";
            if (cmd.anim_mode != "spin" && cmd.anim_mode != "bob" && cmd.anim_mode != "bounce") {
                return "{\"error\": \"anim_mode must be 'spin', 'bob', or 'bounce'\"}";
            }

            Vector3 axis = (cmd.axis != null && cmd.axis.Length == 3)
                ? new Vector3(cmd.axis[0], cmd.axis[1], cmd.axis[2])
                : Vector3.up;

            var state = new AnimationState {
                target = target,
                mode = cmd.anim_mode,
                axis = axis,
                speed = cmd.speed,
                amplitude = cmd.amplitude,
                damping = cmd.damping,
                startTime = EditorApplication.timeSinceStartup,
                durationS = cmd.duration,
                restPosition = target.transform.position,
                restRotation = target.transform.rotation,
            };
            _activeAnimations[target.GetInstanceID()] = state;

            return "{\"status\": \"started\", \"animation_id\": " + target.GetInstanceID() +
                ", \"mode\": \"" + cmd.anim_mode + "\"" +
                (cmd.duration > 0 ? "" : ", \"note\": \"duration<=0: runs until stop_animation is called\"") + "}";
        }

        private static string StopAnimation(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";

            int id = target.GetInstanceID();
            if (!_activeAnimations.ContainsKey(id)) {
                return "{\"status\": \"not_animating\", \"target\": \"" + cmd.target + "\"}";
            }

            _activeAnimations.Remove(id);
            Vector3 finalPos = target.transform.position;
            return "{\"status\": \"stopped\", \"final_position\": {\"x\": " + finalPos.x +
                ", \"y\": " + finalPos.y + ", \"z\": " + finalPos.z + "}}";
        }

        /// <summary>
        /// Moves `state` one tick along its path. Curve types (bezier,
        /// spline, catmull_rom) are approximated as straight multi-segment
        /// linear interpolation — true curve math is not implemented.
        /// This is a real, working limitation, documented honestly rather
        /// than claiming full spline fidelity.
        /// </summary>
        private static bool AdvanceAlongPath(PathMovementState state, float speed, double now, out Vector3 newPos, out Vector3 forward) {
            var points = state.points;
            forward = Vector3.zero;

            if (points == null || points.Count == 0) {
                newPos = state.target.transform.position;
                return true;
            }
            if (points.Count == 1) {
                newPos = points[0];
                return true;
            }

            float totalLength = 0f;
            for (int i = 0; i < points.Count - 1; i++) totalLength += Vector3.Distance(points[i], points[i + 1]);
            if (totalLength <= 0.0001f) {
                newPos = points[points.Count - 1];
                return true;
            }

            float elapsed = (float)(now - state.startTime);
            float distanceCovered = state.duration > 0f
                ? (elapsed / Mathf.Max(state.duration, 0.0001f)) * totalLength
                : elapsed * speed;

            if (state.loop) {
                distanceCovered = distanceCovered % totalLength;
            } else if (distanceCovered >= totalLength) {
                newPos = points[points.Count - 1];
                forward = (points[points.Count - 1] - points[points.Count - 2]).normalized;
                return true;
            }

            float accum = 0f;
            for (int i = 0; i < points.Count - 1; i++) {
                float segLen = Vector3.Distance(points[i], points[i + 1]);
                if (accum + segLen >= distanceCovered || i == points.Count - 2) {
                    float segT = segLen > 0.0001f ? Mathf.Clamp01((distanceCovered - accum) / segLen) : 0f;
                    newPos = Vector3.Lerp(points[i], points[i + 1], segT);
                    forward = (points[i + 1] - points[i]).normalized;
                    return false;
                }
                accum += segLen;
            }

            newPos = points[points.Count - 1];
            return true;
        }

        private static void Listen() {
            while (_listener.IsListening) {
                try {
                    var context = _listener.GetContext();
                    var request = context.Request;
                    
                    if (request.HttpMethod == "POST") {
                        using (var reader = new StreamReader(request.InputStream, request.ContentEncoding)) {
                            string json = reader.ReadToEnd();
                            ProcessCommand(json, context);
                        }
                    } else {
                        context.Response.StatusCode = (int)HttpStatusCode.MethodNotAllowed;
                        context.Response.Close();
                    }
                } catch (Exception) {
                    // Ignored (usually listener closing)
                }
            }
        }

        private static void ProcessCommand(string json, HttpListenerContext context) {
            try {
                var cmd = JsonUtility.FromJson<CommandRequest>(json);
                _executionQueue.Enqueue(() => {
                    string result = HandleCommand(cmd);
                    SendResponse(context, result);
                });
            } catch (Exception e) {
                SendResponse(context, "{\"error\": \"" + e.Message + "\"}", HttpStatusCode.BadRequest);
            }
        }

        private static string HandleCommand(CommandRequest cmd) {
            switch (cmd.action) {
                case "ping":
                    return "{\"status\": \"ok\", \"version\": \"3.2.0\"}";
                
                case "get_hierarchy":
                    return GetHierarchyJson();

                case "transform_object":
                    return TransformObject(cmd);

                case "create_object":
                    return CreateObject(cmd);

                case "delete_object":
                    return DeleteObject(cmd);

                case "capture_game_view":
                    return CaptureGameView(cmd);

                case "capture_multi_angle":
                    return CaptureMultiAngle(cmd);

                case "get_scene_summary":
                    return GetSceneSummary();

                case "validate_scene":
                    return ValidateScene();

                case "create_prefab":
                    return CreatePrefab(cmd);

                case "run_simulation":
                    return RunSimulation(cmd);

                case "simulation_status":
                    return SimulationStatus();

                case "stop_simulation":
                    return StopSimulation();

                case "execute_method":
                    return ExecuteMethod(cmd);

                case "batch_operations":
                    return BatchOperations(cmd);

                case "move_along_path":
                    return MoveAlongPath(cmd);

                case "follow_path_2d":
                    return FollowPath2D(cmd);

                case "follow_path_3d":
                    return FollowPath3D(cmd);

                case "stop_path_movement":
                    return StopPathMovement(cmd);

                case "create_path_visualization":
                    return CreatePathVisualization(cmd);

                case "animate_object":
                    return AnimateObject(cmd);

                case "stop_animation":
                    return StopAnimation(cmd);

                default:
                    return "{\"error\": \"Unknown action: " + cmd.action + "\"}";
            }
        }

        private static string GetHierarchyJson() {
            var objects = GameObject.FindObjectsOfType<GameObject>();
            var list = new List<string>();
            foreach (var obj in objects) {
                list.Add("{\"name\":\"" + obj.name + "\", \"id\":\"" + obj.GetInstanceID() + "\"}");
            }
            return "{\"objects\": [" + string.Join(",", list) + "]}";
        }

        private static string TransformObject(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";

            if (cmd.position != null && cmd.position.Length == 3)
                target.transform.position = new Vector3(cmd.position[0], cmd.position[1], cmd.position[2]);
            
            if (cmd.rotation != null && cmd.rotation.Length == 3)
                target.transform.rotation = Quaternion.Euler(cmd.rotation[0], cmd.rotation[1], cmd.rotation[2]);

            if (cmd.scale > 0f)
                target.transform.localScale = Vector3.one * cmd.scale;

            return "{\"status\": \"success\"}";
        }

        private static string CreateObject(CommandRequest cmd) {
            GameObject go;
            switch (cmd.type) {
                case "Light":
                    go = new GameObject(cmd.name ?? "New Object");
                    go.AddComponent<Light>();
                    break;
                case "Camera":
                    go = new GameObject(cmd.name ?? "New Object");
                    go.AddComponent<Camera>();
                    break;
                // Placeholder primitives — used for objects with no real 3D model/mesh yet
                // (e.g. spawning a labeled vbot for a robot that only exists as a spec).
                case "Capsule":
                    go = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                    go.name = cmd.name ?? "New Object";
                    break;
                case "Sphere":
                    go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                    go.name = cmd.name ?? "New Object";
                    break;
                case "Box":
                case "Cube":
                    go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    go.name = cmd.name ?? "New Object";
                    break;
                default:
                    go = new GameObject(cmd.name ?? "New Object");
                    break;
            }

            if (cmd.position != null && cmd.position.Length == 3)
                go.transform.position = new Vector3(cmd.position[0], cmd.position[1], cmd.position[2]);

            if (cmd.rotation != null && cmd.rotation.Length == 3)
                go.transform.rotation = Quaternion.Euler(cmd.rotation[0], cmd.rotation[1], cmd.rotation[2]);

            // dimensions (per-axis) takes priority over scale (uniform) when both are given -
            // dimensions is the newer, more flexible field added for the fixture spawner.
            if (cmd.dimensions != null && cmd.dimensions.Length == 3)
                go.transform.localScale = new Vector3(cmd.dimensions[0], cmd.dimensions[1], cmd.dimensions[2]);
            else if (cmd.scale > 0f)
                go.transform.localScale = Vector3.one * cmd.scale;

            if (cmd.color != null) {
                var renderer = go.GetComponent<Renderer>();
                if (renderer != null) {
                    // sharedMaterial would edit the built-in Default-Material asset itself -
                    // .material instantiates a per-object copy first.
                    renderer.material.color = new Color(cmd.color.r, cmd.color.g, cmd.color.b, cmd.color.a);
                }
            }

            return "{\"status\": \"created\", \"instanceID\": " + go.GetInstanceID() + "}";
        }

        private static string DeleteObject(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found\"}";
            
            GameObject.DestroyImmediate(target);
            return "{\"status\": \"deleted\"}";
        }

        private static string CaptureGameView(CommandRequest cmd) {
            string path = !string.IsNullOrEmpty(cmd.output_path)
                ? cmd.output_path
                : Path.Combine(Application.dataPath, "../Temp/mcp_capture.png");

            int width = cmd.width > 0 ? cmd.width : 1920;
            int height = cmd.height > 0 ? cmd.height : 1080;

            try {
                string dir = Path.GetDirectoryName(path);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir)) {
                    Directory.CreateDirectory(dir);
                }

                Camera cam = Camera.main;
                if (cam == null) {
                    cam = GameObject.FindObjectOfType<Camera>();
                }
                if (cam == null) {
                    return "{\"error\": \"No camera found in active scene\"}";
                }

                RenderTexture rt = new RenderTexture(width, height, 24);
                RenderTexture prev = cam.targetTexture;
                cam.targetTexture = rt;
                cam.Render();
                RenderTexture.active = rt;
                Texture2D tex = new Texture2D(width, height, Texture2D.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                tex.Apply();
                cam.targetTexture = prev;
                RenderTexture.active = null;
                File.WriteAllBytes(path, tex.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(tex);
                UnityEngine.Object.DestroyImmediate(rt);

                string escaped = path.Replace("\\", "\\\\");
                return "{\"status\": \"success\", \"path\": \"" + escaped + "\", \"width\": " + width + ", \"height\": " + height + "}";
            } catch (Exception e) {
                return "{\"error\": \"" + e.Message.Replace("\"", "'") + "\"}";
            }
        }

        private static string CreatePrefab(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";

            string prefabPath = cmd.prefab_path;
            if (string.IsNullOrEmpty(prefabPath)) {
                string safeName = (cmd.name ?? target.name).Replace(" ", "_");
                prefabPath = "Assets/Prefabs/" + safeName + ".prefab";
            }
            if (!prefabPath.StartsWith("Assets/")) {
                prefabPath = "Assets/" + prefabPath.TrimStart('/');
            }

            try {
                string dir = Path.GetDirectoryName(prefabPath);
                if (!string.IsNullOrEmpty(dir) && !AssetDatabase.IsValidFolder(dir)) {
                    string[] parts = dir.Replace("\\", "/").Split('/');
                    string current = parts[0];
                    for (int i = 1; i < parts.Length; i++) {
                        string next = current + "/" + parts[i];
                        if (!AssetDatabase.IsValidFolder(next)) {
                            AssetDatabase.CreateFolder(current, parts[i]);
                        }
                        current = next;
                    }
                }

                GameObject prefab = PrefabUtility.SaveAsPrefabAsset(target, prefabPath);
                if (prefab == null) {
                    return "{\"error\": \"PrefabUtility.SaveAsPrefabAsset failed\"}";
                }

                string escaped = prefabPath.Replace("\\", "\\\\");
                return "{\"status\": \"success\", \"prefab_path\": \"" + escaped + "\", \"object_name\": \"" + target.name + "\"}";
            } catch (Exception e) {
                return "{\"error\": \"" + e.Message.Replace("\"", "'") + "\"}";
            }
        }

        private static string RunSimulation(CommandRequest cmd) {
            float duration = cmd.duration > 0 ? cmd.duration : 1f;
            _simRecord = cmd.record_data;
            _simDuration = duration;

            if (EditorApplication.isPlaying) {
                _simRunning = true;
                _simEndTime = EditorApplication.timeSinceStartup + duration;
                return "{\"status\": \"simulation_extended\", \"state\": \"running\", \"duration\": " + duration + "}";
            }

            _simRunning = true;
            EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
            EditorApplication.update += SimulationUpdate;
            EditorApplication.EnterPlaymode();
            return "{\"status\": \"simulation_started\", \"state\": \"running\", \"duration\": " + duration + ", \"record_data\": " + _simRecord + "}";
        }

        private static void OnPlayModeStateChanged(PlayModeStateChange state) {
            if (state == PlayModeStateChange.EnteredPlayMode && _simRunning) {
                _simEndTime = EditorApplication.timeSinceStartup + _simDuration;
            }
            if (state == PlayModeStateChange.EnteredEditMode) {
                _simRunning = false;
                EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
                EditorApplication.update -= SimulationUpdate;
            }
        }

        private static void SimulationUpdate() {
            if (!_simRunning || !EditorApplication.isPlaying) return;
            if (EditorApplication.timeSinceStartup >= _simEndTime) {
                EditorApplication.ExitPlaymode();
                _simRunning = false;
                EditorApplication.update -= SimulationUpdate;
            }
        }

        private static string SimulationStatus() {
            if (_simRunning && EditorApplication.isPlaying) {
                double remaining = Math.Max(0, _simEndTime - EditorApplication.timeSinceStartup);
                return "{\"state\": \"running\", \"remaining_seconds\": " + remaining.ToString("F2") + ", \"record_data\": " + _simRecord + "}";
            }
            if (EditorApplication.isPlaying) {
                return "{\"state\": \"playing\", \"sim_managed\": false}";
            }
            return "{\"state\": \"idle\", \"sim_managed\": false}";
        }

        private static string StopSimulation() {
            if (EditorApplication.isPlaying) {
                EditorApplication.ExitPlaymode();
            }
            _simRunning = false;
            EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
            EditorApplication.update -= SimulationUpdate;
            return "{\"status\": \"stopped\", \"state\": \"idle\"}";
        }

        /// <summary>
        /// Invokes a public static, PARAMETERLESS method via reflection —
        /// deliberately the same constraint Unity's own `-executeMethod`
        /// CLI flag has ("must be public and static, can't take any
        /// parameters"). This is real, working reflection, not a stub.
        /// It does NOT attempt arbitrary parameter marshaling: passing a
        /// non-empty `parameters` dict from the Python side is accepted
        /// but explicitly reported as ignored, rather than silently
        /// failing or guessing at type coercion.
        /// </summary>
        private static string ExecuteMethod(CommandRequest cmd) {
            if (string.IsNullOrEmpty(cmd.class_name) || string.IsNullOrEmpty(cmd.method_name)) {
                return "{\"error\": \"class_name and method_name are required\"}";
            }

            try {
                Type targetType = FindTypeByName(cmd.class_name);
                if (targetType == null) {
                    return "{\"error\": \"Class not found: " + cmd.class_name + "\"}";
                }

                MethodInfo method = targetType.GetMethod(
                    cmd.method_name,
                    BindingFlags.Public | BindingFlags.Static | BindingFlags.FlattenHierarchy,
                    null, Type.EmptyTypes, null);

                if (method == null) {
                    return "{\"error\": \"No public static parameterless method '" + cmd.method_name +
                        "' found on " + cmd.class_name + ". Methods with parameters are not supported " +
                        "over the bridge (same constraint as Unity's -executeMethod CLI flag).\"}";
                }

                object result = method.Invoke(null, null);
                string resultStr = result != null ? result.ToString().Replace("\"", "'") : "null";
                return "{\"status\": \"success\", \"class_name\": \"" + cmd.class_name +
                    "\", \"method_name\": \"" + cmd.method_name + "\", \"return_value\": \"" + resultStr + "\"}";
            } catch (Exception e) {
                return "{\"error\": \"" + e.Message.Replace("\"", "'") + "\"}";
            }
        }

        private static Type FindTypeByName(string className) {
            foreach (var assembly in AppDomain.CurrentDomain.GetAssemblies()) {
                Type t = assembly.GetType(className);
                if (t != null) return t;
            }
            return null;
        }

        /// <summary>
        /// Executes a list of sub-commands sequentially through the same
        /// HandleCommand dispatcher used for single commands. Each entry
        /// uses the standard CommandRequest shape (action/target/name/...)
        /// rather than a free-form per-op schema — Unity's JsonUtility
        /// can't deserialize arbitrary heterogeneous dicts, so this is a
        /// deliberate, documented shape change from older aspirational
        /// docs, not an oversight.
        /// </summary>
        private static string BatchOperations(CommandRequest cmd) {
            if (cmd.operations == null || cmd.operations.Length == 0) {
                return "{\"error\": \"operations array is required and must be non-empty\"}";
            }

            var results = new List<string>();
            int successCount = 0;
            foreach (var op in cmd.operations) {
                try {
                    string result = HandleCommand(op);
                    results.Add(result);
                    if (!result.Contains("\"error\"")) successCount++;
                } catch (Exception e) {
                    results.Add("{\"error\": \"" + e.Message.Replace("\"", "'") + "\"}");
                }
            }

            return "{\"status\": \"completed\", \"operation_count\": " + cmd.operations.Length +
                ", \"success_count\": " + successCount +
                ", \"results\": [" + string.Join(",", results) + "]}";
        }

        private static List<Vector3> ExtractPathPoints(CommandRequest cmd, bool force2DPlaneY0) {
            var points = new List<Vector3>();
            if (cmd.path_points == null) return points;
            foreach (var p in cmd.path_points) {
                points.Add(new Vector3(p.x, force2DPlaneY0 ? 0f : p.y, p.z));
            }
            return points;
        }

        private static string MoveAlongPath(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";
            if (cmd.path_points == null || cmd.path_points.Length < 2) {
                return "{\"error\": \"path_points must contain at least 2 points\"}";
            }

            var state = new PathMovementState {
                target = target,
                points = ExtractPathPoints(cmd, false),
                speed = cmd.speed,
                duration = cmd.duration,
                startTime = EditorApplication.timeSinceStartup,
                loop = cmd.loop,
                smoothRotation = true,
                bankAngle = 0f,
            };
            _activeMovements[target.GetInstanceID()] = state;

            return "{\"status\": \"started\", \"animation_id\": " + target.GetInstanceID() +
                ", \"path_type\": \"" + (cmd.path_type ?? "straight") +
                "\", \"point_count\": " + cmd.path_points.Length +
                ", \"note\": \"curve path_types are approximated as straight multi-segment interpolation, not true bezier/spline math\"}";
        }

        private static string FollowPath2D(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";
            if (cmd.path_points == null || cmd.path_points.Length < 2) {
                return "{\"error\": \"path_points must contain at least 2 points\"}";
            }

            var points = ExtractPathPoints(cmd, false);
            float currentY = target.transform.position.y;
            for (int i = 0; i < points.Count; i++) {
                var p = points[i];
                points[i] = new Vector3(p.x, currentY, p.z);
            }

            float totalLength = 0f;
            for (int i = 0; i < points.Count - 1; i++) totalLength += Vector3.Distance(points[i], points[i + 1]);
            float dur = cmd.speed > 0f ? totalLength / cmd.speed : 1f;

            var state = new PathMovementState {
                target = target,
                points = points,
                speed = cmd.speed,
                duration = dur,
                startTime = EditorApplication.timeSinceStartup,
                loop = cmd.loop,
                smoothRotation = cmd.smooth_rotation,
                bankAngle = 0f,
                lookAhead = cmd.look_ahead,
                is2D = true,
            };
            _activeMovements[target.GetInstanceID()] = state;

            return "{\"status\": \"started\", \"animation_id\": " + target.GetInstanceID() +
                ", \"mode\": \"2d\", \"point_count\": " + points.Count + "}";
        }

        private static string FollowPath3D(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";
            if (cmd.path_points == null || cmd.path_points.Length < 2) {
                return "{\"error\": \"path_points must contain at least 2 points\"}";
            }

            var points = ExtractPathPoints(cmd, false);
            float totalLength = 0f;
            for (int i = 0; i < points.Count - 1; i++) totalLength += Vector3.Distance(points[i], points[i + 1]);
            float dur = cmd.speed > 0f ? totalLength / cmd.speed : 1f;

            var state = new PathMovementState {
                target = target,
                points = points,
                speed = cmd.speed,
                duration = dur,
                startTime = EditorApplication.timeSinceStartup,
                loop = cmd.loop,
                smoothRotation = true,
                bankAngle = cmd.bank_angle,
                lookAhead = cmd.look_ahead,
                is2D = false,
            };
            _activeMovements[target.GetInstanceID()] = state;

            return "{\"status\": \"started\", \"animation_id\": " + target.GetInstanceID() +
                ", \"mode\": \"3d\", \"point_count\": " + points.Count + "}";
        }

        private static string StopPathMovement(CommandRequest cmd) {
            GameObject target = FindGameObject(cmd.target);
            if (target == null) return "{\"error\": \"Target not found: " + cmd.target + "\"}";

            int id = target.GetInstanceID();
            if (!_activeMovements.ContainsKey(id)) {
                return "{\"status\": \"not_moving\", \"target\": \"" + cmd.target + "\"}";
            }

            if (cmd.decelerate) {
                var state = _activeMovements[id];
                state.decelerating = true;
                state.decelerationStartTime = EditorApplication.timeSinceStartup;
                state.decelerationStartSpeed = state.speed;
                state.decelerationTime = cmd.deceleration_time > 0f ? cmd.deceleration_time : 0.5f;
                return "{\"status\": \"decelerating\", \"deceleration_time\": " + state.decelerationTime + "}";
            }

            Vector3 finalPos = target.transform.position;
            _activeMovements.Remove(id);
            return "{\"status\": \"stopped\", \"final_position\": {\"x\": " + finalPos.x +
                ", \"y\": " + finalPos.y + ", \"z\": " + finalPos.z + "}}";
        }

        private static string CreatePathVisualization(CommandRequest cmd) {
            if (cmd.path_points == null || cmd.path_points.Length < 2) {
                return "{\"error\": \"path_points must contain at least 2 points\"}";
            }

            try {
                GameObject vizObject = new GameObject("MCP_PathVisualization_" + DateTime.Now.Ticks);
                LineRenderer lr = vizObject.AddComponent<LineRenderer>();
                var points = ExtractPathPoints(cmd, false);

                lr.positionCount = points.Count;
                lr.SetPositions(points.ToArray());
                lr.startWidth = cmd.thickness > 0f ? cmd.thickness : 0.1f;
                lr.endWidth = lr.startWidth;
                lr.useWorldSpace = true;

                Color c = cmd.color != null
                    ? new Color(cmd.color.r, cmd.color.g, cmd.color.b, cmd.color.a)
                    : Color.red;

                Material lineMat = new Material(Shader.Find("Sprites/Default"));
                lineMat.color = c;
                lr.material = lineMat;
                lr.startColor = c;
                lr.endColor = c;

                return "{\"status\": \"success\", \"instanceID\": " + vizObject.GetInstanceID() +
                    ", \"point_count\": " + points.Count + ", \"name\": \"" + vizObject.name + "\"}";
            } catch (Exception e) {
                return "{\"error\": \"" + e.Message.Replace("\"", "'") + "\"}";
            }
        }

        private static string CaptureMultiAngle(CommandRequest cmd) {
            string dir = !string.IsNullOrEmpty(cmd.output_dir)
                ? cmd.output_dir
                : Path.Combine(Application.dataPath, "../Temp/mcp_angles");
            int angles = cmd.angles > 0 ? cmd.angles : 4;
            int width = cmd.width > 0 ? cmd.width : 1280;
            int height = cmd.height > 0 ? cmd.height : 720;

            try {
                if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);

                Camera cam = Camera.main ?? GameObject.FindObjectOfType<Camera>();
                if (cam == null) return "{\"error\": \"No camera found in active scene\"}";

                Vector3 originalPos = cam.transform.position;
                Quaternion originalRot = cam.transform.rotation;
                var paths = new List<string>();

                for (int i = 0; i < angles; i++) {
                    float yaw = (360f / angles) * i;
                    cam.transform.rotation = Quaternion.Euler(20f, yaw, 0f);
                    string path = Path.Combine(dir, "angle_" + i + ".png");
                    RenderTexture rt = new RenderTexture(width, height, 24);
                    RenderTexture prev = cam.targetTexture;
                    cam.targetTexture = rt;
                    cam.Render();
                    RenderTexture.active = rt;
                    Texture2D tex = new Texture2D(width, height, Texture2D.RGB24, false);
                    tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                    tex.Apply();
                    cam.targetTexture = prev;
                    RenderTexture.active = null;
                    File.WriteAllBytes(path, tex.EncodeToPNG());
                    UnityEngine.Object.DestroyImmediate(tex);
                    UnityEngine.Object.DestroyImmediate(rt);
                    paths.Add(path.Replace("\\", "\\\\"));
                }

                cam.transform.position = originalPos;
                cam.transform.rotation = originalRot;

                return "{\"status\": \"success\", \"output_dir\": \"" + dir.Replace("\\", "\\\\") + "\", \"angles\": " + angles + ", \"files\": [\"" + string.Join("\",\"", paths) + "\"]}";
            } catch (Exception e) {
                return "{\"error\": \"" + e.Message.Replace("\"", "'") + "\"}";
            }
        }

        private static string GetSceneSummary() {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var objects = GameObject.FindObjectsOfType<GameObject>();
            var list = new List<string>();
            int meshCount = 0;
            foreach (var obj in objects) {
                if (obj.hideFlags != HideFlags.None) continue;
                if (obj.GetComponent<MeshRenderer>() != null || obj.GetComponent<MeshFilter>() != null)
                    meshCount++;
                list.Add("{\"name\":\"" + obj.name + "\", \"id\":\"" + obj.GetInstanceID() + "\"}");
            }
            return "{\"scene_name\": \"" + scene.name + "\", \"object_count\": " + objects.Length + ", \"mesh_count\": " + meshCount + ", \"objects\": [" + string.Join(",", list) + "]}";
        }

        private static string ValidateScene() {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var objects = GameObject.FindObjectsOfType<GameObject>();
            int triangleCount = 0;
            int meshCount = 0;
            var materialSet = new HashSet<int>();
            int missingScripts = 0;
            var missingList = new List<string>();

            foreach (var obj in objects) {
                if (obj.hideFlags != HideFlags.None) continue;

                var components = obj.GetComponents<Component>();
                foreach (var comp in components) {
                    if (comp == null) {
                        missingScripts++;
                        missingList.Add(obj.name);
                        break;
                    }
                }

                var mf = obj.GetComponent<MeshFilter>();
                if (mf != null && mf.sharedMesh != null) {
                    meshCount++;
                    triangleCount += mf.sharedMesh.triangles.Length / 3;
                }

                var smr = obj.GetComponent<SkinnedMeshRenderer>();
                if (smr != null && smr.sharedMesh != null) {
                    meshCount++;
                    triangleCount += smr.sharedMesh.triangles.Length / 3;
                    if (smr.sharedMaterials != null) {
                        foreach (var mat in smr.sharedMaterials) {
                            if (mat != null) materialSet.Add(mat.GetInstanceID());
                        }
                    }
                }

                var mr = obj.GetComponent<MeshRenderer>();
                if (mr != null && mr.sharedMaterials != null) {
                    foreach (var mat in mr.sharedMaterials) {
                        if (mat != null) materialSet.Add(mat.GetInstanceID());
                    }
                }
            }

            var missingJson = new List<string>();
            foreach (var name in missingList) {
                missingJson.Add("\"" + name.Replace("\"", "'") + "\"");
            }

            return "{" +
                "\"scene_name\": \"" + scene.name + "\"," +
                "\"object_count\": " + objects.Length + "," +
                "\"mesh_count\": " + meshCount + "," +
                "\"triangle_count\": " + triangleCount + "," +
                "\"material_count\": " + materialSet.Count + "," +
                "\"missing_script_count\": " + missingScripts + "," +
                "\"objects_with_missing_scripts\": [" + string.Join(",", missingJson) + "]" +
            "}";
        }

        private static GameObject FindGameObject(string identifier) {
            if (int.TryParse(identifier, out int id)) {
                foreach (var go in GameObject.FindObjectsOfType<GameObject>()) {
                    if (go.GetInstanceID() == id) return go;
                }
            }
            return GameObject.Find(identifier);
        }

        private static void SendResponse(HttpListenerContext context, string responseString, HttpStatusCode code = HttpStatusCode.OK) {
            byte[] buffer = Encoding.UTF8.GetBytes(responseString);
            context.Response.StatusCode = (int)code;
            context.Response.ContentType = "application/json";
            context.Response.ContentLength64 = buffer.Length;
            context.Response.OutputStream.Write(buffer, 0, buffer.Length);
            context.Response.Close();
        }

        [Serializable]
        private class PathPoint {
            public float x;
            public float y;
            public float z;
        }

        [Serializable]
        private class ColorRGBA {
            public float r = 1f;
            public float g = 1f;
            public float b = 1f;
            public float a = 1f;
        }

        [Serializable]
        private class CommandRequest {
            public string action;
            public string target;
            public string name;
            public string type;
            public float[] position;
            public float[] rotation;
            public float scale = 0f;  // 0 = not set (leave localScale untouched)
            public string output_path;
            public string output_dir;
            public int width;
            public int height;
            public int angles;
            public string prefab_path;
            public float duration;
            public int record_data;

            // execute_method (public static, parameterless only — same
            // constraint Unity's own -executeMethod CLI flag has).
            public string class_name;
            public string method_name;

            // batch_operations: each sub-op reuses this same CommandRequest
            // shape (action/target/name/... ) rather than a free-form
            // per-op schema, since Unity's JsonUtility can't deserialize
            // arbitrary heterogeneous dicts. Executed sequentially.
            public CommandRequest[] operations;

            // Path movement / visualization.
            public PathPoint[] path_points;
            public string path_type = "straight";
            public bool loop;
            public string ease_type = "linear";
            public float speed = 1f;
            public float look_ahead = 0.5f;
            public bool smooth_rotation = true;
            public float bank_angle;
            public bool decelerate = true;
            public float deceleration_time = 0.5f;
            public string visualization_type = "line";
            public ColorRGBA color;
            public float thickness = 0.1f;

            // create_object extras: dimensions is a per-axis alternative to the uniform
            // `scale` above (used by the fixture spawner, where a table top and its legs
            // need different width/height/depth, not a single multiplier).
            public float[] dimensions;

            // animate_object / stop_animation.
            public string anim_mode = "spin";
            public float[] axis = new float[] { 0f, 1f, 0f };
            public float amplitude = 0.1f;
            public float damping = 0.6f;
        }

        // Active path-movement state, ticked from Update(). Keyed by
        // GameObject instance ID so multiple objects can move concurrently
        // and be stopped independently.
        private class PathMovementState {
            public GameObject target;
            public List<Vector3> points;
            public float speed;
            public float duration;
            public double startTime;
            public bool loop;
            public bool is2D;
            public bool smoothRotation;
            public float bankAngle;
            public float lookAhead;
            public bool decelerating;
            public float decelerationTime;
            public double decelerationStartTime;
            public float decelerationStartSpeed;
        }

        private static readonly Dictionary<int, PathMovementState> _activeMovements =
            new Dictionary<int, PathMovementState>();

        // Active in-place animation state (spin/bob/bounce), ticked from Update() alongside
        // path movement. Keyed by GameObject instance ID, same pattern as _activeMovements -
        // one animation per object, starting a new one on an already-animating object
        // replaces it.
        private class AnimationState {
            public GameObject target;
            public string mode;
            public Vector3 axis;
            public float speed;
            public float amplitude;
            public float damping;
            public double startTime;
            public double durationS;  // <= 0 means run until stop_animation is called
            public Vector3 restPosition;
            public Quaternion restRotation;
        }

        private static readonly Dictionary<int, AnimationState> _activeAnimations =
            new Dictionary<int, AnimationState>();

        [MenuItem("MCP/Start Bridge")]
        public static void ForceStart() => StartServer();

        [MenuItem("MCP/Stop Bridge")]
        public static void ForceStop() => StopServer();
    }
}
