---
name: unity-editor-automation
description: Expert instructions for automated Unity Editor control. Includes project lifecycle management, scene manipulation, and CLI-based tool interaction.
---

# Unity Editor Automation (SOTA 2026)

This skill provides the foundational logic for orchestrating Unity Editor operations through the `unity3d-mcp` server.

## 🚀 Core Principles

1.  **Project First**: Always ensure a project exists or is correctly initialized before running editor commands.
2.  **CLI Precision**: Use `unity_core(operation="execute_method")` to perform operations that don't require a visible editor.
3.  **Scene Hygiene**: Save current work frequently and validate scene paths before manipulation.

## 🔑 Dual-Mode Architecture (Hands-In vs Hands-Off)

### 1. Hands-In (Active Session)
**Scenario**: Unity Editor is open, and you want to see changes happening live.
- **Tool**: `unity_bridge` (operations: status, execution_mode, ping, get_hierarchy, create_object, delete_object, transform_object, capture_game_view)
- **Requirement**: `MCPBridge.cs` must be installed in your project.
- **Capabilities**: Real-time hierarchy inspection, object movement, lighting adjustment, and scene manipulation.

### 2. Hands-Off (Disk Operations)
**Scenario**: Unity is closed, or you are running in a CI/CD environment.
- **Tool**: `unity3d_disk_api`
- **Requirement**: `UnityPy` Python library (integrated).
- **Capabilities**: Asset extraction from serialized files, prefab data inspection, and regex-based YAML property modification.

---

## 🛠️ Installation: The Unity Bridge

To enable **Hands-In** live control, you must install the MCP bridge in your Unity project.

### Step-by-Step Installation
1.  **Locate the Bridge**: Find the `MCPBridge.cs` script in the `src/unity3d_mcp/resources/` directory of this server.
2.  **Import to Unity**: Copy `MCPBridge.cs` into your Unity project's `Assets/Editor` folder (create the folder if it doesn't exist).
3.  **Automatic Startup**: Once imported, Unity will automatically compile and start the bridge on **http://localhost:10835**.
4.  **Verification**: Look for the `[MCP] Bridge active` message in the Unity Console. You can also use `unity_bridge(operation="status")` to check connection status.


## 🛠️ Common Workflows

### Project Initialization
To create a SOTA-compliant Unity project:
1.  Call `unity_core(operation="create_project", project_name=..., project_path=..., template=..., unity_version=...)`.
2.  There is **no** `switch_platform` tool — no MCP tool changes the active
    build target directly. `unity_build(operation="build_project",
    build_target=...)` builds for a target platform but does not switch the
    open Editor's active target. If you need the Editor itself switched,
    that's a manual step for now.
3.  Import UniVRM with `unity_core(operation="install_univrm",
    project_path=..., vrm_version=...)` (real, works). There is **no**
    `install_asset_package` tool — generic asset-package installation
    (e.g. VRChat SDK via .unitypackage) is not exposed as an MCP tool;
    real but unregistered code exists in `import_export_manager.py`. Do
    this step manually in the Unity Editor for now.

### Method Execution
For advanced automation, use `unity_core(operation="execute_method")`:
- **`class_name`**: The full namespace + class name in your Unity project.
- **`method_name`**: A `[MenuItem]` or `static` method accessible to the editor.
- **`parameters`**: Dict of arguments passed to the method entry point.
- **`project_path`**: Unity project path.

---
**Status:** ✅ SOTA v12.0 Compliant
**Author:** Unity3D-MCP Intelligence
