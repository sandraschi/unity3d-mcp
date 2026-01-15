using UnityEngine;
using UnityEditor;
using System;
using System.IO;
using System.Collections.Generic;

namespace MCP {
    [Serializable]
    public class LightData {
        public string name;
        public string type;
        public float[] color;
        public float intensity;
        public float[] position;
        public float[] rotation;
    }

    public class MCPBridge {
        public static void CreateLight() {
            try {
                // Read parameters from project root
                string paramsPath = Path.Combine(Directory.GetCurrentDirectory(), "mcp_params.json");
                if (!File.Exists(paramsPath)) {
                    Debug.LogError("[MCP] Param file not found: " + paramsPath);
                    return;
                }
                
                string json = File.ReadAllText(paramsPath);
                LightData data = JsonUtility.FromJson<LightData>(json);

                GameObject go = new GameObject(data.name);
                Light light = go.AddComponent<Light>();

                if (Enum.TryParse<LightType>(data.type, out LightType lType)) {
                    light.type = lType;
                } else {
                    light.type = LightType.Spot; // Default
                }

                if (data.color != null && data.color.Length >= 3) {
                    light.color = new Color(data.color[0], data.color[1], data.color[2], data.color.Length > 3 ? data.color[3] : 1f);
                }

                light.intensity = data.intensity;

                if (data.position != null && data.position.Length >= 3) {
                    go.transform.position = new Vector3(data.position[0], data.position[1], data.position[2]);
                }
                
                if (data.rotation != null && data.rotation.Length >= 3) {
                    go.transform.rotation = Quaternion.Euler(data.rotation[0], data.rotation[1], data.rotation[2]);
                }
                
                Debug.Log($"[MCP] Created light: {data.name}");

            } catch (Exception e) {
                Debug.LogError("[MCP] Error creating light: " + e.Message);
            }
        }
    }
}
