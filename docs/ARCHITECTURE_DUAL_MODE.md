# 🏗️ Architecture: Dual-Mode Unity Operations

The Unity3D-MCP server is built on a SOTA **Dual-Mode** architecture designed to bridge the gap between real-time editor manipulation and static asset processing.

---

## 🔑 Mode A: Hands-In (Live Session Control)

**Objective**: Real-time interaction with an active Unity Editor instance.

### 🧩 How it Works
1.  **The Bridge**: A C# script (`MCPBridge.cs`) is placed in the Unity `Editor` folder.
2.  **The Listener**: Upon startup, the bridge initializes an asynchronous `HttpListener` on **port 10835**.
3.  **Command Marshalling**: Incoming JSON commands are queued and executed on the **Unity Main Thread** via `EditorApplication.update`.
4.  **The Pipeline**:
    *   `MCP Server (Python)` → `POST http://localhost:10835` → `Unity Bridge (C#)` → `Reflection/API Call` → `JSON Response`.

### 🛠️ Key Tools
- **`unity3d_bridge_status`**: Heartbeat check for the live bridge.
- **`unity3d_editor_api`**: The primary router for live commands (transform, hierarchy, creation).

---

## 🔑 Mode B: Hands-Off (Disk Operations)

**Objective**: Auditing and modifying project assets without launching Unity.

### 🧩 How it Works
1.  **UnityPy Integration**: The server uses the `UnityPy` Python library to load serialized Unity files (`.unity`, `.prefab`, `.asset`).
2.  **Asset Extraction**: Can extract textures, meshes, and metadata directly from the binary/serialized formats.
3.  **YAML Manipulation**: For "Source" assets (YAML-formatted scenes/prefabs), the server uses high-precision regex modifications to update properties (e.g., changing a light intensity or a script reference) safely.

### 🛠️ Key Tools
- **`unity3d_disk_api`**: Direct project inspection and "off-thread" manipulation.

---

## 📊 Comparison Matrix

| Feature | Hands-In (Live) | Hands_Off (Disk) |
|---------|-----------------|------------------|
| **Speed** | Near-instant | Fast (Batch) |
| **Unity Required** | ✅ Running | ❌ Closed |
| **Visible Changes** | ✅ Real-time | ❌ Next Load |
| **Complexity** | High (Interaction) | Medium (Parsing) |
| **Best For** | Level Design / UI | CI/CD / Auditing |
| **Safety** | High (Undo Support) | High (Text-based) |

---

## 🚀 Environment Optimization

To ensure maximum performance in Dual-Mode:
1.  **Port Allocation**: Ensure port `10835` is not occupied by other services.
2.  **Async/Await**: The MCP server uses non-blocking calls for all bridge interactions.
3.  **Main Thread Safety**: Always use the bridge for operations involving the `UnityEngine` namespace when in Hands-In mode.
