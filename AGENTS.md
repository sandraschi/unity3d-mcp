# AGENTS.md — unity3d-mcp

## Identity
- **Name**: unity3d-mcp (PyPI: `schip-mcp-unity3d`)
- **Purpose**: FastMCP 3.2 server for Unity 3D automation, VRM avatars, VRChat, World Labs
- **Stack**: FastMCP 3.2+, Python 3.12+, Rust extension, UnityPy
- **Ports**: 10830 (Vite dashboard), 10831 (MCP HTTP)
- **Mesh role**: 3D rendering/visualization for the robotics fleet (receives Gazebo models)

## Key Files

| File | Purpose |
|------|---------|
| `src/unity3d_mcp/server.py` | MCP tool registrations (50+ tools) |
| `src/unity3d_mcp/core/` | Unity Editor + Project + Scene management |
| `src/unity3d_mcp/avatar/` | VRM avatar import, rigging, optimization |
| `src/unity3d_mcp/vrchat/` | VRChat SDK + auth + upload |
| `src/unity3d_mcp/worldlabs/` | World Labs Marble/Chisel integration |
| `src/unity3d_mcp/tools/` | Import/export, motors, disk ops, API bridge |

## Tools (selected)

| Category | Tools |
|----------|-------|
| Core | `launch_unity_editor`, `create_unity_project`, `build_unity_project` |
| Avatars | `import_vrm_avatar`, `optimize_for_vrchat`, `setup_avatar_animator` |
| VRChat | `upload_vrchat_avatar`, `send_avatar_parameter`, `send_chatbox_message` |
| World Labs | `import_marble_world`, `install_gaussian_splatting` |
| Motors | `api_add_motor`, `api_start_motor`, `api_stop_motor` |
| Imports | `import_3d_model`, `import_texture`, `import_asset_package` |
| Disk | `unity3d_disk_api` — direct Unity file manipulation via UnityPy |

## Fleet mesh

Unity3D-MCP is a member of the robotics/VR mesh:
- **gazebo-mcp** → syncs Gazebo models → Unity for high-fidelity rendering
- **freecad-mcp** → imports CAD models
- **avatar-mcp** → VRM avatar compositing
- **resonite-mcp** → VR spatial sync
- **worldlabs-mcp** → AI-generated 3D worlds

## Testing

```powershell
.\scripts\run-tests.ps1
uv run pytest
```
