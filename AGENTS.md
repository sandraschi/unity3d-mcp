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

## Tools (portmanteau)

| Tool | Key Operations |
|------|----------------|
| `unity_core` | `launch_editor`, `create_project`, `execute_method`, `check_univrm`, `install_univrm` |
| `unity_scene` | `create_light` |
| `unity_avatar` | `import_vrm`, `setup_animator` |
| `unity_bridge` | `status`, `execution_mode`, `ping`, `get_hierarchy`, `create_object`, `delete_object`, `transform_object`, `capture_game_view` |
| `unity_render` | `capture`, `multi_angle`, `scene_summary` |
| `unity_api` | `get_scene_objects`, `modify_object`, `create_prefab`, `run_simulation`, `execute_method`, `batch_operations`, `move_along_path` |
| `unity_jobs` | `submit` (build/batch_import/simulation), `status`, `list`, `cancel` |
| `unity_import` | `import_blender`, `import_fleet_batch`, `list_formats` |
| `unity_vision_refine` | `capture`, `review_bundle`, `apply_bridge_commands` |
| `unity_validation` | `list_limits`, `validate_scene`, `check_polycount`, `check_materials`, `validate_model`, `validate_avatar`, `unified_audit` |
| `vrchat` | `check_auth`, `authenticate`, `check_sdk`, `validate_avatar`, `setup_descriptor`, `upload_avatar` |
| `worldlabs` | `assemble_review`, `import_marble`, `check_gaussian`, `install_gaussian`, `optimize_for_vrchat` |
| `multiplatform` | `list_platforms`, `check_sdk`, `check_cck`, `setup_cvr_avatar`, `validate_cvr`, `prepare_resonite`, `check_cluster_kit`, `prepare_cluster`, `audit_all` |
| `unity_build` | `build_project` |
| `unity_asset` | `optimize_textures` |
| `unity3d_disk_api` | Direct UnityPy disk manipulation |
| `unity3d_agentic_workflow` | SEP-1577 autonomous multi-step orchestration |

## REST API (FastAPI, port 10831)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Server health, version, tool count, uptime |
| GET | `/api/v1/status` | Detailed status + Unity Editor detection |
| GET | `/api/v1/llm/providers` | Probe Ollama/LM Studio |
| GET | `/api/v1/scene` | Scene hierarchy with transforms |
| GET | `/api/v1/avatar/status` | Avatar pipeline metrics |
| GET | `/api/v1/packages` | Installed UPM packages |
| GET | `/api/v1/editor/scripts` | C# script library |
| GET | `/api/v1/apps` | Connected apps |

## Fleet mesh

- **gazebo-mcp** → syncs Gazebo models → Unity for rendering
- **freecad-mcp** → imports CAD models
- **avatar-mcp** → VRM avatar compositing
- **resonite-mcp** → VR spatial sync
- **worldlabs-mcp** → AI-generated 3D worlds

## Testing

```powershell
.\scripts\run-tests.ps1
uv run pytest
```

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
