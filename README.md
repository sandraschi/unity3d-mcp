# Unity3D MCP Server

Comprehensive Unity 3D automation with VRM avatar pipeline and VRChat integration.

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

- **Dual Interface**: Both stdio and HTTP interfaces
- **FastMCP 2.10**: Modern MCP server architecture
- **Comprehensive Logging**: Structured logging with performance metrics
- **Platform Management**: Multi-platform build and optimization
- **Path Resolution**: Intelligent Unity installation detection

## Installation

### Via Claude Desktop (DXT Package)

1. Download the latest `.dxt` package from releases
2. Install via Claude Desktop MCP settings
3. Configure Unity Editor path in settings

### Manual Installation

```bash
pip install unity3d-mcp
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
├── core/           # Unity Editor automation, project management, UniVRM
├── avatar/         # VRM avatar management
├── assets/         # Asset import and optimization
├── build/          # Build pipeline management
├── vrchat/         # VRChat SDK integration + authentication
├── worldlabs/      # World Labs Marble/Chisel integration
└── utils/          # Shared utilities
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
