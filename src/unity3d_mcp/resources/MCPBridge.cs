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
            public int width;
            public int height;
        }

        [MenuItem("MCP/Start Bridge")]
        public static void ForceStart() => StartServer();

        [MenuItem("MCP/Stop Bridge")]
        public static void ForceStop() => StopServer();
    }
}
