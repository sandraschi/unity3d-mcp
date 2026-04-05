"""
Unity3D MCP Server Implementation

FastMCP 3.2.0+ compliant server with comprehensive Unity 3D automation,
VRM avatar pipeline, and VRChat integration.
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .assets import AssetManager, MaterialManager
from .avatar import AnimationManager, VRMAvatarManager
from .build import BuildManager
from .core import ProjectManager, SceneManager, UnityEditorManager
from .platforms import PlatformManager
from .tools import (
    ImportExportManager,
    MotorManager,
)
from .tools.portmanteau.unity_api_bridge import UnityBridgeClient
from .tools.portmanteau.unity_disk_ops import UnityDiskOps
from .transport import run_server, run_server_async

# Portmanteau managers are imported lazily in _init_portmanteau_managers to avoid circular dependencies
from .utils import ConfigManager, LogManager, UnityPathResolver
from .vrchat import VRChatSDKManager

# NOTE: OSC functionality moved to oscmcp - use server composition for VRChat OSC
from .worldlabs import WorldLabsManager

# Configure structured logging with stderr output (no stdout - reserved for MCP protocol)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),  # JSON output for structured logging
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Setup stderr handler (stdout is reserved for MCP protocol!)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(logging.Formatter("%(message)s"))

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(stderr_handler)

# Get structured logger
logger = structlog.get_logger(__name__)


class Unity3DConfig(BaseModel):
    """Configuration for Unity3D MCP server."""

    unity_editor_path: str = Field(default="", description="Path to Unity Editor executable")
    project_path: str = Field(default="", description="Default Unity project path")
    auto_detect_unity: bool = Field(default=True, description="Auto-detect Unity Editor installation")
    enable_http: bool = Field(default=True, description="Enable HTTP interface alongside stdio")
    http_port: int = Field(default=10831, description="HTTP server port (fleet 10831 backend per WEBAPP_PORTS)")
    log_level: str = Field(default="INFO", description="Logging level")


@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP):
    """Server lifespan for startup and cleanup.

    Handles Unity3D MCP server initialization and shutdown lifecycle.
    """
    logger.info("Unity3D MCP server starting up", version="1.0.0")
    yield
    logger.info("Unity3D MCP server shutting down")


class Unity3DMCP:
    """Unity3D MCP Server with comprehensive automation capabilities."""

    def __init__(self, config: Optional[Unity3DConfig] = None):
        """Initialize Unity3D MCP server."""
        self.config = config or Unity3DConfig()

        # Initialize FastMCP with lifespan (FastMCP 3.2.0+)
        self.app = FastMCP(name="Unity3D-MCP", version="1.0.0", lifespan=server_lifespan)

        # Initialize managers
        self._init_managers()

        # Register all tools
        self._register_tools()

        logger.info(
            "Unity3D MCP server initialized",
            unity_path=self.config.unity_editor_path,
            project_path=self.config.project_path,
        )

    def _init_managers(self):
        """Initialize all component managers."""
        self.unity_editor = UnityEditorManager(self.config)
        self.project_manager = ProjectManager(self.config)
        self.scene_manager = SceneManager(self.config)
        self.vrm_avatar = VRMAvatarManager(self.config)
        self.animation = AnimationManager(self.config)
        self.asset_manager = AssetManager(self.config)
        self.material_manager = MaterialManager(self.config)
        self.build_manager = BuildManager(self.config)
        self.platform_manager = PlatformManager(self.config)
        self.vrchat_sdk = VRChatSDKManager(self.config)
        # OSC removed - use oscmcp for OSC/MIDI transport
        self.worldlabs = WorldLabsManager(self.config)
        self.motor_manager = MotorManager(self.config)
        self.import_export_manager = ImportExportManager(self.config)
        self.vrm_avatar_manager = VRMAvatarManager(self.config)
        self.platforms = PlatformManager(self.config)
        self.path_resolver = UnityPathResolver(self.config)
        self.config_manager = ConfigManager(self.config)
        self.log_manager = LogManager(self.config)

        # Initialize portmanteau tool managers
        self._init_portmanteau_managers()

    def _init_portmanteau_managers(self):
        """Initialize portmanteau tool managers."""
        from .tools.portmanteau import (
            PlatformToolManager,
            UnityAPIToolManager,
            UnityAssetToolManager,
            UnityAvatarToolManager,
            UnityBuildToolManager,
            UnityCoreToolManager,
            UnitySceneToolManager,
            VRChatToolManager,
            WorldLabsToolManager,
        )

        self.unity_core_manager = UnityCoreToolManager(self.app, self.unity_editor, self.project_manager)
        self.unity_scene_manager = UnitySceneToolManager(self.app, self.scene_manager)
        self.unity_avatar_manager = UnityAvatarToolManager(self.app, self.vrm_avatar, self.animation)
        self.unity_asset_manager = UnityAssetToolManager(self.app, self.asset_manager)
        self.unity_build_manager = UnityBuildToolManager(self.app, self.build_manager)
        self.vrchat_manager = VRChatToolManager(self.app, self.vrchat_sdk, self.config)
        self.worldlabs_manager = WorldLabsToolManager(self.app, self.worldlabs)
        self.platform_manager = PlatformToolManager(self.app, self.platforms)
        self.unity_api_manager = UnityAPIToolManager(self.app)

    def _register_tools(self):
        """Register all MCP tools using portmanteau pattern."""

        # Register portmanteau tool managers
        self.unity_core_manager.register_tools()
        self.unity_scene_manager.register_tools()
        self.unity_avatar_manager.register_tools()
        self.unity_asset_manager.register_tools()
        self.unity_build_manager.register_tools()
        self.vrchat_manager.register_tools()
        self.worldlabs_manager.register_tools()
        self.platform_manager.register_tools()
        self.unity_api_manager.register_tools()

        logger.info("Portmanteau tools registered successfully")

        @self.app.tool
        async def list_vr_platforms() -> dict:
            """List all supported social VR platforms.

            Returns information about all supported social VR platforms including
            VRChat, ChilloutVR, Resonite, and Cluster with their requirements.

            Returns:
                Dictionary containing:
                - success: Boolean indicating query succeeded
                - platforms: List of platform dictionaries with:
                  - name: Platform name
                  - engine: Game engine required
                  - avatar_format: Avatar file format
                  - sdk_required: Whether SDK installation is needed
                  - sdk_name: SDK package name
                  - unity_versions: List of compatible Unity versions
                  - documentation_url: Link to platform documentation
                - error: Error message if failed

            Examples:
                # List all platforms
                list_vr_platforms()

                # Returns platforms: VRChat, ChilloutVR, Resonite, Cluster
            """
            return await self.platforms.list_supported_platforms()

        @self.app.tool
        async def check_platform_sdk(
            platform: str,
            project_path: str,
        ) -> Dict[str, Any]:
            """Check if a social VR platform SDK is installed.

            Verifies whether SDK for specified platform (VRChat, ChilloutVR, Cluster)
            is installed in Unity project.

            Args:
                platform: Platform name ("vrchat", "chilloutvr", "cluster", "resonite")
                project_path: Unity project path to check

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - platform: Platform name checked
                - installed: Boolean indicating if SDK is installed
                - sdk_version: SDK version if installed
                - package_path: Path to SDK package
                - error: Error message if failed

            Examples:
                # Check VRChat SDK
                check_platform_sdk("vrchat", "D:/Projects/VRChat")

                # Check ChilloutVR CCK
                check_platform_sdk("chilloutvr", "D:/Projects/CVR")
            """
            return await self.platforms.check_platform_sdk(platform, project_path)

        # ChilloutVR Tools
        @self.app.tool
        async def check_cck_installed(project_path: str) -> Dict[str, Any]:
            """Check if ChilloutVR CCK (Content Creation Kit) is installed.

            Verifies whether ChilloutVR CCK is present in Unity project for
            creating avatars and worlds for ChilloutVR platform.

            Args:
                project_path: Unity project path to check

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - installed: Boolean indicating if CCK is installed
                - cck_version: CCK version if installed
                - package_path: Path to CCK package
                - error: Error message if failed

            Examples:
                # Check CCK
                check_cck_installed("D:/Projects/ChilloutVR")
            """
            return await self.platforms.chillout.check_cck_installed(project_path)

        @self.app.tool
        async def setup_cvr_avatar(
            avatar_object: str,
            project_path: str,
            eye_height: float = 1.6,
        ) -> Dict[str, Any]:
            """Setup CVRAvatar component for ChilloutVR.

            Configures avatar GameObject with CVRAvatar component required
            for ChilloutVR avatar upload.

            Args:
                avatar_object: Path to avatar GameObject in scene
                project_path: Unity project path
                eye_height: Avatar eye height in meters (default: 1.6)

            Returns:
                Dictionary containing:
                - success: Boolean indicating setup succeeded
                - avatar_path: Path to configured avatar
                - eye_height: Configured eye height
                - components_added: List of components added
                - error: Error message if failed

            Examples:
                # Setup avatar with default eye height
                setup_cvr_avatar(
                    avatar_object="MyAvatar",
                    project_path="D:/Projects/ChilloutVR"
                )

                # Custom eye height
                setup_cvr_avatar(
                    avatar_object="TallAvatar",
                    project_path="D:/CVR",
                    eye_height=1.8
                )
            """
            return await self.platforms.chillout.setup_cvr_avatar(avatar_object, project_path, eye_height)

        @self.app.tool
        async def validate_for_chilloutvr(
            avatar_name: str,
            project_path: str,
        ) -> Dict[str, Any]:
            """Validate avatar for ChilloutVR upload.

            Checks avatar against ChilloutVR technical requirements and
            provides validation report.

            Args:
                avatar_name: Name of avatar to validate
                project_path: Unity project path

            Returns:
                Dictionary containing:
                - success: Boolean indicating validation completed
                - valid: Boolean indicating if avatar passes checks
                - polygon_count: Total triangle count
                - validation_errors: List of blocking errors
                - validation_warnings: List of non-blocking warnings
                - suggestions: List of optimization suggestions
                - error: Error message if failed

            Examples:
                # Validate avatar
                validate_for_chilloutvr(
                    avatar_name="MyAvatar",
                    project_path="D:/Projects/ChilloutVR"
                )
            """
            return await self.platforms.chillout.validate_for_chillout(avatar_name, project_path)

        # Resonite Tools
        @self.app.tool
        async def prepare_for_resonite(
            model_path: str,
            optimize: bool = True,
        ) -> Dict[str, Any]:
            """Prepare model for Resonite import (VRM/GLB direct import).

            Prepares VRM or GLB model for direct import into Resonite social VR.
            No Unity project required - Resonite imports VRM/GLB directly.

            Args:
                model_path: Path to .vrm or .glb file
                optimize: Apply optimization for Resonite (texture compression, LOD)

            Returns:
                Dictionary containing:
                - success: Boolean indicating preparation succeeded
                - model_path: Path to prepared model
                - format: Model format ("vrm" or "glb")
                - polygon_count: Triangle count
                - texture_count: Number of textures
                - optimization_report: Dict with optimization details (if optimize=True)
                - resonite_compatible: Boolean indicating Resonite compatibility
                - error: Error message if failed

            Examples:
                # Prepare VRM for Resonite
                prepare_for_resonite("D:/Avatars/model.vrm")

                # Prepare without optimization
                prepare_for_resonite(
                    model_path="D:/Models/character.glb",
                    optimize=False
                )
            """
            return await self.platforms.resonite.prepare_for_resonite(model_path, optimize)

        @self.app.tool
        async def check_resonite_compatibility(model_path: str) -> Dict[str, Any]:
            """Check if model is compatible with Resonite.

            Verifies whether VRM or GLB model meets Resonite import requirements.

            Args:
                model_path: Path to .vrm or .glb file

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - compatible: Boolean indicating Resonite compatibility
                - model_format: Format ("vrm" or "glb")
                - compatibility_issues: List of compatibility issues
                - warnings: List of non-blocking warnings
                - suggestions: List of optimization suggestions
                - error: Error message if failed

            Examples:
                # Check VRM compatibility
                check_resonite_compatibility("D:/Avatars/model.vrm")

                # Check GLB compatibility
                check_resonite_compatibility("D:/Models/character.glb")
            """
            return await self.platforms.resonite.check_resonite_compatibility(model_path)

        # Cluster Tools
        @self.app.tool
        async def check_cluster_kit(project_path: str) -> Dict[str, Any]:
            """Check if Cluster Creator Kit is installed.

            Verifies whether Cluster Creator Kit (Japanese social VR platform)
            is present in Unity project.

            Args:
                project_path: Unity project path to check

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - installed: Boolean indicating if Creator Kit is installed
                - kit_version: Kit version if installed
                - package_path: Path to kit package
                - error: Error message if failed

            Examples:
                # Check Cluster Kit
                check_cluster_kit("D:/Projects/Cluster")
            """
            return await self.platforms.cluster.check_cluster_kit_installed(project_path)

        @self.app.tool
        async def prepare_for_cluster(
            avatar_path: str,
            project_path: str,
        ) -> Dict[str, Any]:
            """Prepare avatar for Cluster upload.

            Configures VRM avatar for upload to Cluster (Japanese social VR platform).
            Cluster uses VRM format natively.

            Args:
                avatar_path: Path to avatar in Unity project
                project_path: Unity project path

            Returns:
                Dictionary containing:
                - success: Boolean indicating preparation succeeded
                - avatar_path: Path to prepared avatar
                - vrm_export_path: Path to exported VRM file
                - polygon_count: Triangle count
                - cluster_compatible: Boolean indicating Cluster compatibility
                - validation_report: Dict with validation details
                - error: Error message if failed

            Examples:
                # Prepare avatar for Cluster
                prepare_for_cluster(
                    avatar_path="Assets/Avatars/MyAvatar.prefab",
                    project_path="D:/Projects/Cluster"
                )
            """
            return await self.platforms.cluster.prepare_for_cluster(avatar_path, project_path)

        @self.app.tool
        async def api_execute_method(
            class_name: str,
            method_name: str,
            parameters: Optional[Dict[str, Any]] = None,
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
            wait_for_completion: bool = True,
        ) -> Dict[str, Any]:
            """Execute Unity Editor method with full parameter support via API.

            Uses Unity Editor API to execute methods with complex parameters,
            unlike CLI which has parameter limitations. Perfect for robotics
            spawning, scene manipulation, and advanced Unity operations.

            Args:
                class_name: Unity class name containing the method (e.g., "VbotSpawner")
                method_name: Method name to execute (e.g., "SpawnRobot")
                parameters: Dictionary of parameters to pass to the method
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)
                wait_for_completion: Wait for method completion before returning

            Returns:
                Dictionary containing:
                - success: Boolean indicating execution succeeded
                - result: Method return value (if any)
                - execution_time: Time taken in seconds
                - error: Error message if failed

            Examples:
                # Spawn robot with full parameters (CLI cannot do this)
                api_execute_method(
                    class_name="VbotSpawner",
                    method_name="SpawnRobot",
                    parameters={
                        "robotId": "scout_01",
                        "robotType": "scout",
                        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                        "scale": 1.0
                    }
                )

                # Manipulate scene objects
                api_execute_method(
                    class_name="SceneManager",
                    method_name="MoveObject",
                    parameters={
                        "objectName": "Robot",
                        "targetPosition": {"x": 5.0, "y": 0.0, "z": 5.0}
                    }
                )
            """
            return await self._api_execute_method(
                class_name,
                method_name,
                parameters,
                project_path,
                scene_path,
                wait_for_completion,
            )

        @self.app.tool
        async def api_get_scene_objects(
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
            object_filter: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Get all objects in Unity scene via API.

            Retrieves complete list of scene objects with their properties,
            transforms, and components. Much more detailed than CLI approaches.

            Args:
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)
                object_filter: Optional filter pattern (e.g., "*Robot*" for robot objects)

            Returns:
                Dictionary containing:
                - success: Boolean indicating query succeeded
                - objects: List of scene objects with properties
                - scene_name: Name of queried scene
                - object_count: Total number of objects
                - error: Error message if failed

            Examples:
                # Get all robots in scene
                api_get_scene_objects(object_filter="*Robot*")

                # Get all objects
                api_get_scene_objects()
            """
            return await self._api_get_scene_objects(project_path, scene_path, object_filter)

        @self.app.tool
        async def api_modify_object(
            object_name: str,
            modifications: Dict[str, Any],
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Modify Unity scene object properties via API.

            Directly modify object transforms, components, and properties
            using Unity Editor API. Supports complex modifications that
            CLI cannot handle.

            Args:
                object_name: Name of object to modify
                modifications: Dictionary of modifications to apply
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating modification succeeded
                - object_name: Name of modified object
                - modifications_applied: List of applied modifications
                - error: Error message if failed

            Examples:
                # Move robot to new position
                api_modify_object(
                    object_name="ScoutRobot",
                    modifications={
                        "transform.position": {"x": 10.0, "y": 0.0, "z": 5.0},
                        "transform.rotation": {"x": 0.0, "y": 45.0, "z": 0.0}
                    }
                )

                # Change material color
                api_modify_object(
                    object_name="RobotBody",
                    modifications={
                        "renderer.material.color": {"r": 1.0, "g": 0.0, "b": 0.0}
                    }
                )
            """
            return await self._api_modify_object(object_name, modifications, project_path, scene_path)

        @self.app.tool
        async def api_create_prefab(
            object_name: str,
            prefab_name: str,
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Create Unity prefab from scene object via API.

            Uses Unity Editor API to create prefabs with proper references,
            components, and nested object hierarchies. CLI cannot handle
            complex prefab creation.

            Args:
                object_name: Name of scene object to convert to prefab
                prefab_name: Name for the new prefab
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating prefab creation succeeded
                - prefab_path: Path to created prefab
                - object_name: Original scene object name
                - prefab_name: Name of created prefab
                - error: Error message if failed

            Examples:
                # Create robot prefab
                api_create_prefab(
                    object_name="ScoutRobotInstance",
                    prefab_name="ScoutRobot"
                )
            """
            return await self._api_create_prefab(object_name, prefab_name, project_path, scene_path)

        @self.app.tool
        async def api_run_simulation(
            duration: float,
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
            record_data: bool = False,
        ) -> Dict[str, Any]:
            """Run Unity physics simulation via API.

            Executes Unity physics simulation for specified duration,
            optionally recording object movements and collisions.
            Perfect for testing robot movements and interactions.

            Args:
                duration: Simulation duration in seconds
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)
                record_data: Record object positions/transforms during simulation

            Returns:
                Dictionary containing:
                - success: Boolean indicating simulation succeeded
                - duration: Actual simulation duration
                - recorded_data: Position/transform data if record_data=True
                - collision_count: Number of collisions detected
                - error: Error message if failed

            Examples:
                # Run 5-second simulation
                api_run_simulation(duration=5.0, record_data=True)

                # Quick physics test
                api_run_simulation(duration=1.0)
            """
            return await self._api_run_simulation(duration, project_path, scene_path, record_data)

        @self.app.tool
        async def api_batch_operations(
            operations: List[Dict[str, Any]],
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Execute multiple Unity operations in batch via API.

            Performs multiple Unity Editor operations in a single API call,
            ensuring atomicity and efficiency. Essential for complex robotics
            setup workflows.

            Args:
                operations: List of operation dictionaries to execute
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating all operations succeeded
                - results: List of individual operation results
                - operation_count: Number of operations executed
                - total_time: Total execution time
                - error: Error message if failed

            Examples:
                # Spawn multiple robots
                api_batch_operations([
                    {
                        "type": "execute_method",
                        "class_name": "VbotSpawner",
                        "method_name": "SpawnRobot",
                        "parameters": {"robotId": "robot1", "robotType": "scout"}
                    },
                    {
                        "type": "execute_method",
                        "class_name": "VbotSpawner",
                        "method_name": "SpawnRobot",
                        "parameters": {"robotId": "robot2", "robotType": "scout"}
                    }
                ])
            """
            return await self._api_batch_operations(operations, project_path, scene_path)

        @self.app.tool
        async def api_move_along_path(
            object_name: str,
            path_type: str,
            path_points: List[Dict[str, float]],
            duration: float = 1.0,
            loop: bool = False,
            ease_type: str = "linear",
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Move object along a path (straight, spline, 2D, 3D) via Unity Editor API.

            Animates an object along a defined path using Unity's animation system.
            Supports straight lines, bezier curves, and custom spline paths in both 2D and 3D.

            Args:
                object_name: Name of the object to move
                path_type: Path type ("straight", "bezier", "spline", "catmull_rom")
                path_points: List of points defining the path [{"x": 0.0, "y": 0.0, "z": 0.0}, ...]
                duration: Movement duration in seconds (default: 1.0)
                loop: Whether to loop the path animation (default: False)
                ease_type: Easing function ("linear", "ease_in", "ease_out", "ease_in_out")
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating path movement started
                - object_name: Object being moved
                - path_type: Type of path used
                - duration: Animation duration
                - points_count: Number of path points
                - animation_id: ID for tracking the animation
                - error: Error message if failed

            Examples:
                # Move robot along straight path
                api_move_along_path(
                    object_name="ScoutRobot",
                    path_type="straight",
                    path_points=[
                        {"x": 0.0, "y": 0.0, "z": 0.0},
                        {"x": 5.0, "y": 0.0, "z": 0.0},
                        {"x": 5.0, "y": 0.0, "z": 5.0}
                    ],
                    duration=3.0
                )

                # Move along smooth spline path
                api_move_along_path(
                    object_name="Drone",
                    path_type="catmull_rom",
                    path_points=[
                        {"x": 0.0, "y": 2.0, "z": 0.0},
                        {"x": 2.0, "y": 3.0, "z": 1.0},
                        {"x": 4.0, "y": 2.0, "z": 2.0},
                        {"x": 6.0, "y": 1.0, "z": 1.0}
                    ],
                    duration=5.0,
                    ease_type="ease_in_out"
                )
            """
            return await self._api_move_along_path(
                object_name,
                path_type,
                path_points,
                duration,
                loop,
                ease_type,
                project_path,
                scene_path,
            )

        @self.app.tool
        async def api_create_path_visualization(
            path_points: List[Dict[str, float]],
            path_type: str = "straight",
            visualization_type: str = "line",
            color: Optional[Dict[str, float]] = None,
            thickness: float = 0.1,
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Create visual representation of a path in Unity scene.

            Generates visual aids (lines, curves, waypoints) to show the path
            that objects will follow. Useful for debugging and planning robot movements.

            Args:
                path_points: List of points defining the path
                path_type: Path type ("straight", "bezier", "spline", "catmull_rom")
                visualization_type: How to visualize ("line", "dotted", "waypoints", "full")
                color: Path color {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}
                thickness: Line thickness (default: 0.1)
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating visualization created
                - visualization_object: Name of created visualization object
                - path_type: Type of path visualized
                - points_count: Number of path points
                - error: Error message if failed

            Examples:
                # Create red path visualization
                api_create_path_visualization(
                    path_points=[
                        {"x": 0.0, "y": 0.0, "z": 0.0},
                        {"x": 5.0, "y": 0.0, "z": 0.0}
                    ],
                    color={"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0},
                    thickness=0.05
                )
            """
            return await self._api_create_path_visualization(
                path_points,
                path_type,
                visualization_type,
                color,
                thickness,
                project_path,
                scene_path,
            )

        @self.app.tool
        async def api_follow_path_2d(
            object_name: str,
            path_points: List[Dict[str, float]],
            speed: float = 1.0,
            look_ahead: float = 0.5,
            smooth_rotation: bool = True,
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Move object along 2D path with forward-looking behavior.

            Specialized for 2D movement where objects need to look ahead
            and rotate smoothly to follow the path direction.

            Args:
                object_name: Name of the object to move
                path_points: List of 2D points [{"x": 0.0, "z": 0.0}, ...] (Y ignored)
                speed: Movement speed (units per second)
                look_ahead: Distance to look ahead for rotation (default: 0.5)
                smooth_rotation: Whether to smoothly rotate towards movement direction
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating path following started
                - object_name: Object following the path
                - path_length: Total length of the path
                - estimated_duration: Estimated time to complete path
                - error: Error message if failed

            Examples:
                # 2D robot navigation
                api_follow_path_2d(
                    object_name="GroundRobot",
                    path_points=[
                        {"x": 0.0, "z": 0.0},
                        {"x": 10.0, "z": 0.0},
                        {"x": 10.0, "z": 10.0},
                        {"x": 0.0, "z": 10.0}
                    ],
                    speed=2.0,
                    look_ahead=1.0
                )
            """
            return await self._api_follow_path_2d(
                object_name,
                path_points,
                speed,
                look_ahead,
                smooth_rotation,
                project_path,
                scene_path,
            )

        @self.app.tool
        async def api_follow_path_3d(
            object_name: str,
            path_points: List[Dict[str, float]],
            speed: float = 1.0,
            bank_angle: float = 0.0,
            look_ahead: float = 1.0,
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Move object along 3D path with banking and advanced controls.

            Full 3D path following with banking angles for aircraft/drone-like
            movement. Objects automatically bank into turns and maintain proper orientation.

            Args:
                object_name: Name of the object to move
                path_points: List of 3D points [{"x": 0.0, "y": 1.0, "z": 0.0}, ...]
                speed: Movement speed (units per second)
                bank_angle: Maximum banking angle in degrees (default: 0.0 for no banking)
                look_ahead: Distance to look ahead for orientation (default: 1.0)
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating 3D path following started
                - object_name: Object following the path
                - path_length: Total 3D path length
                - max_elevation: Highest point on path
                - banking_enabled: Whether banking is active
                - error: Error message if failed

            Examples:
                # 3D drone flight path
                api_follow_path_3d(
                    object_name="Drone",
                    path_points=[
                        {"x": 0.0, "y": 1.0, "z": 0.0},
                        {"x": 5.0, "y": 3.0, "z": 2.0},
                        {"x": 10.0, "y": 2.0, "z": 5.0},
                        {"x": 15.0, "y": 1.0, "z": 3.0}
                    ],
                    speed=3.0,
                    bank_angle=30.0,
                    look_ahead=2.0
                )
            """
            return await self._api_follow_path_3d(
                object_name,
                path_points,
                speed,
                bank_angle,
                look_ahead,
                project_path,
                scene_path,
            )

        @self.app.tool
        async def api_stop_path_movement(
            object_name: str,
            decelerate: bool = True,
            deceleration_time: float = 0.5,
            project_path: Optional[str] = None,
            scene_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Stop object path movement with optional deceleration.

            Halts any ongoing path movement for an object, either immediately
            or with smooth deceleration.

            Args:
                object_name: Name of the object to stop
                decelerate: Whether to decelerate smoothly (default: True)
                deceleration_time: Time to decelerate in seconds (default: 0.5)
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating movement stopped
                - object_name: Object that was stopped
                - deceleration_applied: Whether smooth deceleration was used
                - final_velocity: Final velocity when stopped
                - error: Error message if failed

            Examples:
                # Emergency stop
                api_stop_path_movement("Robot", decelerate=False)

                # Smooth stop
                api_stop_path_movement("Drone", decelerate=True, deceleration_time=1.0)
            """
            return await self._api_stop_path_movement(
                object_name, decelerate, deceleration_time, project_path, scene_path
            )

    # Unity Editor API Implementation Methods
    async def _api_execute_method(
        self,
        class_name: str,
        method_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        project_path: Optional[str] = None,
        scene_path: Optional[str] = None,
        wait_for_completion: bool = True,
    ) -> Dict[str, Any]:
        """Execute Unity Editor method via API.

        This would connect to Unity Editor via API (e.g., Unity Hub API,
        or custom Unity Editor plugin) to execute methods with full parameter support.
        """
        # TODO: Implement Unity Editor API connection
        # This would require:
        # 1. Unity Editor with custom API plugin
        # 2. Connection to running Unity instance
        # 3. Method execution with parameter serialization

        return {
            "success": False,
            "error": "Unity Editor API not yet implemented - requires Unity plugin development",
            "class_name": class_name,
            "method_name": method_name,
            "parameters": parameters,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_get_scene_objects(
        self,
        project_path: Optional[str] = None,
        scene_path: Optional[str] = None,
        object_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get scene objects via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_modify_object(
        self,
        object_name: str,
        modifications: Dict[str, Any],
        project_path: Optional[str] = None,
        scene_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modify scene object via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_create_prefab(
        self,
        object_name: str,
        prefab_name: str,
        project_path: Optional[str] = None,
        scene_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create prefab via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_run_simulation(
        self,
        duration: float,
        project_path: Optional[str] = None,
        scene_path: Optional[str] = None,
        record_data: bool = False,
    ) -> Dict[str, Any]:
        """Run physics simulation via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_batch_operations(
        self,
        operations: List[Dict[str, Any]],
        project_path: Optional[str] = None,
        scene_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute batch operations via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_move_along_path(
        self,
        object_name: str,
        path_type: str,
        path_points: List[Dict[str, float]],
        duration: float,
        loop: bool,
        ease_type: str,
        project_path: Optional[str],
        scene_path: Optional[str],
    ) -> Dict[str, Any]:
        """Move object along path via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "path_type": path_type,
            "points_count": len(path_points),
            "duration": duration,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_create_path_visualization(
        self,
        path_points: List[Dict[str, float]],
        path_type: str,
        visualization_type: str,
        color: Optional[Dict[str, float]],
        thickness: float,
        project_path: Optional[str],
        scene_path: Optional[str],
    ) -> Dict[str, Any]:
        """Create path visualization via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "path_type": path_type,
            "visualization_type": visualization_type,
            "points_count": len(path_points),
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_follow_path_2d(
        self,
        object_name: str,
        path_points: List[Dict[str, float]],
        speed: float,
        look_ahead: float,
        smooth_rotation: bool,
        project_path: Optional[str],
        scene_path: Optional[str],
    ) -> Dict[str, Any]:
        """Follow 2D path via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "path_length": len(path_points),
            "speed": speed,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_follow_path_3d(
        self,
        object_name: str,
        path_points: List[Dict[str, float]],
        speed: float,
        bank_angle: float,
        look_ahead: float,
        project_path: Optional[str],
        scene_path: Optional[str],
    ) -> Dict[str, Any]:
        """Follow 3D path with banking via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "path_length": len(path_points),
            "banking_enabled": bank_angle > 0,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_stop_path_movement(
        self,
        object_name: str,
        decelerate: bool,
        deceleration_time: float,
        project_path: Optional[str],
        scene_path: Optional[str],
    ) -> Dict[str, Any]:
        """Stop path movement via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "deceleration_applied": decelerate,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def run_stdio(self):
        """Run server in stdio mode."""
        # Updated for fastmcp 3.2.0+
        await run_server_async(self.app, server_name="unity3d-mcp")

    async def run_http(self, host: str = "0.0.0.0", port: int = 10831):
        """Run server in HTTP mode."""
        # Updated for fastmcp 3.2.0+
        try:
            # Use unified transport with http mode
            from argparse import Namespace

            args = Namespace(http=True, stdio=False, sse=False, host=host, port=port, path="/mcp", debug=False)
            await run_server_async(self.app, args=args, server_name="unity3d-mcp")
        except Exception as e:
            logger.error("Failed to run HTTP mode", error=str(e))
            raise

    async def run_dual(self):
        """Run server in dual stdio + HTTP mode."""
        # Dual mode might not be supported in the same way.
        # Fallback to stdio for now to ensure basic functionality.
        logger.warning("Dual mode not fully supported - falling back to stdio")
        run_server(self, server_name="unity3d-mcp")


def create_app(config: Optional[Unity3DConfig] = None) -> Unity3DMCP:
    """Create Unity3D MCP application instance."""
    return Unity3DMCP(config)


# --- SOTA Global App Exposure for Uvicorn (FastMCP 3.2.0+) ---
# This allows 'uvicorn unity3d_mcp.server:app' to work out of the box.
server_instance = create_app()
app = server_instance.app  # The FastMCP instance is an ASGI-compatible app


# --- SOTA 2026 Skills & Instruction Discovery (FastMCP 3.2.0+) ---


@app.resource("resource://unity3d/skills/{skill_name}")
async def get_unity_skill(skill_name: str) -> str:
    """Retrieve expert instructions for a specific Unity3D skill.

    Args:
        skill_name: The name of the skill to retrieve (e.g., 'unity-editor-automation')
    """
    skill_path = Path(__file__).parent.parent.parent / "skills" / skill_name / "SKILL.md"
    if not skill_path.exists():
        return f"Error: Skill '{skill_name}' not found at {skill_path}"

    return skill_path.read_text(encoding="utf-8")


@app.resource("resource://unity3d/skills/list")
async def list_unity_skills() -> str:
    """List all available Unity3D skills for instruction discovery."""
    skills_dir = Path(__file__).parent.parent.parent / "skills"
    if not skills_dir.exists():
        return "No skills found in the skills directory."

    skills = []
    for skill_subdir in skills_dir.iterdir():
        if skill_subdir.is_dir() and (skill_subdir / "SKILL.md").exists():
            skills.append(skill_subdir.name)

    return "Available Unity3D Skills:\n- " + "\n- ".join(skills)


# --- SOTA 2026 Prompts (FastMCP 3.2.0+) ---


@app.prompt()
async def unity_setup_workflow(project_name: str = "MyNewProject") -> str:
    """Standardized prompt for initializing a new Unity project with SOTA standards."""
    return f"""Launch and initialize a new Unity project named '{project_name}'.
Follow these steps:
1. Create the project directory using `create_unity_project`.
2. Launch the Unity Editor via `launch_unity_editor`.
3. Set the build target to 'StandaloneWindows64' if applicable.
4. Verify project health after initialization.
"""


@app.prompt()
async def vrc_avatar_workflow(avatar_name: str, vrm_path: str) -> str:
    """Step-by-step instructions for the VRM-to-VRChat avatar optimization pipeline."""
    return f"""Optimize the VRM avatar '{avatar_name}' from '{vrm_path}' for VRChat.
Workflow:
1. Import the VRM asset using `import_vrm_avatar`.
2. Apply VRChat-specific optimizations via `optimize_for_vrchat`.
3. Validate the avatar performance using `vrchat_validate_avatar`.
4. Report any validation errors that might block the upload.
"""


# --- SOTA 2026 Agentic Workflow (FastMCP 3.2.0+ SEP-1577) ---

# --- SOTA 2026 Dual-Mode Tools (Hands-In / Hands-Off) ---

_bridge_client = UnityBridgeClient()


@app.tool()
async def unity3d_bridge_status() -> Dict[str, Any]:
    """Check if the Unity Editor Bridge (MCPBridge.cs) is alive and reachable.

    Returns:
        A dictionary with 'status' (connected/disconnected) and 'port'.
    """
    alive = await _bridge_client.is_alive()
    return {
        "status": "connected" if alive else "disconnected",
        "port": 10835,
        "bridge_script": "MCPBridge.cs",
        "instruction": "If disconnected, ensure MCPBridge.cs is in your Unity Assets/Editor folder.",
    }


@app.tool()
async def unity3d_editor_api(action: str, target: str = None, **kwargs) -> Dict[str, Any]:
    """[Hands-In] Execute a real-time command in an active Unity Editor session.

    Args:
        action: The action to perform (ping, get_hierarchy, transform_object, create_object, delete_object).
        target: The name or InstanceID of the target GameObject.
        **kwargs: Additional parameters (position, rotation, name, type).
    """
    return await _bridge_client.execute_command(action, target=target, **kwargs)


@app.tool()
async def unity3d_disk_api(operation: str, file_path: str, **kwargs) -> Dict[str, Any]:
    """[Hands-Off] Manipulate Unity project assets directly on disk without Unity running.

    Args:
        operation: The operation (inspect_file, list_textures, modify_yaml).
        file_path: Absolute path to the .unity, .prefab, or .asset file.
        **kwargs: component_type, property_name, new_value for modify_yaml.
    """
    if operation == "inspect_file":
        return UnityDiskOps.inspect_file(file_path)
    elif operation == "list_textures":
        return {"textures": UnityDiskOps.list_textures(file_path)}
    elif operation == "modify_yaml":
        return UnityDiskOps.modify_yaml_property(
            file_path, kwargs.get("component_type"), kwargs.get("property_name"), kwargs.get("new_value")
        )
    return {"error": f"Unknown operation: {operation}"}


@app.tool()
async def unity3d_agentic_workflow(ctx: Any, goal: str) -> str:
    """Perform an autonomous Unity3D workflow by orchestrating multiple tools using AI sampling.

    This tool is a SEP-1577 compliant agentic entry point. It leverages dual-mode capabilities:
    - Hands-In: Real-time Editor control if bridge is active.
    - Hands-Off: Direct disk access via UnityPy if Unity is closed.

    Args:
        ctx: Unified FastMCP Context (injected by server).
        goal: The high-level Unity or VRChat objective to achieve.
    """
    logger.info("Executing agentic workflow", goal=goal)

    bridge = await _bridge_client.is_alive()
    mode = "Hands-In (Live Session)" if bridge else "Hands-Off (Disk Operations)"

    # Define the mission instructions for sampling
    mission_instructions = f"""You are the Unity3D-MCP Autonomous Orchestrator.
Your goal is: {goal}
Current Mode: {mode}

Available tool categories:
- core: project/scene management
- dual-mode:
    * unity3d_editor_api: Real-time session control (requires bridge)
    * unity3d_disk_api: UnityPy disk manipulation (works without Unity)
- avatar: VRM/Unity avatar rigging
- assets: import/export, package management
- build: multi-platform builds
- vrchat: SDK interaction, validation, upload
- worldlabs: Marble/Chisel integration

Formulate a multi-step plan using the available tools.
If Mode is '{mode}', prioritize tools that work in this environment.
Always start by checking if the project path is valid.
"""

    try:
        # Perform autonomous sampling (SEP-1577 Pattern)
        # Note: In production, we would dynamically pull the tool descriptions from self.app.list_tools()
        result = await ctx.sample(
            messages=[{"role": "user", "content": mission_instructions}], max_tokens=2000, temperature=0.0
        )

        logger.info("Agentic workflow completed successfully")
        return f"Unity3D Agentic Workflow Result for '{goal}':\n\n{result.content}"

    except Exception as e:
        error_msg = f"Agentic workflow failed: {str(e)}"
        logger.error(error_msg)
        return error_msg


async def async_main():
    """Main entry point for Unity3D MCP server."""
    # Use standardized transport runner
    await run_server_async(server_instance.app, server_name="unity3d-mcp")


def main():
    """Synchronous entry point."""
    # Use standardized transport runner
    run_server(server_instance.app, server_name="unity3d-mcp")


if __name__ == "__main__":
    main()
