# Improvement Roadmap

Phased plan derived from [COMPETITIVE_ANALYSIS.md](COMPETITIVE_ANALYSIS.md).
Mirrors the blender-mcp agent-lab phases, adapted for Unity Editor + social VR pipelines.

## Phase 1 — Bridge wiring and agent vision (1.1.0)

**Status: complete (v1.1.0)**

| Item | Tool / module |
|------|----------------|
| Bridge-first runtime | `utils/unity_runtime.py` |
| Game view / scene camera capture | `unity_render` → `capture_game_view` |
| Live bridge portmanteau | `unity_bridge` → status, hierarchy, create, delete, transform |
| Wire scaffolded scene API | `unity_api` → `get_scene_objects`, `modify_object` via bridge |
| Bridge screenshot action | `resources/MCPBridge.cs` → `capture_game_view` |
| Prometheus metrics skeleton | `utils/telemetry.py`, optional `monitoring` extra |

### Live GUI workflow

```powershell
# HTTP MCP (webapp / IDE)
uv run python -m unity3d_mcp --http --port 10831

# Unity Editor: copy MCPBridge.cs to Assets/Editor/
# Bridge auto-starts on load (or MCP > Start Bridge)

# Agent:
# unity_bridge operation=status
# unity_render operation=capture_game_view output_path=D:/Temp/unity_review.png
```

## Phase 2 — Jobs and build depth (1.2.0)

**Status: complete (v1.2.0)**

| Item | Tool / module |
|------|----------------|
| Async job queue | `unity_jobs` (submit build, batch import, status) |
| Prefab create via bridge | `unity_api` → `create_prefab` |
| Play mode simulation | `unity_api` → `run_simulation` + bridge poll runner |

## Phase 3 — Fleet handoff and vision refine (1.3.0)

**Status: complete (v1.3.0)**

| Item | Tool / module |
|------|----------------|
| Blender GLB/VRM import orchestration | `unity_import` + `utils/fleet_import.py` |
| Multi-angle capture review bundle | `unity_vision_refine` + `unity_render` multi-angle |
| World Labs + scene assembly agent loop | `worldlabs` → `assemble_review` |

## Phase 4 — Validation and polish (1.4.0)

| Item | Tool / module |
|------|----------------|
| General scene/mesh validation | `unity_validation` (polycount, materials, missing scripts) |
| VRChat + CVR + Resonite unified audit | extend `multiplatform` + validation |
| Webapp Agent Lab page | `/agent-tools` tabs (mirror blender-mcp) |

## Phase 5 — Telemetry, Docker, monitoring (1.5.0)

| Item | Tool / module |
|------|----------------|
| JSON logs for Loki | `UNITY3D_MCP_LOG_FORMAT=json` |
| Docker + GHCR image | `Dockerfile`, CI publish |
| Grafana/Prometheus profile | `docker-compose.yml --profile monitoring` |
| Smoke test script | `scripts/smoke_test.py` |
