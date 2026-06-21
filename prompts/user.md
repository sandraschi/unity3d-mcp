# Unity3D-MCP User Guide

Welcome to Unity3D-MCP, your AI-powered Unity development assistant. This guide covers everything from basic setup to advanced workflows.

## Getting Started

### Prerequisites
- Python 3.12 or later
- Unity Editor (2019.4 LTS or later, 2022.3 LTS recommended)
- Unity Hub (recommended for version management)

### Installation
```bash
pip install unity3d-mcp
```

Or for development:
```bash
git clone https://github.com/sandraschi/unity3d-mcp.git
cd unity3d-mcp
uv sync
```

### Configuration
Set the following environment variables based on your needs:
- `UNITY_PROJECT_PATH`: Default Unity project path
- `UNITY_EDITOR_PATH`: Explicit Unity Editor path
- `VRCHAT_USERNAME` and `VRCHAT_PASSWORD`: For VRChat uploads
- `VRCHAT_TOTP_SECRET`: For 2FA-authenticated VRChat accounts
- `UNITY3D_MCP_LOG_FORMAT`: Set to "json" for structured JSON logging
- `UNITY3D_MCP_START_METRICS_SERVER`: "true" (default) or "false"

### Quick Start
1. Start the server: `uv run python -m unity3d_mcp.server`
2. The server listens on stdio for MCP protocol
3. In HTTP mode, the server listens on port 10831
4. The web dashboard is available on port 10830

## Unity Editor Operations

### Launching the Editor
```python
await unity3d_editor_api(action="ping")
```

Check editor status without parameters. The tool automatically detects Unity installations from Unity Hub and common installation paths.

### Project Management
```python
# Check if a project has UniVRM installed
await check_univrm_installed(project_path="D:/Projects/MyAvatar")

# Install UniVRM in an existing project
await install_univrm(project_path="D:/Projects/MyAvatar", vrm_version="vrm0")

# Create a new project with UniVRM pre-installed
await create_project_with_univrm(
    project_name="VRChatProject",
    project_path="D:/Projects",
    unity_version="2022.3",
    vrm_version="vrm1"
)
```

### Scene Management
```python
# Create a directional light
await api_execute_method(
    class_name="MCP.MCPBridge",
    method_name="CreateLight",
    parameters={
        "name": "Sun",
        "type": "Directional",
        "intensity": 1.0
    }
)
```

## VRM Avatar Pipeline

### Importing VRM Files
```python
await import_vrm_avatar(
    vrm_path="D:/Avatars/my_avatar.vrm",
    project_path="D:/Projects/MyAvatar",
    optimize_for_vrchat=True,
    create_prefab=True
)
```

### Animation Setup
```python
# Setup animator with facial expressions
await setup_animator_controller(
    avatar_path="D:/Projects/MyAvatar/Assets/Models/my_avatar.vrm",
    animator_type="humanoid",
    include_facial=True
)

# Create a custom animation clip
await create_animation_clip(
    clip_name="Wave",
    duration=1.5,
    keyframes=[
        {"property": "Arm_Left.localRotation.x", "time": 0.0, "value": 0.0},
        {"property": "Arm_Left.localRotation.x", "time": 0.75, "value": -45.0},
        {"property": "Arm_Left.localRotation.x", "time": 1.5, "value": 0.0}
    ]
)
```

## VRChat Integration

### Authentication
```python
# Check current authentication status
await check_vrchat_authentication()

# Authenticate with VRChat API
await authenticate_vrchat(username="your_username", password="your_password")

# With 2FA
await authenticate_vrchat(
    username="your_username",
    password="your_password",
    totp_code="123456"
)
```

### Avatar Validation and Upload
```python
# Validate avatar before upload
await vrchat_validate_avatar(
    avatar_prefab="Assets/Avatars/MyAvatar.prefab",
    project_path="D:/Projects/MyAvatar"
)

# Upload to VRChat
await vrchat_upload_avatar(
    avatar_prefab="Assets/Avatars/MyAvatar.prefab",
    avatar_name="My Awesome Avatar",
    description="A cool avatar with custom expressions",
    tags=["cool", "custom", "furry"],
    release_status="public"
)
```

## Asset Management

### Importing Assets
```python
# Import a .unitypackage
await import_package(
    package_path="D:/Downloads/Textures.unitypackage",
    project_path="D:/Projects/MyGame",
    interactive=False
)
```

### Material Management
```python
# Create a new material
await create_material("RedMetal", "Standard", {
    "_Color": [1.0, 0.0, 0.0, 1.0],
    "_Metallic": 0.8,
    "_Glossiness": 0.3
})

# Convert materials for VRChat
await convert_materials_vrchat(
    material_paths=["Assets/Materials/Character.mat"],
    project_path="D:/Projects/MyAvatar"
)

# Optimize textures for target platform
await optimize_textures(
    texture_paths=["Assets/Textures/albedo.png"],
    platform="Android",
    quality="High"
)
```

## Build Pipeline

### Building Projects
```python
# Build for Windows
await build_project(
    project_path="D:/Projects/MyGame",
    build_target="StandaloneWindows64",
    output_path="D:/Builds/MyGame"
)

# Build for Android
await build_project(
    project_path="D:/Projects/MyGame",
    build_target="Android",
    output_path="D:/Builds/MyGame_Android",
    development_build=True
)
```

### Build Settings
```python
# Get current build settings
await get_build_settings(project_path="D:/Projects/MyGame")

# Switch platform
await switch_platform(
    project_path="D:/Projects/MyGame",
    target_platform="Android"
)

# Apply platform optimizations
await optimize_for_platform(
    project_path="D:/Projects/MyGame",
    platform="Android"
)
```

## Social VR Platform Operations

### ChilloutVR
```python
# Check CCK installation
await check_cck_installed(project_path="D:/Projects/CVR")

# Setup avatar for ChilloutVR
await setup_cvr_avatar(
    avatar_object="MyAvatar",
    project_path="D:/Projects/CVR",
    eye_height=1.6
)

# Validate for CVR upload
await validate_for_chilloutvr(
    avatar_name="MyAvatar",
    project_path="D:/Projects/CVR"
)
```

### Resonite
```python
# Prepare model for Resonite (VRM/GLB direct import)
await prepare_for_resonite(model_path="D:/Avatars/model.vrm")

# Check compatibility
await check_resonite_compatibility(model_path="D:/Avatars/model.glb")
```

### Cluster
```python
# Check Cluster Creator Kit
await check_cluster_kit(project_path="D:/Projects/Cluster")

# Prepare avatar for Cluster
await prepare_for_cluster(
    avatar_path="Assets/Avatars/MyAvatar.prefab",
    project_path="D:/Projects/Cluster"
)
```

## World Labs Integration

### Importing Marble Worlds
```python
# Import a Marble-exported world
await import_marble_world(
    source_path="D:/Worlds/forest/",
    project_path="D:/Projects/MarbleWorlds",
    asset_name="ForestScene"
)

# Check and install Gaussian Splatting
await check_gaussian_splatting_installed(project_path="D:/Projects/MarbleWorlds")

# Install Gaussian Splatting package
await install_gaussian_splatting(project_path="D:/Projects/MarbleWorlds")
```

## Motor Control System

### Basic Motor Operations
```python
# Create a motor configuration
await motor_control(
    operation="configure",
    motor_id="motor_1",
    max_speed=1000,
    acceleration=500,
    deceleration=500,
    pid_p=0.5,
    pid_i=0.01,
    pid_d=0.1
)

# Run motor program
await motor_control(
    operation="run_program",
    motor_id="motor_1",
    program=[
        {"target_speed": 500, "duration": 2.0},
        {"target_speed": 1000, "duration": 3.0},
        {"target_speed": 0, "duration": 1.0}
    ]
)

# Monitor motor status
await motor_control(
    operation="status",
    motor_id="motor_1"
)
```

## Hands-In and Hands-Off Dual Mode

Unity3D-MCP supports two execution modes:

### Hands-In (Live Unity Editor Bridge)
When the Unity Editor is running with MCPBridge.cs installed:
```python
# Get live scene hierarchy
await unity3d_editor_api(action="get_hierarchy")

# Move an object in real-time
await unity3d_editor_api(
    action="transform_object",
    target="MyCube",
    position=[5.0, 1.0, 3.0],
    rotation=[0.0, 45.0, 0.0]
)

# Capture game view screenshot
await unity3d_editor_api(
    action="capture_game_view",
    output_path="D:/screenshots/scene.png",
    width=1920,
    height=1080
)
```

### Hands-Off (Direct Disk Access)
When Unity is not running, manipulate project files directly:
```python
# Inspect a Unity scene file
await unity3d_disk_api(
    operation="inspect_file",
    file_path="D:/Projects/MyGame/Assets/Scenes/Main.unity"
)

# List textures in a project
await unity3d_disk_api(
    operation="list_textures",
    file_path="D:/Projects/MyGame/Assets"
)

# Modify a YAML property
await unity3d_disk_api(
    operation="modify_yaml",
    file_path="D:/Projects/MyGame/Assets/Materials/RedMetal.mat",
    component_type="Material",
    property_name="m_Color",
    new_value="1.0 0.0 0.0 1.0"
)
```

## Advanced Path Operations

### 2D Path Following
```python
await api_follow_path_2d(
    object_name="GroundRobot",
    path_points=[
        {"x": 0, "z": 0},
        {"x": 10, "z": 0},
        {"x": 10, "z": 10}
    ],
    speed=2.0,
    look_ahead=1.0,
    smooth_rotation=True
)
```

### 3D Path Following with Banking
```python
await api_follow_path_3d(
    object_name="Drone",
    path_points=[
        {"x": 0, "y": 2, "z": 0},
        {"x": 5, "y": 4, "z": 2},
        {"x": 10, "y": 3, "z": 5}
    ],
    speed=3.0,
    bank_angle=30.0,
    look_ahead=2.0
)
```

## Performance Optimization

### Avatar Performance
```python
# Analyze avatar performance
await vrchat_validate_avatar(
    avatar_prefab="Assets/Avatars/MyAvatar.prefab",
    project_path="D:/Projects/MyAvatar"
)

# The response includes polygon count, material count,
# texture memory, bone count, and performance rank.
```

### Texture Optimization
```python
# Optimize textures for VR
await optimize_textures(
    texture_paths=["Assets/Textures/face_albedo.png", "Assets/Textures/body_albedo.png"],
    platform="VR",
    quality="High"
)
```

## Import/Export Management

### Model Import
The import_export_manager supports various 3D formats. Each import extracts materials and textures automatically.

```python
# Import a single FBX file
await import_3d_model(
    file_path="D:/Models/character.fbx",
    project_path="D:/Projects/MyGame",
    extract_materials=True
)

# Import multiple files as batch
await import_3d_model(
    file_path=["D:/Models/building.fbx", "D:/Models/tree.fbx"],
    project_path="D:/Projects/MyGame",
    scale=0.01
)
```

### GLTF/GLB Export
Export scenes or objects for use in other engines or web viewers.

```python
# Export single object
await export_gltf(
    object_names="Character",
    output_path="D:/Exports/character.gltf"
)

# Export multiple objects to single file
await export_gltf(
    object_names=["Building", "Terrain"],
    output_path="D:/Exports/level.glb"
)
```

### Unity Package Export
Share your assets as .unitypackage files:

```python
await export_unity_package(
    asset_paths=["Assets/Characters", "Assets/Animations"],
    output_path="D:/Exports/character_pack.unitypackage"
)
```

## Batch Operations

### Sequential Motor Programs
```python
await motor_control(
    operation="run_program",
    motor_id="assembly_arm",
    program=[
        {"target_speed": 200, "duration": 1.0},
        {"target_speed": 500, "duration": 2.0},
        {"target_speed": 0, "duration": 0.5}
    ],
    loop=True
)
```

### Batch API Operations
```python
await api_batch_operations(
    operations=[
        {
            "type": "execute_method",
            "class_name": "VbotSpawner",
            "method_name": "SpawnRobot",
            "parameters": {"robotId": "robot_01", "robotType": "scout"}
        },
        {
            "type": "execute_method",
            "class_name": "VbotSpawner",
            "method_name": "SpawnRobot",
            "parameters": {"robotId": "robot_02", "robotType": "heavy"}
        }
    ]
)
```

## MCPBridge.cs Setup

MCPBridge.cs enables real-time communication with a running Unity Editor. For Hands-In mode:

1. The server attempts to install MCPBridge.cs automatically when needed
2. The bridge file goes to Assets/Editor/MCP/MCPBridge.cs
3. Communication happens over TCP on port 10835
4. The bridge supports: CreateLight, GetSceneObjects, MoveObject, and custom methods

To verify bridge status:
```python
await unity3d_bridge_status()
# Returns: {"status": "connected", "port": 10835}
```

If the bridge is disconnected:
1. Ensure Unity Editor is running with the project open
2. Check that MCPBridge.cs exists in Assets/Editor/MCP/
3. Restart the Unity Editor if the bridge was just installed

## Server Configuration

### HTTP Mode
The server can run in HTTP mode for REST API access:

```python
# In HTTP mode, the server listens on port 10831
# API endpoints:
# GET  /health - Server health check
# GET  /api/logs - Query activity log
# GET  /api/logs/stats - Log statistics
# POST /api/v1/launch - Launch fleet apps
```

### Structured Logging
Enable JSON-formatted structured logging for log aggregation:

```bash
set UNITY3D_MCP_LOG_FORMAT=json
```

This produces structured log entries consumable by Elasticsearch, Loki, or any JSON log aggregator.

### Metrics
Prometheus metrics are exposed when enabled:
```bash
set UNITY3D_MCP_START_METRICS_SERVER=true
```

Available metrics:
- unity3d_mcp_tool_calls_total - Total tool call count
- unity3d_mcp_active_jobs - Currently active background jobs
- unity3d_mcp_errors_total - Error count by tool

## Fleet Integration

### Cross-Server Handoffs
Unity3D-MCP integrates with other fleet MCP servers for pipeline workflows:

1. **godot-mcp**: Export GLB/GLTF scenes for import into Godot Engine for game builds
2. **worldlabs-mcp**: Generate 3D worlds with Marble AI, import into Unity via WorldLabsManager
3. **osc-mcp**: Handle VRChat OSC parameters (composed via FastMCP.mount)
4. **fleet-agent-mcp**: Centralized fleet monitoring and job orchestration
5. **aiwatcher-mcp**: Fleet-wide notification and digest system

### Fleet Exchange
The fleet exchange at FLEET_EXCHANGE_ROOT enables cross-repo asset sharing:
- Export GLB models to exchange for godot-mcp consumption
- Import Marble world meshes from worldlabs-mcp
- Stage VRChat avatar exports for deployment pipelines

## Performance Tuning

### VRChat Avatar Optimization Strategies

#### Polygon Reduction
Target triangle counts for each performance rank:
- Excellent: Under 7,500 triangles (use decimation tools)
- Good: Under 10,000 triangles (moderate optimization)
- Medium: Under 15,000 triangles (minimal optimization)
- Poor/Very Poor: Above limits, blocked in many worlds

#### Material Optimization
Reduce material count by:
1. Combine materials using texture atlases
2. Share materials across similar objects
3. Remove unused material slots
4. Use VRChat/Mobile shaders for efficiency

#### Texture Memory Optimization
Manage texture memory budget:
1. Resize textures to power-of-two dimensions
2. Use appropriate compression (DXT for PC, ASTC for mobile)
3. Remove unused texture channels (e.g., remove alpha if not used)
4. Use normal map compression where possible

#### Bone Count Optimization
Keep bone counts reasonable:
- Excellent: Under 150 bones
- Good: Under 256 bones
- Remove unnecessary bone chains (individual finger bones if not animated)
- Use generic bone naming conventions for compatibility

### Build Optimization

#### Platform-Specific Compression
- **Android**: ASTC 6x6 for high quality, ETC2 for compatibility
- **iOS**: ASTC 4x4 for Retina displays
- **PC**: DXT5 for color, BC5 for normals
- **WebGL**: DXT for desktop browsers, ETC2 for mobile WebGL

#### Script Stripping
- **High**: Aggressive stripping for mobile builds (test thoroughly)
- **Medium**: Balanced for most desktop builds
- **Low**: Minimal stripping for development builds
- **None**: Full assemblies for debugging

## Agentic Workflows

Unity3D-MCP supports autonomous multi-step workflows via FastMCP sampling:

```python
await unity3d_agentic_workflow(
    goal="Import this VRM file, optimize it for VRChat Excellent rank, set up expressions, and upload"
)
```

The agentic workflow automatically:
1. Detects whether the Unity Editor bridge is available (Hands-In) or not (Hands-Off)
2. Chooses appropriate tools based on the current mode
3. Formulates a multi-step plan using LLM reasoning
4. Executes each step sequentially with validation

## Unity Editor API Reference

### execute_method Parameters
The core method for Unity batch operations:
- `class_name`: Unity C# class (e.g., "MCP.MCPBridge", "VbotSpawner")
- `method_name`: Method to execute
- `parameters`: Dictionary of parameters (logged but may not be passed directly)
- `project_path`: Path to Unity project
- `scene_path`: Optional scene file path
- `wait_for_completion`: Wait for execution to finish (default: True)

### api_execute_method vs execute_method
The API variant supports complex parameter passing through the Unity Editor API plugin, ideal for:
- Spawning robots with full parameter sets
- Scene manipulation with nested objects
- Batch operations across multiple objects
- Physics simulation with data recording

## Troubleshooting

### Common Issues

#### Unity Editor Not Found
If you get "Unity Editor not found":
1. Verify Unity is installed via Unity Hub
2. Set UNITY_EDITOR_PATH environment variable
3. Check that Unity Hub editors.json exists at %APPDATA%/UnityHub/editors.json

#### UniVRM Installation Fails
If UniVRM packages don't install:
1. Check the project is a valid Unity project with manifest.json
2. Ensure Unity is closed during package manifest editing
3. Verify GitHub connectivity for git-based UPM packages
4. Try installing via Unity Package Manager UI instead

#### VRChat Upload Fails
If avatar upload fails:
1. Verify VRChat SDK is installed (both avatars and worlds packages)
2. Check authentication status with check_vrchat_authentication()
3. Ensure avatar meets VRChat performance requirements
4. Check Unity Editor version compatibility (2022.3 LTS recommended)
5. Look for specific errors in the Unity build output

#### OSC Not Working
OSC functionality is now in oscmcp. To use both:
```python
from fastmcp import FastMCP
orchestrator = FastMCP(name="VRChat-Pipeline")
orchestrator.mount(unity3d_mcp, prefix="unity")
orchestrator.mount(osc_mcp, prefix="osc")
```

### Getting Help
- Check the server logs (stderr or unity3d_mcp.log in home directory)
- Use the web dashboard at http://localhost:10830 for monitoring
- Enable JSON logging: set UNITY3D_MCP_LOG_FORMAT=json
- Examine Prometheus metrics if monitoring addon is installed

## API Tool Reference

### Path Operations
The path movement tools provide complete control for robotics and animation:

**api_move_along_path** moves an object along a predefined path with easing:
- Supports straight, bezier, spline, and catmull_rom path types
- Configurable duration, looping, and easing (linear, ease_in, ease_out, ease_in_out)
- Returns animation ID for tracking

**api_follow_path_2d** is optimized for ground-based robots:
- Y-axis is ignored, only XZ plane movement
- look_ahead parameter for smooth rotation toward path direction
- Supports speed control instead of fixed duration

**api_follow_path_3d** provides full spatial movement:
- Bank angle for aircraft-style turning
- Works with any 3D path in world space
- Speed-based movement with look_ahead orientation

**api_stop_path_movement** halts active path following:
- Smooth deceleration option (default 0.5 seconds)
- Immediate stop for emergencies
- Returns final velocity and position

### Path Visualization
Create visual guides for debugging path planning:
```python
await api_create_path_visualization(
    path_points=[{"x": 0, "y": 0, "z": 0}, {"x": 10, "y": 0, "z": 0}],
    path_type="straight",
    visualization_type="line",
    color={"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}
)
```

### Scene Query Tools
**api_get_scene_objects** retrieves the full scene hierarchy:
- Returns object names, positions, rotations, and scales
- Optional filter pattern for targeted queries (e.g., "*Robot*")
- Works with both Hands-In and Hands-Off modes

### Batch Operations
**api_batch_operations** executes multiple operations atomically:
- All operations succeed or fail together
- Returns individual results for each operation
- Great for complex scene setup workflows
- Supports mixed operation types in single call

## Unity Version Compatibility Matrix

### UniVRM Compatibility
| Unity Version | VRM 0.x | VRM 1.0 | Notes |
|--------------|---------|---------|-------|
| 2019.4 LTS | Yes | No | Legacy VRM support only |
| 2020.3 LTS | Yes | Yes | Stable for both VRM versions |
| 2021.3 LTS | Yes | Yes | Recommended for VRM 0.x |
| 2022.3 LTS | Yes | Yes | Recommended for VRM 1.0 |
| 2023.3+ | Partial | Yes | VRM 1.0 preferred |

### VRChat SDK Compatibility
| Unity Version | SDK 3.0 | Notes |
|--------------|---------|-------|
| 2019.4 LTS | Yes | Legacy, limited features |
| 2022.3 LTS | Yes | Recommended by VRChat |
| 2023.3+ | No | Not yet supported |

### Platform Build Module Requirements
- Windows: Included with Unity installation
- macOS: Requires macOS build module (Mac Editor recommended)
- Linux: Requires Linux build module (IL2CPP not supported)
- Android: Requires Android SDK (via Unity Hub or manual)
- iOS: Requires macOS + Xcode + iOS build module
- WebGL: Requires WebGL build module

## Configuration Reference

### Environment Variables Reference
| Variable | Default | Description |
|----------|---------|-------------|
| UNITY_PROJECT_PATH | (empty) | Default Unity project path for all operations |
| UNITY_EDITOR_PATH | (empty) | Explicit path to Unity Editor executable |
| VRCHAT_USERNAME | (empty) | VRChat API username for authentication |
| VRCHAT_PASSWORD | (empty) | VRChat API password for authentication |
| VRCHAT_TOTP_SECRET | (empty) | TOTP secret for auto-generating 2FA codes |
| MCP_BRIDGE_URLS | (empty) | Comma-separated URLs for MCP proxy bridges |
| UNITY3D_MCP_LOG_FORMAT | text | Log format: "text" or "json" |
| UNITY3D_MCP_START_METRICS | true | Enable Prometheus metrics server |
| UNITY3D_MCP_PORT | 10831 | HTTP server port (fleet reserved) |
| UNITY3D_MCP_HOST | 127.0.0.1 | HTTP server bind address |

### Unity Editor Auto-Detection
The server automatically finds Unity installations by:
1. Checking UNITY_EDITOR_PATH environment variable
2. Reading Unity Hub installation database at %APPDATA%/UnityHub/editors.json
3. Scanning C:/Program Files/Unity/Hub/Editor/ for installed versions
4. Checking common installation paths (Program Files, Program Files (x86))
5. When a version is specified, the best match is selected from available installations

### Port Configuration
By default the server uses:
- Port 10830: Web dashboard (Vite dev server)
- Port 10831: HTTP API server
- Port 10835: MCPBridge.cs TCP connection
All ports are within the fleet reserved range (10700-11500).

## Server Lifecycle

### Startup Sequence
1. Configuration loading (environment variables, config file)
2. FastMCP initialization with lifespan
3. Bridge proxy registration (from MCP_BRIDGE_URLS)
4. Skills provider registration
5. Manager initialization (ordered by dependency)
6. Portmanteau tool registration
7. Lifespan startup: metrics server, telemetry
8. Ready for tool calls

### Shutdown Sequence
1. Lifespan cleanup: stop metrics server
2. Active process management: clean up Unity processes
3. Log flush and handler cleanup
4. FastMCP shutdown

### Process Management
- Unity Editor processes are tracked in active_processes dict
- Long-running builds use asyncio subprocess with timeout
- VRChat uploads have 5-minute timeout (configurable)
- Background jobs run via job_queue with proper lifecycle
- All subprocesses are properly terminated on shutdown

## Best Practices

### Project Organization
1. **Version Control**: Always use Git for Unity projects. Add Assets/ to the repository but exclude Library/, Temp/, and Logs/.
2. **Asset Organization**: Use consistent folder structure (Scenes, Scripts, Models, Textures, Materials, Animations, Prefabs, Editor).
3. **Naming Conventions**: Use PascalCase for C# classes and scene objects, snake_case for asset files.
4. **Scene Management**: Keep scenes focused (one scene per level/section). Use additive scene loading for complex worlds.

### Performance Budgets
For social VR avatars, follow these budgets:
- **Polygons**: Keep under 10,000 for Good VRChat rank
- **Materials**: Under 8 material slots, combine where possible
- **Texture Memory**: Under 40 MB total for Good rank
- **Bones**: Under 256 bones for Good rank
- **Draw Calls**: Under 10 for Excellent rank, under 20 for Good

### Workflow Automation
Create efficient workflows by chaining operations:
1. Import VRM -> Setup Animator -> Configure Descriptor -> Validate -> Upload
2. Create Project -> Import Assets -> Build Scene -> Build Project
3. Import Model -> Create Materials -> Setup Lighting -> Test Simulation

### Unity Version Compatibility
- **2022.3 LTS**: Recommended for most projects (VRChat, VRM)
- **2021.3 LTS**: Compatible with older VRChat SDK versions
- **2019.4 LTS**: Required for legacy VRChat SDK2 projects
- Always check package compatibility with the target Unity version before starting a project.

### VRChat Upload Pipeline Best Practices
1. **Always validate** before uploading using vrchat_validate_avatar
2. **Test in Unity** Play mode before building
3. **Build with development** options for debugging
4. **Check performance rank** before public upload (Excellent or Good recommended)
5. **Set appropriate release status**: private for testing, public for sharing
6. **Document avatar features** in the description for users

### Multi-Platform Build Strategy
1. **Primary Platform**: Build and test on your main target platform first
2. **Cross-Platform Testing**: Verify builds on each target platform
3. **Platform-Specific Optimizations**: Apply per-platform texture compression and settings
4. **Build Automation**: Use CI/CD with batch mode for regular builds
5. **Version Tracking**: Tag builds with version numbers in output path

## Scene Management Guide

### Creating Lights
Unity3D-MCP supports three light types with full parameter control:

```python
# Directional light (sun)
await api_execute_method(
    class_name="MCP.MCPBridge",
    method_name="CreateLight",
    parameters={
        "name": "Sun",
        "type": "Directional",
        "color": [1.0, 0.95, 0.8, 1.0],
        "intensity": 1.2,
        "position": {"x": 10, "y": 20, "z": -10},
        "rotation": {"x": 50, "y": -30, "z": 0}
    }
)

# Spot light
await api_execute_method(
    class_name="MCP.MCPBridge",
    method_name="CreateLight",
    parameters={
        "name": "Flashlight",
        "type": "Spot",
        "intensity": 2.0,
        "position": {"x": 0, "y": 2, "z": 0}
    }
)
```

### Creating GameObjects
```python
# Create a primitive GameObject
await unity3d_editor_api(
    action="create_object",
    name="MyCube",
    object_type="GameObject"
)

# Create a camera
await unity3d_editor_api(
    action="create_object",
    name="MainCamera",
    object_type="Camera",
    position=[0, 1, -5]
)
```

## File Format Reference

### Supported Import Formats
| Format | Extension | Notes |
|--------|-----------|-------|
| Unity Package | .unitypackage | Full package with dependencies |
| Filmbox | .fbx | Industry standard, animation support |
| Wavefront | .obj | Simple geometry, no animation |
| GL Transmission | .gltf/.glb | Web-friendly, PBR materials |
| VRM | .vrm | VR avatar format (0.x and 1.0) |

### Supported Export Formats
| Format | Extension | Use Case |
|--------|-----------|----------|
| GLTF | .gltf | Web, Godot, other engines |
| GLB | .glb | Binary GLTF, single file |
| Unity Package | .unitypackage | Sharing with other Unity devs |

### World Labs Formats
| Format | Extension | Type |
|--------|-----------|------|
| Marble Mesh | .obj/.fbx/.glb | Environment geometry |
| Gaussian Splat | .ply/.splat | Photorealistic point cloud |
| Chisel Mesh | .glb | High-detail sculpted mesh |

## Automation Scripts Guide

### CI/CD Pipeline Setup
For automated builds in GitHub Actions:

```yaml
- name: Build Unity Project
  run: |
    $env:UNITY_EDITOR_PATH = "C:\Program Files\Unity\Hub\Editor\2022.3.0f1\Editor\Unity.exe"
    uv run python -c "
    from unity3d_mcp.server import create_app
    app = create_app()
    import asyncio
    asyncio.run(app.build_manager.build_project(
        project_path='D:/Projects/MyGame',
        build_target='StandaloneWindows64',
        output_path='D:/Builds/release'
    ))
    "
```

### Local Dev Workflow Script
```python
# development_workflow.py
"""Automate local Unity development setup."""
import asyncio
from unity3d_mcp.server import create_app

async def setup_dev_environment():
    app = create_app()
    
    # 1. Create project with UniVRM
    result = await app.project_manager.create_project_with_univrm(
        project_name="DevProject",
        project_path="D:/Projects",
        vrm_version="vrm1"
    )
    project_path = result["project_path"]
    
    # 2. Import VRM avatar
    await app.vrm_avatar_manager.import_vrm(
        vrm_path="D:/Templates/base_avatar.vrm",
        project_path=project_path,
        optimize_for_vrchat=True
    )
    
    # 3. Setup animator
    await app.animation_manager.setup_animator(
        avatar_path=f"{project_path}/Assets/Models/template_avatar.vrm",
        include_facial=True
    )
    
    # 4. Get build settings
    settings = await app.build_manager.get_build_settings(project_path)
    print(f"Project ready. Settings: {settings}")

asyncio.run(setup_dev_environment())
```

### Batch Processing Script
For processing multiple assets:

```python
# batch_process.py
"""Process multiple avatars in sequence."""
async def batch_process_avatars():
    app = create_app()
    avatars = ["avatar_a.vrm", "avatar_b.vrm", "avatar_c.vrm"]
    
    for avatar in avatars:
        print(f"Processing {avatar}...")
        
        # Import
        result = await app.vrm_avatar_manager.import_vrm(
            vrm_path=f"D:/Source/{avatar}",
            project_path="D:/Projects/Batch",
            optimize_for_vrchat=True
        )
        
        if result["status"] == "success":
            print(f"  Imported: {avatar}")
        else:
            print(f"  Failed: {avatar} - {result.get('message', '')}")

asyncio.run(batch_process_avatars())
```

## Cross-Platform Reference

### Standalone Windows
- Architecture: x64 (recommended), x86
- Scripting Backend: Mono (development), IL2CPP (release)
- API Compatibility: .NET Standard 2.1
- Compression: LZ4HC for release, LZ4 for development
- Build Output: .exe with Data folder

### Standalone macOS
- Architecture: Universal (Intel + Apple Silicon)
- Scripting Backend: IL2CPP recommended
- Code Signing: Required for distribution
- Build Output: .app bundle

### Standalone Linux
- Architecture: x64
- Scripting Backend: Mono only
- Dependencies: SDL2, Vulkan/OpenGL drivers
- Build Output: .x86_64 executable

### Android
- Architecture: ARM64 (primary), ARMv7 (fallback)
- Minimum API: 22 (Android 5.1), target 31+
- Scripting Backend: IL2CPP
- Texture Compression: ASTC
- Build Output: .apk or .aab (Android App Bundle)

### iOS
- Architecture: ARM64
- Scripting Backend: IL2CPP
- Required: macOS with Xcode
- Provisioning: Apple Developer account required
- Build Output: Xcode project → .ipa

### WebGL
- Compression: Brotli
- Code Optimization: Size (release)
- Memory: 256MB-1GB configuration
- Build Output: HTML + JavaScript + WebAssembly

## Advanced Topics

### Custom Unity Editor Plugins
For advanced integration, create custom C# plugins:
1. Place scripts in Assets/Editor/ folder
2. Use ExecuteInEditMode for runtime editing
3. Expose static methods callable via -executeMethod
4. Use EditorApplication.delayCall for safe Editor API calls
5. Handle serialization and undo for reliability

### VRChat OSC Integration
While OSC control has moved to oscmcp, here is the recommended setup:
```python
from fastmcp import FastMCP
app = FastMCP("VRChat-Stack")
app.mount(unity3d_mcp, prefix="unity")
app.mount(osc_mcp, prefix="osc")
```
This enables workflows like:
1. Upload avatar with Unity3D-MCP
2. Switch to avatar via VRChat API
3. Control parameters with OSC
4. Monitor chatbox messages

### Gaussian Splatting for Environments
Use World Labs Marble with Gaussian Splatting for photorealistic environments:
1. Generate a 3D world with worldlabs-mcp
2. Export as mesh and splat files
3. Import mesh into Unity via import_marble_world
4. Install Gaussian Splatting renderer
5. Import .ply/.splat files for volumetric rendering
6. Combine with traditional geometry for hybrid scenes

### Fleet Pipeline for Game Development
Chain multiple MCP servers for a complete game development pipeline:
1. **worldlabs-mcp**: Generate 3D environments from text/images
2. **unity3d-mcp**: Import environments, add interactions, build game
3. **godot-mcp**: Export to Godot for lightweight web builds
4. **itch-mcp**: Ship builds to itch.io for playtesting
5. **aiwatcher-mcp**: Monitor feedback and bug reports

### Physics Simulation
Run Unity physics simulations via the API:
```python
# Set up scene with objects
await api_batch_operations(operations=[...])

# Run simulation
result = await api_run_simulation(
    duration=5.0,
    record_data=True
)

# Analyze results
for frame in result.get("recorded_data", []):
    print(f"Frame {frame['time']}: {frame['positions']}")
```

Use simulations for:
- Testing robot movements and collisions
- Verifying physics interactions before building
- Generating training data for ML models
- Previewing complex animations

### Performance Monitoring
Track performance across builds:
1. Enable metrics server: UNITY3D_MCP_START_METRICS_SERVER=true
2. Access /metrics endpoint in HTTP mode
3. Integrate with Prometheus for long-term tracking
4. Set up alerts for error rate spikes
5. Use structured logging for post-mortem analysis
