using UnityEngine;
using UnityEditor;
using System;
using System.IO;
using System.Net;
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

            return "{\"status\": \"success\"}";
        }

        private static string CreateObject(CommandRequest cmd) {
            GameObject go = new GameObject(cmd.name ?? "New Object");
            if (cmd.type == "Light") go.AddComponent<Light>();
            else if (cmd.type == "Camera") go.AddComponent<Camera>();
            
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
        private class CommandRequest {
            public string action;
            public string target;
            public string name;
            public string type;
            public float[] position;
            public float[] rotation;
            public string output_path;
            public string output_dir;
            public int width;
            public int height;
            public int angles;
            public string prefab_path;
            public float duration;
            public int record_data;
        }

        [MenuItem("MCP/Start Bridge")]
        public static void ForceStart() => StartServer();

        [MenuItem("MCP/Stop Bridge")]
        public static void ForceStop() => StopServer();
    }
}
