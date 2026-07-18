# Game Development - Unity3D-MCP

**Corrected 2026-07-18** against `src/unity3d_mcp/server.py` and
`tools/portmanteau/*.py`. The previous version of this file used flat
function names (`create_unity_project`, `create_gameobject`,
`add_component`, `instantiate_prefab`, `build_project`,
`build_all_platforms`) that are not, and in some cases never were,
registered MCP tools. Below: what's real, and what's honestly not.

## Unity Game Development Workflow

### Project Creation
```python
unity_core(
    operation="create_project",
    project_name="MyGame",
    project_path="D:/Projects/MyGame",
    template="3D",  # whatever templates ProjectManager.create_project supports
    unity_version="2022.3.0f1"
)
```
This is real (CLI-backed via `ProjectManager.create_project`), not a
bridge/mock operation.

### Scene Creation
No dedicated scene-authoring tool exists (no "create scene with these
GameObjects" helper). `unity_scene(operation="create_light")` is the only
scene-composition operation currently registered. Structuring scenes
(MainMenu, Level1, GameOver, etc.) is a manual Unity Editor task today.

### GameObject Management
```python
# Create a GameObject (Hands-In only, requires MCPBridge.cs connected)
unity_bridge(operation="create_object", name="Player", object_type="GameObject")

# Move/transform it
unity_bridge(operation="transform_object", target="Player", position=[0, 0, 0])
```
**No `add_component` or `instantiate_prefab` equivalent exists.** Adding
arbitrary components to a GameObject, or instantiating a prefab by path,
is not exposed as an MCP tool anywhere in this server — not even as a
non-bridge stub. If you need this, it's new work, not a naming fix.

### Scripting
```csharp
// C# script structure
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    void Start() { }  // Initialization
    void Update() { }  // Per frame
    void FixedUpdate() { }  // Physics updates
}
```
Writing/injecting C# scripts into a Unity project is not something this
server automates; scripts are authored normally and the server operates
on the resulting project/scene.

### Build Process
```python
# Build for Windows
unity_build(
    operation="build_project",
    project_path="D:/Projects/MyGame",
    build_target="StandaloneWindows64",
    output_path="Builds/Windows/MyGame.exe",
    development_build=False
)
```
Real, CLI-backed via `BuildManager.build_project`.

**No `build_all_platforms` / multi-platform batch build tool exists.**
Call `unity_build(operation="build_project", ...)` once per target, or
submit each as a separate async job via `unity_jobs(operation="submit",
job_type="build", ...)`.

---

**Austrian Game Dev**: Solid architecture, optimized performance, polished gameplay! 🇦🇹🎮
