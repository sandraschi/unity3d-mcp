# 📘 API Reference: Unity3D-MCP Toolset

The Unity3D-MCP server provides a comprehensive toolset for project lifecycle management, real-time Editor control, avatar optimization, and build automation.

---

## 🏗️ Core: Project & Scene Management

### `create_unity_project`
**Objective**: Create a new Unity project from scratch.
- **`project_path`**: Absolute path to create the project.
- **`unity_version`**: (Optional) Version to use (e.g., '2022.3.15f1').

### `launch_unity_editor`
**Objective**: Open a project in the Unity Editor.
- **`project_path`**: Absolute path to the existing project.
- **`batch_mode`**: (Bool) Run without a visible UI.

### `execute_unity_method`
**Objective**: Trigger a specific C# method within Unity.
- **`class_name`**: Full namespace and class (e.g., 'MyNamespace.MyClass').
- **`method_name`**: Static or MenuItem method to call.

---

## 🕹️ Dual-Mode: Hands-In (Live) / Hands-Off (Disk)

### `unity3d_bridge_status`
**Objective**: Check the connection to an active Unity bridge (`MCPBridge.cs`).
- **Return**: `{status: "connected/disconnected", port: 10835}`.

### `unity3d_editor_api`
**Objective**: [Hands-In] Real-time session control.
- **`action`**: `ping`, `get_hierarchy`, `transform_object`, `create_object`, `delete_object`.
- **`target`**: Name or InstanceID for transformation/deletion.
- **`position / rotation`**: Float arrays `[x, y, z]` for object placement.

### `unity3d_disk_api`
**Objective**: [Hands-Off] Direct project file manipulation.
- **`operation`**: `inspect_file`, `list_textures`, `modify_yaml`.
- **`file_path`**: Path to `.unity`, `.prefab`, or `.asset`.
- **`new_value`**: Used for `modify_yaml` to update properties (e.g., light intensity).

---

## 🎭 Avatar & VRM Optimization

### `import_vrm_avatar`
**Objective**: Import a `.vrm` file into the active Unity project.
- **`vrm_path`**: Source `.vrm` location.
- **`target_folder`**: (Optional) Destination in `Assets/`.

### `optimize_for_vrchat`
**Objective**: Automate the VRM-to-VRChat conversion.
- **`avatar_root`**: Path to the imported folder.
- **Actions**: Fixes shaders (Standard to VRChat-compliant), sets up `PipelineManager`, and audits polycount.

### `setup_avatar_rigging`
**Objective**: Automatically map bones to Unity's Humanoid standard.

---

## 🚀 VRChat: SDK Integration

### `vrchat_validate_avatar`
**Objective**: Run the VRChat SDK "Auto-Fix" and validation logic.
- **`avatar_id`**: The Target GameObject.
- **Returns**: Errors/Warnings about performance rank.

### `vrchat_upload_avatar`
**Objective**: Trigger the VRChat SDK build and upload pipeline.

---

## 🌍 World Labs: Marble/Chisel Integration

### `worldlabs_import_marble`
**Objective**: Import AI-generated `.marble` files (3D world snapshots).

### `worldlabs_chisel_edit`
**Objective**: Send/Receive geometry updates to the World Labs Chisel engine for AI-guided mesh modification.

---

## 📦 Build: Multi-Platform pipelines

### `trigger_unity_build`
**Objective**: Trigger a platform-specific build.
- **`platform`**: `StandaloneWindows64`, `Android`, `iOS`, `Quest`.
- **`output_path`**: Destination for the build artifacts.

---

## 📊 Error Handling & Troubleshooting

- **Timeout**: Most bridge operations have a 5.0s timeout.
- **Bridge Installation**: Ensure `MCPBridge.cs` is in the `Assets/Editor` folder.
- **Port Conflict**: Check for port `10835` usage if connection fails.
