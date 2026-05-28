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

### Agent Lab (v1.5.0)

| Tool | Purpose |
|------|---------|
| `unity_bridge` | Live Editor bridge — **`execution_mode`** (Hands-In vs Hands-Off), hierarchy, CRUD |
| `unity_render` | Agent vision — capture, multi-angle, scene summary |
| `unity_vision_refine` | Review bundle + apply bridge commands after vision model feedback |
| `unity_import` | **Blender/fleet handoff** — GLB/VRM/FBX batch import into Assets |
| `unity_validation` | **Scene/avatar preflight** — polycount, materials, missing scripts, unified audit |
| `unity_api` | Scene objects, modify, create_prefab, run_simulation |
| `unity_jobs` | Async build, batch_import, simulation |
| `worldlabs` | Marble import + **`assemble_review`** agent loop |
| `multiplatform` | CVR/Resonite/Cluster + **`audit_all`** unified platform audit |

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

```text
blender-mcp export GLB/VRM → unity_import import_blender → unity_vision_refine review_bundle → VRChat/build
worldlabs Marble → worldlabs assemble_review → agent fixes → unity_jobs build
```


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

### Unity Editor API Tools (Advanced)

** Future Enhancement** - Scaffolded for Unity Editor API integration

These tools provide direct Unity Editor API access for advanced operations that CLI cannot handle:

#### Core API Tools
- **Method Execution**: `api_execute_method()` - Execute Unity methods with complex parameters
- **Scene Inspection**: `api_get_scene_objects()` - Get detailed scene object information
- **Object Manipulation**: `api_modify_object()` - Direct object property modification
- **Prefab Creation**: `api_create_prefab()` - Create prefabs with proper references
- **Physics Simulation**: `api_run_simulation()` - Run physics simulation with data recording
- **Batch Operations**: `api_batch_operations()` - Atomic multi-operation execution

#### Path Movement Tools
- **Path Animation**: `api_move_along_path()` - Move objects along straight/spline/2D/3D paths
- **Path Visualization**: `api_create_path_visualization()` - Create visual path representations
- **2D Path Following**: `api_follow_path_2d()` - 2D movement with rotation and look-ahead
- **3D Path Following**: `api_follow_path_3d()` - 3D movement with banking and elevation
- **Movement Control**: `api_stop_path_movement()` - Stop path movement with deceleration

#### Motor Control Tools
- **Add Motor**: `api_add_motor()` - Attach configurable motors to objects
- **Start Motor**: `api_start_motor()` - Start motors with speed/acceleration control
- **Stop Motor**: `api_stop_motor()` - Stop motors with deceleration options
- **Set Speed**: `api_set_motor_speed()` - Dynamic speed adjustments during operation
- **Motor Status**: `api_get_motor_status()` - Real-time motor monitoring and diagnostics
- **Physics Config**: `api_configure_motor_physics()` - Realistic motor physics simulation

#### Import/Export Tools
- **Import Package**: `import_asset_package()` - Import Unity .unitypackage files
- **Import 3D Model**: `import_3d_model()` - Import FBX, OBJ, GLTF, etc.
- **Import Texture**: `import_texture()` - Import textures with type-specific settings
- **Export FBX**: `export_fbx()` - Export objects to FBX format
- **Export Package**: `export_unity_package()` - Create .unitypackage files
- **Export Prefab**: `export_prefab()` - Export objects as prefabs
- **Batch Import**: `batch_import()` - Perform multiple imports at once
- **Import Status**: `get_import_status()` - Monitor import operation progress
- **Export Status**: `get_export_status()` - Monitor export operation progress

#### VRM Avatar Tools (Unity Integration)
- **Import VRM to Unity**: `import_vrm_to_unity()` - Import VRM into Unity projects
- **Unity Rigging Setup**: `setup_unity_avatar_rigging()` - Configure Unity humanoid rigging
- **Unity Materials**: `configure_unity_materials()` - Setup Unity-specific materials
- **Build Avatar Package**: `build_unity_avatar_package()` - Create complete Unity packages
- **Avatar-mcp Integration**: `integrate_with_avatarmcp()` - Connect to avatar-mcp for compositing
- **Import Status**: `get_unity_import_status()` - Monitor Unity VRM import progress
- **Legacy VRM Import**: `import_vrm_avatar()` - Basic VRM import (delegates to avatar-mcp)

*Note: These tools are currently scaffolded and return "not implemented" status. They require Unity Editor plugin development for full functionality.*

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
- **Tools**: `unity3d_editor_api`, `unity3d_bridge_status`
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

#### Core Unity Operations

- `launch_unity_editor`: Launch Unity Editor with project
- `create_unity_project`: Create new Unity project
- `execute_unity_method`: Execute Unity Editor methods

#### Avatar Management

- `import_vrm_avatar`: Import VRM avatar into Unity
- `setup_avatar_animator`: Configure animator controller
- `optimize_for_vrchat`: Apply VRChat optimizations

#### Asset Operations

- `import_asset_package`: Import Unity packages
- `optimize_textures`: Optimize textures for platforms
- `create_material`: Create Unity materials

#### Build Pipeline

- `build_unity_project`: Build for target platforms
- `switch_platform`: Switch Unity platform
- `optimize_for_platform`: Apply platform optimizations

#### VRChat Integration

- `upload_vrchat_avatar`: Upload avatar to VRChat
- `vrchat_check_auth`: Check authentication status
- `vrchat_authenticate`: Authenticate with VRChat API
- `vrchat_check_sdk`: Verify SDK installation
- `vrchat_validate_avatar`: Validate avatar before upload
- `send_avatar_parameter`: Send OSC parameters
- `send_chatbox_message`: Send VRChat chatbox messages

#### World Labs (Marble/Chisel)

- `import_marble_world`: Import 3D worlds from Marble exports
- `check_gaussian_splatting`: Check renderer installation
- `install_gaussian_splatting`: Install Gaussian Splatting package
- `optimize_worldlabs_for_vrchat`: Get VRChat optimization tips

#### UniVRM Management

- `check_univrm_installed`: Check UniVRM installation
- `install_univrm`: Install UniVRM packages
- `create_unity_project_with_univrm`: Create project with UniVRM

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
