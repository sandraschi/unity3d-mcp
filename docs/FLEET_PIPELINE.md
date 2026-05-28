# Fleet E2E pipeline (Gazebo + blender-mcp → unity3d-mcp)

Robotics + authoring handoff into Unity:

```text
gazebo_models (sim mesh) ──POST /api/v1/gazebo/import──┐
blender_export (GLB/VRM) ──unity_import─────────────────┤
                                                        ▼
                              unity_validation → unity_jobs build
```

**Gazebo** complements **Unity** for sim-origin meshes (robots, worlds); **Blender** for authored props/avatars.

## Prerequisites

| Step | Requires |
|------|----------|
| Gazebo import | Exported FBX/OBJ under `gazebo_models/{name}.fbx` (or custom template) |
| Gazebo-mcp export (optional) | gazebo-mcp HTTP on **10991** (when repo is running) |
| Blender export | blender-mcp **10849**, live Blender |
| Unity steps | unity3d-mcp (in-process via script) or HTTP **10831** for gazebo REST |

## Examples

Gazebo + Blender (full fleet):

```powershell
.\scripts\run-fleet-pipeline.ps1 `
  -ProjectPath "D:\Unity\RoboticsDemo" `
  -WithGazebo `
  -GazeboModels "scout" "warehouse_floor" `
  -GazeboFileTemplate "gazebo_models/{model}.fbx" `
  -ModelPath "D:\exports\props.glb" `
  -SkipBuild
```

Gazebo-only into Unity:

```powershell
uv run python scripts/fleet_pipeline.py `
  --project-path "D:\Unity\RoboticsDemo" `
  --with-gazebo `
  --gazebo-models scout warehouse_floor `
  --skip-export `
  --skip-build
```

Blender-only (previous behavior):

```powershell
.\scripts\run-fleet-pipeline.ps1 `
  -ProjectPath "D:\Unity\MyProject" `
  -ModelPath "D:\exports\avatar.glb" `
  -SkipBuild
```

## Flags

| Flag | Purpose |
|------|---------|
| `--with-gazebo` / `-WithGazebo` | Enable gazebo REST import step |
| `--gazebo-models` | Model names (required with `--with-gazebo`) |
| `--gazebo-file-template` | Default `gazebo_models/{model}.fbx` |
| `--try-gazebo-mcp-export` | Call gazebo-mcp export before import (when server available) |
| `--unity-url` | unity3d-mcp base (default `http://127.0.0.1:10831`) |

## Fleet role

See `mcp-central-docs/docs/FLEET_FOUNDATION.md` — **gazebo-mcp** bridges simulation state to **unity3d-mcp** for rendering and builds.
