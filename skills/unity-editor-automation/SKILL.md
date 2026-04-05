---
name: unity-editor-automation
description: Expert instructions for automated Unity Editor control. Includes project lifecycle management, scene manipulation, and CLI-based tool interaction.
---

# Unity Editor Automation (SOTA 2026)

This skill provides the foundational logic for orchestrating Unity Editor operations through the `unity3d-mcp` server.

## 🚀 Core Principles

1.  **Project First**: Always ensure a project exists or is correctly initialized before running editor commands.
2.  **CLI Precision**: Use the specific CLI wrappers (e.g., `execute_unity_method`) to perform operations that don't required a visible editor.
3.  **Scene Hygiene**: Save current work frequently and validate scene paths before manipulation.

## 🔑 Dual-Mode Architecture (Hands-In vs Hands-Off)

### 1. Hands-In (Active Session)
**Scenario**: Unity Editor is open, and you want to see changes happening live.
- **Tool**: `unity3d_editor_api`
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
4.  **Verification**: Look for the `[MCP] Bridge active` message in the Unity Console. You can also use the `unity3d_bridge_status` tool to check connection status.


## 🛠️ Common Workflows

### Project Initialization
To create a SOTA-compliant Unity project:
1.  Call `create_unity_project` with a descriptive path.
2.  Set the target platform early using `switch_platform`.
3.  Import baseline packages (UniVRM, VRChat SDK) using `install_univrm` and `install_asset_package`.

### Method Execution
For advanced automation, use `execute_unity_method`:
- **Class**: The full namespace + class name in your Unity project.
- **Method**: A `[MenuItem]` or `static` method accessible to the editor.
- **Args**: Pass JSON-formatted arguments to the method entry point.

---
**Status:** ✅ SOTA v12.0 Compliant
**Author:** Unity3D-MCP Intelligence
