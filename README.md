# Unity3D MCP Server

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

**FastMCP 3.2.0+ Compliant** - Comprehensive Unity 3D automation with VRM avatar pipeline and VRChat integration.

- [Competitive Analysis](docs/COMPETITIVE_ANALYSIS.md)
- [Roadmap (Phases 1–5)](docs/ROADMAP.md)

### Tool surface (verified against `src/unity3d_mcp/server.py`, 2026-07-18)

**This table is the single source of truth for this server's tools.** Any
other tool names you see elsewhere in this README below this point, or
inferred from `src/unity3d_mcp/app.py` (unused dead code — not imported by
`__main__.py` or referenced in `pyproject.toml`; the real entry point is
`server.py`), are stale. See the housekeeping note at the bottom of this
section.

**15 portmanteau tools** (one tool, `operation` argument selects behavior —
this is the real, current tool-count-reduction pattern this server uses):

| Tool | Operations |
|------|------------|
| `unity_core` | `launch_editor`, `create_project`, `execute_method`, `check_univrm`, `install_univrm`, `create_project_with_univrm` |
| `unity_scene` | `create_light` |
| `unity_avatar` | `import_vrm`, `setup_animator` |
| `unity_asset` | `optimize_textures` |
| `unity_build` | `build_project` |
| `vrchat` | `check_auth`, `authenticate`, `check_sdk`, `validate_avatar`, `setup_descriptor`, `upload_avatar` — **avatars only, no world upload/publish** |
| `worldlabs` | `assemble_review`, `import_marble`, `check_gaussian`, `install_gaussian`, `optimize_for_vrchat` |
| `multiplatform` | `list_platforms`, `check_sdk`, `check_cck`, `setup_cvr_avatar`, `validate_cvr`, `prepare_resonite`, `check_resonite_compat`, `check_cluster_kit`, `prepare_cluster`, `audit_all` (ChilloutVR/Resonite/Cluster — not VRChat, that's the `vrchat` tool) |
| `unity_bridge` | `status`, `execution_mode`, `ping`, `get_hierarchy`, `create_object`, `delete_object`, `transform_object`, `capture_game_view` — **live Editor, Hands-In only** |
| `unity_render` | `bridge_status`, `get_scene_summary`, `capture_multi_angle` — agent vision |
| `unity_api` | `get_scene_objects`, `modify_object`, `create_prefab`, `run_simulation`, `execute_method`, `batch_operations`, `move_along_path`, `create_path_visualization`, `follow_path_2d`, `follow_path_3d`, `stop_path_movement` — **all real, bridge-dependent** (require a live Unity Editor session with `MCPBridge.cs` running; return an honest "bridge not connected" error otherwise, not a fake success) |
| `unity_jobs` | `submit` (`job_type`: build/batch_import/simulation), `status`, `list`, `cancel` — async queue |
| `unity_import` | `import_blender`, `import_fleet_batch`, `list_formats` — Blender/fleet GLB/VRM/FBX/OBJ handoff |
| `unity_vision_refine` | `capture`, `review_bundle`, `apply_bridge_commands` |
| `unity_validation` | `list_limits`, `validate_scene`, `check_polycount`, `check_materials`, `validate_model`, `validate_avatar`, `unified_audit` |

**2 standalone tools** (dual-mode/agentic, registered directly, not via a
manager class):

| Tool | Purpose |
|------|---------|
| `unity3d_disk_api` | `[Hands-Off]` UnityPy disk manipulation: inspect_file, list_textures, modify_yaml — no overlap, genuinely standalone |
| `unity3d_agentic_workflow` | SEP-1577 sampling — autonomous multi-step orchestration from a high-level goal |

**Cleaned up 2026-07-18** (previously flagged here as known duplication,
now actually removed — see `TODO.md` for the full record):

- The 9 flat platform-helper tools (`list_vr_platforms`,
  `check_platform_sdk`, `check_cck_installed`, `setup_cvr_avatar`,
  `validate_for_chilloutvr`, `prepare_for_resonite`,
  `check_resonite_compatibility`, `check_cluster_kit`,
  `prepare_for_cluster`) are gone. Use `multiplatform(operation=...)`.
- The 11 flat `api_*` tools (`api_execute_method`, `api_get_scene_objects`,
  etc.) and their backing `_api_*` stub methods on the server class are
  gone. Use `unity_api(operation=...)` — the real implementation, which
  actually works for `get_scene_objects`/`modify_object` via the live
  bridge (the flat versions unconditionally returned "not implemented",
  even for those).
- `unity3d_bridge_status` and `unity3d_editor_api` are gone, folded into
  `unity_bridge`. The one operation `unity3d_editor_api` had that
  `unity_bridge` didn't — `capture_game_view` — is now a `unity_bridge`
  operation too. Use `unity_bridge(operation="status")` and
  `unity_bridge(operation=...)` instead.

**Still real, still unregistered** (not part of this pass — a bigger,
separate task if ever done): motor control (`api_add_motor` etc.), generic
asset export/import (`export_fbx`, `import_asset_package`, `batch_import`),
and dedicated VRM-Unity-rigging tools (`import_vrm_to_unity`,
`setup_unity_avatar_rigging`, etc.) are **not exposed as MCP tools at
all** — the underlying manager classes exist (`motor_manager.py`,
`import_export_manager.py`, `vrm_avatar_manager.py`) but nothing in
`server.py` registers them. `app.py` (and its `.bak` twin) is dead code
containing a second, never-wired implementation of some of this — don't
trust it as a source of truth for what's callable.

Copy `src/unity3d_mcp/resources/MCPBridge.cs` to your project's `Assets/Editor/` folder.

Webapp **Agent Tools** page: `/agent-tools` (mirror blender-mcp Agent Lab UI).

### Dual mode (live GUI vs headless)

| Mode | When | You see |
|------|------|---------|
| **Hands-In** | Unity Editor + `MCPBridge.cs` (:10835) | Scene edits, play-mode sim, captures live in Editor |
| **Hands-Off** | No bridge / disk-only | UnityPy edits, imports, **build jobs** (`-batchmode`, no GUI) |

`unity_bridge(operation='execution_mode')` reports current mode. See [docs/DUAL_MODE.md](docs/DUAL_MODE.md).

### Observability (v1.5)

- Prometheus: `http://127.0.0.1:9092/metrics` and `/api/v1/metrics` on :10831
- JSON logs: `UNITY3D_MCP_LOG_FORMAT=json`
- Docker: `docker compose --profile monitoring up -d` — [docs/MONITORING.md](docs/MONITORING.md), [docs/DOCKER.md](docs/DOCKER.md)

### Fleet pipeline (Blender → Unity)

```powershell
.\scripts\run-fleet-pipeline.ps1 -ProjectPath "D:\Unity\MyProject" -ModelPath "D:\exports\avatar.glb" -SkipBuild
```

See [docs/FLEET_PIPELINE.md](docs/FLEET_PIPELINE.md).

```text
blender-mcp export GLB/VRM → unity_import import_blender → unity_vision_refine review_bundle → VRChat/build
worldlabs Marble → worldlabs assemble_review → agent fixes → unity_jobs build
```

**One-shot automation:** [docs/FLEET_PIPELINE.md](docs/FLEET_PIPELINE.md) — `scripts/run-fleet-pipeline.ps1`


```powershell
git clone https://github.com/sandraschi/unity3d-mcp
cd unity3d-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:

## Features

### Core Unity Automation

- **Unity Editor Management**: Launch, control, and automate Unity Editor
- **Project Operations**: Create, configure, and manage Unity projects
- **Scene Management**: Create and manipulate Unity scenes
- **Build Pipeline**: Automated builds for multiple platforms

### Avatar & VRM Pipeline

- **VRM Import**: Import and configure VRM avatars for Unity
- **Avatar Optimization**: Optimize avatars for VRChat compatibility
- **Animation System**: Setup animator controllers and animation clips
- **Performance Profiling**: Analyze and optimize avatar performance

### Asset Management

- **Package Import**: Import Unity asset packages
- **Texture Optimization**: Platform-specific texture optimization
- **Material Management**: Create and convert materials for VRChat
- **Asset Organization**: Automated asset organization and versioning

### VRChat Integration

- **SDK Automation**: Automate VRChat SDK operations
- **Avatar Upload**: Upload avatars to VRChat platform
- **OSC Communication**: Real-time OSC parameter control
- **Performance Validation**: VRChat-specific performance validation
- **Authentication**: VRChat API auth with 2FA/TOTP support

### Multi-Platform Social VR

| Platform | Engine | Avatar Format | SDK | Status |
|----------|--------|---------------|-----|--------|
| **VRChat** | Unity | VRC prefab | VRChat SDK | Full support |
| **ChilloutVR** | Unity | CVR prefab | CCK | Supported |
| **Resonite** | FrooxEngine | VRM/GLB direct | None needed | Supported |
| **Cluster** | Unity | VRM | Creator Kit | Supported |

- **ChilloutVR**: CCK detection, CVRAvatar setup, validation
- **Resonite**: Direct VRM/GLB import (no Unity needed!)
- **Cluster**: Japanese social VR with VRM support

### Advanced Unity Editor API operations

Covered by the `unity_api` portmanteau tool (see the tool table above).
Every operation is real and bridge-dependent: it calls the `MCPBridge.cs`
Editor bridge (HTTP, `localhost:10835`) and requires Unity to be open with
that script installed and running. Two known, honestly-documented
limitations in the current bridge implementation:
- `execute_method` only supports public, static, **parameterless** Unity
  methods (the same constraint Unity's own `-executeMethod` CLI flag has).
  Passing `parameters` is accepted but explicitly reported back as
  ignored, not silently dropped or type-coerced.
- Path movement (`move_along_path`, `follow_path_2d`, `follow_path_3d`)
  approximates all `path_type` curve variants (`bezier`, `spline`,
  `catmull_rom`) as straight multi-segment linear interpolation — real
  curve math is not implemented.

This was verified by manual C# code review only (no `dotnet`/`mono`/`csc`
compiler was available in the environment this was built in), so treat it
as unverified against a live Unity Editor until you've smoke-tested it
yourself.

**Not currently exposed as MCP tools at all** (real code exists in
`motor_manager.py`, `import_export_manager.py`, and
`vrm_avatar_manager.py`, but nothing in `server.py` registers it):
motor control (attach/start/stop/configure motors on objects), generic
asset export/import (`.unitypackage`, standalone FBX/prefab export,
texture-specific import), and dedicated VRM-Unity-rigging tools separate
from `unity_avatar`'s `import_vrm`/`setup_animator`. If you need any of
these, they'd need a portmanteau wrapper written and registered in
`server.py` first — that's real, scoped future work, not a documentation
fix. Tracked in `TODO.md`.

### Agentic Sampling (SEP-1577)

FastMCP 3.2.0+ introduces **Agentic Sampling**, allowing the server to borrow the client's LLM to orchestrate complex workflows autonomously.

- **`unity3d_agentic_workflow`**: Execute a mission-based objective (e.g., "Setup a new VRChat project and import my avatar").

### Contextual Discovery (Skills & Prompts)

This server provides expert instructions and pre-defined workflows via the SOTA Skill system.

#### Skills
Available via `resource://unity3d/skills/`:
- `unity-editor-automation`: Expert guide for editor control.
- `vrc-avatar-pipeline`: Guide for VRM to VRChat optimization.

#### Prompts
Registered SOTA prompts:
- `unity_setup_workflow`: Guide for project initialization.
- `vrc_avatar_workflow`: Instructions for the VRM optimization lifecycle.

###  Dual-Mode Operations

This server uniquely supports two distinct operational modes for maximum flexibility across development and CI/CD environments.

#### 1. Hands-In (Active Session)
Real-time control of a running Unity Editor. Requires the **MCPBridge.cs** plugin.
- **Tools**: `unity_bridge` (operations: status, execution_mode, ping, get_hierarchy, create_object, delete_object, transform_object, capture_game_view)
- **Use Case**: Scene layout, live debugging, lighting setup, and real-time hierarchy manipulation.
- **Port**: 10835 (HTTP)
- **Guide**: [Real-Time Editor Automation](file:///D:/Dev/repos/unity3d-mcp/docs/GUIDE_EDITOR_AUTO.md)

#### 2. Hands-Off (Disk Operations)
Direct manipulation of Unity assets on disk. Powered by **UnityPy**.
- **Tools**: `unity3d_disk_api`
- **Use Case**: CI/CD pipelines, batch asset auditing, texture extraction, and quick prefab fixes without launching Unity.
- **Support**: Serialized files (.unity, .prefab, .asset) + Unity YAML source files.
- **Guide**: [Direct Disk Manipulation](file:///D:/Dev/repos/unity3d-mcp/docs/ARCHITECTURE_DUAL_MODE.md#mode-b-hands-off-disk-operations)

---

##  Technical Documentation

A comprehensive technical suite is available in the **[Documentation Portal](file:///D:/Dev/repos/unity3d-mcp/docs/README.md)**.

###  Core Concepts
- **[Architecture Deep Dive](file:///D:/Dev/repos/unity3d-mcp/docs/ARCHITECTURE_DUAL_MODE.md)**: Hands-In vs Hands-Off analysis.
- **[Complete API Reference](file:///D:/Dev/repos/unity3d-mcp/docs/API_REFERENCE.md)**: Details for all 50+ tools.

###  Specialized Pipeliens
- **[VRM-to-VRChat Guide](file:///D:/Dev/repos/unity3d-mcp/docs/GUIDE_VRCHAT_PIPELINE.md)**: High-fidelity avatar optimization.
- **[Scene Automation Guide](file:///D:/Dev/repos/unity3d-mcp/docs/GUIDE_EDITOR_AUTO.md)**: Real-time Editor control.

### Technical Standards

- **FastMCP 3.2.0+**: Latest MCP protocol implementation with ASGI/Uvicorn and SEP-1577 sampling.
- **Agentic Workflows**: Integrated autonomous orchestration using dual-mode intelligence.
- **Modular Skills**: Discoverable expert instructions for bridge installation and disk ops.
- **Structured Logging**: JSON-formatted logs via `structlog`.
- **Security**: CVE-2025-62801 and CVE-2025-62800 fixes applied.





### World Labs Integration

- **Marble Import**: Import AI-generated 3D worlds from World Labs Marble
- **Chisel Support**: Works with Chisel-edited environments
- **Gaussian Splatting**: Install renderer for `.ply`/`.splat` files
- **VRChat Optimization**: Recommendations for VRChat world uploads
- **Format Support**: OBJ, FBX, GLB, GLTF meshes + Gaussian Splats

### UniVRM Management

- **Package Detection**: Check if UniVRM is installed
- **Auto-Install**: Install UniVRM 0.x or 1.0 via Package Manager
- **Project Templates**: Create projects with UniVRM pre-configured

### Advanced Features

- **Dual Interface**: Both stdio and HTTP (ASGI/Uvicorn) interfaces.
- **FastMCP 3.2.0**: Modern MCP server architecture with sampling support.
- **Comprehensive Logging**: Structured logging with performance metrics.
- **Platform Management**: Multi-platform build and optimization.
- **Path Resolution**: Intelligent Unity installation detection.


##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx unity3d-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "unity3d-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/unity3d-mcp", "run", "unity3d-mcp"]
  }
}
```
### From PyPI (Recommended)

```bash
pip install unity3d-mcp
```

##  Packaging & Distribution

This repository is SOTA 2026 compliant and uses the officially validated `@anthropic-ai/mcpb` workflow for distribution.

### Pack Extension
To generate a `.mcpb` distribution bundle with complete source code and automated build exclusions:
```bash
# SOTA 2026 standard pack command
mcpb pack . dist/unity3d-mcp.mcpb
```

### From GitHub Releases

```bash
# Direct wheel download
pip install https://github.com/sandraschi/unity3d-mcp/releases/download/v1.2.0/unity3d_mcp-1.2.0-py3-none-any.whl

# Or from git
pip install git+https://github.com/sandraschi/unity3d-mcp.git
```

## Configuration

Create a configuration file or use environment variables:

```json
{
  "unity_editor_path": "C:/Program Files/Unity/Hub/Editor/2022.3.0f1/Editor/Unity.exe",
  "project_path": "D:/Unity Projects",
  "auto_detect_unity": true,
  "enable_http": true,
  "http_port": 8080,
  "log_level": "INFO"
}
```

## Usage

### Command Line

```bash
# Start in stdio mode
unity3d-mcp --mode stdio

# Start HTTP server
unity3d-mcp --mode http --port 8080

# Dual mode (stdio + HTTP)
unity3d-mcp --mode dual
```

### MCP Tools

See **[Tool surface](#tool-surface-verified-against-srcunity3d_mcpserverpy-2026-07-18)**
near the top of this README for the complete, verified-against-source tool
list with real operation names. (An earlier revision of this README had a
second, incompatible tool list here using names like `launch_unity_editor`,
`import_vrm_avatar`, `upload_vrchat_avatar` — those aren't callable tools;
the real operations are `unity_core(operation="launch_editor")`,
`unity_avatar(operation="import_vrm")`,
`vrchat(operation="upload_avatar")`, etc. Removed 2026-07-18 to stop the
two lists drifting further apart — one source of truth from now on.)

## Architecture

```
unity3d_mcp/
 core/           # Unity Editor automation, project management, UniVRM
 avatar/         # VRM avatar management
 assets/         # Asset import and optimization
 build/          # Build pipeline management
 vrchat/         # VRChat SDK integration + authentication
 worldlabs/      # World Labs Marble/Chisel integration
 utils/          # Shared utilities
```

## Testing

```powershell
# Run all tests
.\scripts\run-tests.ps1

# Run with coverage
.\scripts\run-tests.ps1 -Coverage

# Run E2E tests (requires Unity)
.\scripts\run-tests.ps1 -E2E

# Run specific test pattern
.\scripts\run-tests.ps1 -Pattern "test_worldlabs"
```

## Requirements

- Python 3.8+
- Unity Editor (2019.4 LTS or newer)
- VRChat SDK (for VRChat features)
- Windows 10/11 (primary support)

## Performance

Optimized for:

- VRChat avatar requirements
- Mobile VR platforms
- Multi-platform deployment
- Real-time OSC communication


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- Documentation: [GitHub Wiki](https://github.com/sandraschi/unity3d-mcp/wiki)
- Issues: [GitHub Issues](https://github.com/sandraschi/unity3d-mcp/issues)
- Discussions: [GitHub Discussions](https://github.com/sandraschi/unity3d-mcp/discussions)


##  Webapp Dashboard

This MCP server includes a premium SOTA web interface for monitoring and control.

### Port Allocation (Standardized)
- **Frontend**: `10830` (Vite / React)
- **Backend (API)**: `10831` (FastAPI / FastMCP)

To start the webapp:
1. Navigate to the `web_sota` directory.
2. Run `start.bat` (Windows) or `./start.ps1` (PowerShell).
3. The dashboard will automatically open at `http://localhost:10830`.
