## Session Context (Unity3D MCP)

You have access to a Unity 3D automation server with 50+ tools: editor control, project/scene management, VRM avatar import and optimization, VRChat upload, World Labs integration, 3D model import, and motor control.

**Before starting work:**
1. Check server health: unity3d_status()
2. List active scenes: list_scenes()
3. Check Unity Editor connection: check_unity_bridge()

**At end of work, save findings:**
- Save open scenes: save_current_scene()
- Build any modified projects: build_unity_project()
