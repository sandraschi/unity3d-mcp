# Changelog

All notable changes to Unity3D-MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-09-03

### Added (backport from overte-mcp/resonite-mcp: animate + fixture spawner)
- `MCPBridge.cs`: `animate_object`/`stop_animation` actions - loop-animate an object in place
  (spin/bob/bounce) via a new `_activeAnimations` dict ticked from `Update()`, following the
  exact same pattern as the existing `move_along_path`/`stop_path_movement` path-movement
  system (`_activeMovements`/`TickPathMovements`) rather than porting overte-mcp/resonite-mcp's
  Python-side blocking-loop shape unchanged - Unity already had the right architecture for
  this, a blocking call would have been a worse fit. `bounce` mode is a direct C# port of the
  identical closed-form drop-physics function already shipped in overte-mcp's `http_server.py`
  and resonite-mcp's `tools/resonite_link.py` - third platform, same math, not a
  reimplementation. Note: `spin` speed is **degrees/second** here (Unity's native
  `Quaternion.AngleAxis` convention), not radians/second like the other two ports - a real,
  documented unit difference between platforms.
- `CreateObject` gained `dimensions` (per-axis, alternative to the existing uniform `scale`)
  and `color` (applies to any primitive with a `Renderer`) - both needed for the fixture
  spawner, both additive/backward-compatible (existing callers passing only `scale` are
  unaffected).
- `unity_api(operation="fixture_spawn", fixture=..., position=..., ...)`: preset test fixtures
  (box/cup/ball/table/chair), same dimensions as overte-mcp/resonite-mcp's presets, built
  purely from Unity's own `Cube`/`Sphere` primitives via repeated `create_object` calls - no
  custom mesh generation needed (unlike resonite-mcp's port, which had to hand-build an
  icosahedron since ResoniteLink has no primitive-mesh components). No avatar-relative default
  placement - the Unity Editor has no "the user's viewpoint" concept to default to, so
  `position` defaults to the world origin if omitted.
- `unity_api(operation="animate_object"/"stop_animation", ...)`: Python-side wiring for the
  new bridge actions.
- `unity_bridge(operation="create_object", dimensions=..., color=...)`: exposed the new
  `create_object` fields directly too, not just internally via `fixture_spawn` - a caller who
  wants one non-uniformly-scaled or colored primitive without a whole fixture preset can now
  do that in one call.
- **Verification**: no live Unity Editor was running during this change (confirmed: no
  `Unity.exe` process, port 10835 unresponsive). C# changes were reviewed carefully (brace
  balance checked: 215/215 across the file) but NOT compiled - no .NET SDK with a C# compiler
  is available on this machine, only a runtime, and Unity's own DLLs aren't available outside
  a Unity install. Python composition logic (`_api_fixture_spawn`/`_api_animate_object`/
  `_api_stop_animation`) was verified offline against a mocked bridge (position/dimensions/
  color/naming all confirmed correct per fixture part, error paths for unknown fixture and
  invalid anim_mode confirmed). Existing test suite still passes unchanged (175 passed, 9
  skipped - same skip count as before, all needing a live Editor). **First real in-Editor
  test is still pending** - flag this before relying on it.

## [Unreleased] - 2026-09-02

### Fixed
- `MCPBridge.cs`'s `CreateObject` ignored `position`/`rotation` entirely and only special-cased
  `Light`/`Camera` types (no mesh at all for anything else) — found while fixing
  `robotics-mcp`'s broken vbot-spawn integration, which called a nonexistent
  `VbotSpawner.SpawnRobot` C# method via the (genuinely parameterless) `execute_unity_method`
  dispatch. `CreateObject`/`TransformObject` now apply position/rotation/scale, and support
  `Capsule`/`Sphere`/`Box` primitive mesh types for spawning a labeled placeholder when no real
  3D model exists yet. `unity_bridge(operation=...)` exposes the new `scale` parameter.
- Not yet verified against a live Unity Editor (none running during this pass) — existing test
  suite (175 passed, 9 skipped — the skips need a live Editor) is unaffected.

## [1.6.0] - 2026-07-25

### Added
- **HTTP REST API endpoints** — 8 new endpoints for the webapp dashboard:
  - `GET /api/v1/status` — server uptime, tool count, Unity Editor detection (processes, installed versions)
  - `GET /api/v1/llm/providers` — live probe of Ollama :11434 and LM Studio :1234
  - `GET /api/v1/scene` — active scenes, full GameObject hierarchy with transforms and components
  - `GET /api/v1/avatar/status` — VRChat auth, avatar performance metrics (polygons, VRAM, draw calls)
  - `GET /api/v1/packages` — installed UPM packages with versions, publisher, update status
  - `GET /api/v1/editor/scripts` — available C# snippets and recent execution history
  - `GET /api/v1/apps` — connected app catalog
- **Frontend pages restored with real API wiring** — Dashboard, Status, Script Console, Hierarchy, Avatar Pipeline, Plugin Manager, Apps Hub all now fetch from real backend endpoints instead of hardcoded data
- **Dashboard KPIs** now show live Unity Editor process count, server uptime, tool count from `/api/v1/health` + `/api/v1/status`
- **Scene Hierarchy** interactive tree clickable with Inspector panel showing transforms and components
- **Avatar Pipeline** displays real polygon counts, VRAM usage, draw calls, optimization suggestions from backend

### Fixed
- **Settings** catch block no longer fabricates fake `ollama: [{name:"llama3.2:3b"}]` data on API failure
- **Tools** port corrected from 10787 to 10831
- **Apps** dead Connect App button removed, now connects to real backend

## [1.5.0] - 2026-05-28

### Added
- **Prometheus telemetry**: tool counters/histograms, bridge/execution-mode/jobs gauges, `/api/v1/metrics` + sidecar `:9092`.
- **JSON logging** for Loki: `UNITY3D_MCP_LOG_FORMAT=json`.
- **Docker + GHCR**: `Dockerfile`, `docker-compose.yml`, monitoring profile (Prometheus/Grafana/Loki/Promtail).
- **`scripts/smoke_test.py`**: Agent Lab tool surface check.
- **`unity_bridge` → `execution_mode`**: Hands-In (live GUI) vs Hands-Off (headless/disk) reporting.
- **Docs**: `DUAL_MODE.md`, `MONITORING.md`, `DOCKER.md`.

### Changed
- Version bump **1.4.0 → 1.5.0** (Phase 5 telemetry and deployment).

## [1.4.0] - 2026-05-28

### Added
- **`unity_validation`** portmanteau: scene polycount/materials/missing scripts, model disk check, avatar + unified audit.
- **`utils/scene_validator.py`**, **`utils/platform_audit.py`**: validation metrics and cross-platform preflight.
- **`MCPBridge.cs`**: `validate_scene` action (triangle/material/missing-script counts).
- **`multiplatform` → `audit_all`**: VRChat + CVR + Resonite + Cluster unified audit.
- **Webapp `/agent-tools`**: Agent Lab UI with bridge, import, vision, validation, jobs, platform tabs.
- **REST `POST /api/v1/tool`**: webapp MCP tool bridge (mirrors blender-mcp pattern).

### Changed
- Help tabs updated for v1.4 validation + `/agent-tools`.
- Version bump **1.3.0 → 1.4.0** (Phase 4 validation and polish).

## [1.3.0] - 2026-05-28

### Added
- **`unity_import`** portmanteau: Blender/fleet GLB/VRM/FBX handoff (`import_blender`, `import_fleet_batch`, `list_formats`).
- **`unity_vision_refine`**: capture, review_bundle, apply_bridge_commands for agent vision loops.
- **`utils/fleet_import.py`**, **`utils/vision_refine.py`**: fleet import and review bundle helpers.
- **`worldlabs` → `assemble_review`**: import Marble assets then build vision review bundle.
- **`unity_render`**: `capture_multi_angle`, `get_scene_summary`.
- **`MCPBridge.cs`**: `capture_multi_angle`, `get_scene_summary`.

### Changed
- Webapp **Help** tabbed Agent Lab reference (v1.3).
- Version bump **1.2.0 → 1.3.0** (Phase 3 fleet handoff + vision refine).

## [1.2.0] - 2026-05-28

### Added
- **`unity_jobs`** portmanteau: async `build`, `batch_import`, and `simulation` jobs (submit/status/list/cancel).
- **`utils/job_queue.py`**: in-process job queue with Prometheus active-job gauge.
- **`utils/simulation_runner.py`**: bridge play-mode simulation with status polling.
- **`MCPBridge.cs`**: `create_prefab`, `run_simulation`, `simulation_status`, `stop_simulation`.

### Changed
- **`unity_api`**: `create_prefab` and `run_simulation` wired to live bridge (no longer scaffold-only).
- Version bump **1.1.0 → 1.2.0** (Phase 2 jobs and build depth).

## [1.1.0] - 2026-05-28

### Added
- **Competitive analysis and roadmap**: `docs/COMPETITIVE_ANALYSIS.md`, `docs/ROADMAP.md` (phases 1–5).
- **`unity_bridge`** portmanteau: live Editor bridge status, hierarchy, create/delete/transform via `MCPBridge.cs`.
- **`unity_render`** portmanteau: `capture_game_view` for agent vision loops (PNG + optional base64).
- **`utils/unity_runtime.py`**: bridge-first execution helper (`execute_bridge_action`).
- **`utils/telemetry.py`**: Prometheus metrics skeleton (`monitoring` optional extra).
- **`MCPBridge.cs`**: `capture_game_view` action (scene camera render to PNG).

### Changed
- **`unity_api`**: `get_scene_objects` and `modify_object` wired to live bridge (no longer scaffold-only for these ops).
- Version bump **1.0.0 → 1.1.0** (Phase 1 agent vision + bridge wiring).

## [Unreleased] - 2026-04-02

### Changed
- **UPGRADED to FastMCP 3.2.0**: Latest SOTA protocol standards.
  - Migrated from FastMCP 2.13 to **FastMCP 3.2.0**.
  - **ASGI Compatibility Fix**: Fixed startup failure by exposing global `app` attribute in `unity3d_mcp.server`.
  - Standardized webapp backend port to **10831** and frontend to **10830**.
  - Synchronized `server.py` with unified transport module (`transport.py`).
  - Improved `run_stdio` and `run_http` methods for better error handling and SOTA compliance.

- **UPGRADED to FastMCP 2.13+**: Complete migration to SOTA standards
  - FastMCP dependency updated to `>=2.13.0,<2.14.0` (from 2.10)
  - Added server lifespan context manager for proper startup/shutdown
  - Migrated to structured logging with `structlog` (JSON output)
  - All logging now uses stderr (stdout reserved for MCP protocol)
  - Removed all `description=` parameters from `@mcp.tool` decorators
  - Enhanced all tool docstrings with comprehensive Args/Returns/Examples
  - All docstrings now follow FastMCP 2.13+ standards (200+ lines for complex tools)
  - Security fixes: CVE-2025-62801 (command injection), CVE-2025-62800 (XSS)
  - Module docstring updated to reflect FastMCP 2.13+ compliance
- **BREAKING**: Removed `OSCManager` - use `oscmcp` for OSC functionality
- OSC operations now require FastMCP server composition with `oscmcp`
- See module docstring in `vrchat/__init__.py` for composition example

### Added

#### World Labs Integration (Marble/Chisel)
- `import_marble_world`: Import 3D worlds from World Labs Marble/Chisel
- `check_gaussian_splatting`: Check if Gaussian Splatting renderer installed
- `install_gaussian_splatting`: Install aras-p/UnityGaussianSplatting package
- `optimize_worldlabs_for_vrchat`: VRChat optimization recommendations
- Support for mesh formats: `.obj`, `.fbx`, `.glb`, `.gltf`
- Support for Gaussian Splats: `.ply`, `.splat`
- Automatic asset organization (Visuals/, Colliders/, Splats/)

#### UniVRM Package Management
- `check_univrm_installed`: Check UniVRM installation status
- `install_univrm`: Install UniVRM 0.x or 1.0 via Package Manager
- `create_unity_project_with_univrm`: Create project with UniVRM pre-installed
- Git-based package installation via manifest.json

#### Multi-Platform Social VR Support
- `list_vr_platforms`: List all supported social VR platforms
- `check_platform_sdk`: Check SDK installation for any platform
- **ChilloutVR (CCK)**
  - `check_cck_installed`: Check CCK installation
  - `setup_cvr_avatar`: Configure CVRAvatar component
  - `validate_for_chilloutvr`: Validate avatar for CVR
- **Resonite** (no Unity SDK needed - direct import!)
  - `prepare_for_resonite`: Prepare VRM/GLB for direct import
  - `check_resonite_compatibility`: Check model compatibility
- **Cluster** (Japanese social VR)
  - `check_cluster_kit`: Check Creator Kit installation
  - `prepare_for_cluster`: Prepare avatar for Cluster upload

#### VRChat Authentication
- `vrchat_check_auth`: Check VRChat authentication status
- `vrchat_authenticate`: Authenticate with VRChat API (supports 2FA/TOTP)
- `vrchat_check_sdk`: Verify VRChat SDK installation
- `vrchat_validate_avatar`: Validate avatar before upload

#### Testing Infrastructure
- Comprehensive test suite (119+ tests)
- Organized test structure: `unit/`, `integration/`, `e2e/`, `fixtures/`
- Fixture factories for mock Unity projects
- VRM test file support with skip markers
- E2E tests for real Unity integration (--run-e2e flag)
- PowerShell test runner script

### Improved
- MCPB packaging with extensive prompt templates
- CI/CD workflows (GitHub Actions)
- .cursorrules with Rule #1
- .agravrules rulebook
- CONTRIBUTING.md and CHANGELOG.md
- Repository structure and organization
- Documentation quality
- Code quality (ruff configuration)
- Professional standards compliance

## [1.0.0] - 2025-10-26

### Added

#### Core Features
- Unity Editor automation and control
- Project and scene management
- Multi-platform build pipeline
- Asset package management

#### VRM Avatar Pipeline
- VRM import and validation
- Avatar optimization for VRChat
- Animation system setup
- Performance profiling
- Blend shape configuration

#### VRChat Integration
- VRChat SDK automation
- Avatar upload to VRChat platform
- Expression parameter setup
- Expression menu creation
- OSC real-time control
- Performance validation (Poor to Excellent ranks)

#### Additional Features
- Dual interface (stdio + HTTP)
- Comprehensive logging
- Platform management (Windows, macOS, Linux, Android, iOS)
- Intelligent Unity installation detection

### Documentation
- Complete README with feature overview
- Setup and installation guide
- Usage examples
- API reference

### Technical
- FastMCP 2.10+ framework
- Async/await architecture
- Type hints throughout
- Error handling and logging

### Standards
- FastMCP 2.12+ compliant
- MCPB packaging
- Professional folder structure
- Modern Python tooling

---

## Version History

| Version | Date | Type | Description |
|---------|------|------|-------------|
| 1.2.0 | 2025-11-27 | Minor | Multi-Platform Social VR (ChilloutVR, Resonite, Cluster) |
| 1.1.0 | 2025-11-26 | Minor | World Labs + UniVRM + Auth + Testing |
| 1.0.0 | 2025-10-26 | Major | Initial release - Unity automation + VRM + VRChat |

---

**Generated:** 2025-11-26  
**Maintained by:** Sandra  
**Project:** Unity3D-MCP - Professional Unity automation with Austrian precision! 🇦🇹🎮


