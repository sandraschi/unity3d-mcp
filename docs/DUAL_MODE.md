# Hands-In vs Hands-Off (Live GUI vs Headless)

unity3d-mcp uses **dual-mode execution**, similar to blender-mcp live session vs headless `bpy` subprocess.

## Hands-In — Live GUI (watch the Editor)

**Requires:** Unity Editor open with `MCPBridge.cs` in `Assets/Editor/` (bridge on **http://localhost:10835**).

You see changes live in the Unity window:

| Capability | Tool |
|------------|------|
| Hierarchy, create/delete/transform | `unity_bridge`, `unity_api` |
| Game view / multi-angle captures | `unity_render`, `unity_vision_refine` |
| Play-mode simulation (visible) | `unity_api` → `run_simulation`, `unity_jobs` → `simulation` |
| Live polycount / materials / missing scripts | `unity_validation` → `validate_scene` |

Check mode:

```text
unity_bridge(operation='execution_mode')
```

Returns `mode: hands_in` when the bridge responds.

## Hands-Off — Headless / disk (no Editor GUI)

**Unity Editor closed** (or bridge disconnected). MCP still runs; tools use disk/batch paths:

| Capability | Tool |
|------------|------|
| UnityPy asset/prefab inspection | `unity3d_disk_api` |
| Copy GLB/VRM into `Assets/` | `unity_import` |
| File-size / format checks | `unity_validation` → `validate_model` |
| **Builds** (Unity `-batchmode -nographics`) | `unity_jobs` → `build` |
| Fleet HTTP import/export | REST `/api/v1/...` |

Build and batch validation jobs **do not show a Unity GUI** — Unity runs headless. That is expected for CI and long builds.

## Docker note

The **GHCR/Docker image** runs the MCP HTTP server only. It does **not** include the Unity Editor.

- Container: MCP, metrics, logs, fleet REST.
- Host: Unity Editor + bridge for **Hands-In** live watching.

Set `UNITY3D_MCP_BRIDGE_HOST=host.docker.internal` (default in `docker-compose.yml`) so the container can reach the host bridge on port 10835.

## Agent guidance

1. Call `unity_bridge` → `execution_mode` before scene edits.
2. Prefer bridge tools when `hands_in`; fall back to disk/import/jobs when `hands_off`.
3. Use `unity_jobs` for builds regardless of mode (always batch/headless Unity).

See also [GUIDE_EDITOR_AUTO.md](GUIDE_EDITOR_AUTO.md) and [MONITORING.md](MONITORING.md).
