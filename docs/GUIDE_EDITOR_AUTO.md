# 🕹️ Guide: Real-Time Unity Editor Automation

Unity3D-MCP's "Hands-In" mode allows you to control an active Unity session with the same precision as a human developer.

---

## 🛠️ Step 1: Bridge Installation

### Installation:
1. Copy `src/unity3d_mcp/resources/MCPBridge.cs` to your Unity project's **`Assets/Editor`** folder.
2. Unity will automatically start the bridge on **http://localhost:10835**.

### Verification:
```python
# Check status
unity3d_bridge_status()
```

- **Returns**: `{"status": "connected", "port": 10835}`.

---

## 🛠️ Step 2: Scene Hierarchy Inspection

### Automation:
```python
# Get Hierarchy
unity3d_editor_api(action="get_hierarchy")
```

- **Objective**: Returns a list of all GameObjects in the active scene with their **InstanceIDs**.

---

## 🛠️ Step 3: Object Transformation & Movement

### Commands:
```python
# Move object
unity3d_editor_api(
    action="transform_object", 
    target="MainCamera", 
    position=[0, 5, -10], 
    rotation=[15, 0, 0]
)
```

- **Logic**: The bridge finds the target by name or InstanceID and applies the `Vector3` position and `Quaternion` rotation on the Unity main thread.

---

## 🛠️ Step 4: Batch Creation & Deletion

### Automation:
```python
# Create batch
unity3d_editor_api(action="create_object", name="LightingProbe", type="Light")

# Delete object
unity3d_editor_api(action="delete_object", target="TemporaryObject")
```

- **Objective**: Allows rapid level design and cleanup of temporary assets.

---

## 💎 Advanced Workflows

### 🏎️ UnityMainThreadDispatcher
The bridge uses the `EditorApplication.update` loop. This means:
- You can safely perform heavy computations in Python and only send the "update" command to Unity.
- Multiple commands are queued and executed sequentially.

### 🧩 Custom Command Extension
The `MCPBridge.cs` script is designed to be extensible. You can add new `case` statements to the `HandleCommand` method to expose project-specific API calls.

### 🚨 Troubleshooting
- **Conflict**: If port `10835` is occupied, change the `PORT` constant in `MCPBridge.cs` and the `port` in the server's `UnityBridgeClient`.
- **Sync**: Ensure the Editor window is active or "Run in Background" is enabled in Unity project settings for the smoothest experience.
