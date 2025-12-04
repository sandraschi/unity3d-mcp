"""
Unity3D MCP Server Implementation

FastMCP 2.13+ compliant server with comprehensive Unity 3D automation,
VRM avatar pipeline, and VRChat integration.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import structlog
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .assets import AssetManager, MaterialManager
from .avatar import AnimationManager, VRMAvatarManager
from .build import BuildManager
from .core import ProjectManager, SceneManager, UnityEditorManager
from .platforms import PlatformManager
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
    auto_detect_unity: bool = Field(
        default=True, description="Auto-detect Unity Editor installation"
    )
    enable_http: bool = Field(default=True, description="Enable HTTP interface alongside stdio")
    http_port: int = Field(default=8080, description="HTTP server port")
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

        # Initialize FastMCP with lifespan
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
        self.platforms = PlatformManager(self.config)
        self.path_resolver = UnityPathResolver(self.config)
        self.config_manager = ConfigManager(self.config)
        self.log_manager = LogManager(self.config)

    def _register_tools(self):
        """Register all MCP tools with comprehensive metadata."""

        # Core Unity Tools
        self._register_core_tools()

        # Avatar/VRM Tools
        self._register_avatar_tools()

        # Asset Management Tools
        self._register_asset_tools()

        # Build Pipeline Tools
        self._register_build_tools()

        # VRChat Integration Tools
        self._register_vrchat_tools()

        # World Labs Integration Tools
        self._register_worldlabs_tools()

        # Multi-Platform Tools (ChilloutVR, Resonite, Cluster)
        self._register_platform_tools()

    def _register_core_tools(self):
        """Register core Unity Editor automation tools."""

        @self.app.tool
        async def launch_unity_editor(
            project_path: str,
            unity_version: str = "",
            batch_mode: bool = False,
            no_graphics: bool = False,
        ) -> Dict[str, Any]:
            """Launch Unity Editor with specified project.

            Opens the Unity Editor application with the specified Unity project,
            optionally in batch mode (headless) or without graphics rendering.

            Args:
                project_path: Path to Unity project directory
                unity_version: Specific Unity version to use (empty for auto-detect)
                batch_mode: Run Unity in batch mode (no GUI)
                no_graphics: Run without graphics device initialization

            Returns:
                Dictionary containing:
                - success: Boolean indicating if launch succeeded
                - process_id: Process ID of launched Unity Editor
                - editor_version: Unity Editor version being used
                - project_path: Confirmed project path
                - error: Error message if failed

            Examples:
                # Basic launch
                launch_unity_editor("D:/Projects/MyGame")

                # Launch specific version in batch mode
                launch_unity_editor(
                    project_path="D:/Projects/MyGame",
                    unity_version="2022.3.15f1",
                    batch_mode=True
                )

                # Headless mode for CI/CD
                launch_unity_editor(
                    project_path="D:/Projects/MyGame",
                    batch_mode=True,
                    no_graphics=True
                )
            """
            return await self.unity_editor.launch_editor(
                project_path, unity_version, batch_mode, no_graphics
            )

        @self.app.tool
        async def create_unity_project(
            project_name: str, project_path: str, template: str = "3D", unity_version: str = ""
        ) -> Dict[str, Any]:
            """Create new Unity project with template.

            Initializes a new Unity project with the specified template (3D, 2D, URP, HDRP, etc.).
            Automatically configures project settings and folder structure.

            Args:
                project_name: Name for the new Unity project
                project_path: Parent directory where project will be created
                template: Unity project template (default: "3D").
                    Options: "3D", "2D", "3D (URP)", "3D (HDRP)", "VR"
                unity_version: Specific Unity version (empty for latest installed)

            Returns:
                Dictionary containing:
                - success: Boolean indicating if project creation succeeded
                - project_path: Full path to created project
                - unity_version: Unity version used
                - template: Template that was used
                - error: Error message if failed

            Examples:
                # Basic 3D project
                create_unity_project("MyGame", "D:/Projects")

                # URP project with specific version
                create_unity_project(
                    project_name="VRChatWorld",
                    project_path="D:/VRChat",
                    template="3D (URP)",
                    unity_version="2022.3.15f1"
                )

                # 2D project
                create_unity_project("Platformer", "D:/Games", template="2D")
            """
            return await self.project_manager.create_project(
                project_name, project_path, template, unity_version
            )

        @self.app.tool
        async def execute_unity_method(
            class_name: str,
            method_name: str,
            parameters: Dict[str, Any] = {},
            project_path: str = "",
        ) -> Dict[str, Any]:
            """Execute Unity Editor method via command line.

            Runs a static C# method in Unity Editor using -executeMethod command line flag.
            Useful for custom build scripts, asset processing, and automation tasks.

            Args:
                class_name: Fully qualified class name (e.g., "BuildTools.MyBuilder")
                method_name: Static method name to execute
                parameters: Dictionary of parameters to pass to method
                    (converted to command line args)
                project_path: Unity project path (empty for default)

            Returns:
                Dictionary containing:
                - success: Boolean indicating if execution succeeded
                - output: Console output from Unity Editor
                - exit_code: Editor exit code
                - execution_time: Time taken in seconds
                - error: Error message if failed

            Examples:
                # Simple build method
                execute_unity_method("BuildTools.Builder", "BuildWindows")

                # With parameters
                execute_unity_method(
                    class_name="AssetProcessor.Optimizer",
                    method_name="OptimizeTextures",
                    parameters={"quality": "high", "platform": "Android"}
                )

                # Custom project path
                execute_unity_method(
                    class_name="CustomTools.Exporter",
                    method_name="ExportAssets",
                    project_path="D:/Projects/MyGame"
                )
            """
            return await self.unity_editor.execute_method(
                class_name, method_name, parameters, project_path
            )

        @self.app.tool
        async def check_univrm_installed(project_path: str) -> Dict[str, Any]:
            """Check if UniVRM is installed in a Unity project.

            Verifies whether UniVRM (VRM importer/exporter for Unity) is installed
            by checking the Packages/manifest.json file for UniVRM package entries.

            Args:
                project_path: Path to Unity project directory

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - installed: Boolean indicating if UniVRM is installed
                - vrm_version: Version string ("vrm0" or "vrm1") if installed
                - package_info: Dictionary with package details
                - error: Error message if failed

            Examples:
                # Check installation
                check_univrm_installed("D:/Projects/VRChatAvatar")

                # Returns: {"success": True, "installed": True, "vrm_version": "vrm0"}
            """
            return await self.project_manager.check_univrm_installed(project_path)

        @self.app.tool
        async def install_univrm(
            project_path: str,
            vrm_version: str = "vrm0",
            refresh_unity: bool = True,
        ) -> Dict[str, Any]:
            """Install UniVRM packages into a Unity project.

            Adds UniVRM package dependencies to Unity Package Manager manifest.
            UniVRM enables importing and exporting VRM format avatars in Unity.

            VRM VERSIONS:
            - vrm0: VRM 0.x specification (widely supported, stable)
            - vrm1: VRM 1.0 specification (newer, better features)

            Args:
                project_path: Path to Unity project directory
                vrm_version: "vrm0" for VRM 0.x (default) or "vrm1" for VRM 1.0
                refresh_unity: Whether to refresh Unity after install

            Returns:
                Dictionary containing:
                - success: Boolean indicating if installation succeeded
                - installed_packages: List of installed package names
                - vrm_version: VRM version that was installed
                - manifest_path: Path to modified manifest.json
                - error: Error message if failed

            Examples:
                # Install VRM 0.x (most compatible)
                install_univrm("D:/Projects/VRChatAvatar")

                # Install VRM 1.0
                install_univrm(
                    project_path="D:/Projects/Avatar",
                    vrm_version="vrm1"
                )

                # Install without refreshing Unity
                install_univrm(
                    project_path="D:/Projects/Avatar",
                    refresh_unity=False
                )
            """
            return await self.project_manager.install_univrm(
                project_path, vrm_version, refresh_unity
            )

        @self.app.tool
        async def create_unity_project_with_univrm(
            project_name: str,
            project_path: str,
            template: str = "3D",
            unity_version: str = "",
            vrm_version: str = "vrm0",
        ) -> Dict[str, Any]:
            """Create new Unity project with UniVRM pre-installed.

            Combines project creation and UniVRM installation into one step.
            Perfect for starting new VRM avatar projects quickly.

            Args:
                project_name: Name for the new Unity project
                project_path: Parent directory where project will be created
                template: Unity project template (default: "3D")
                unity_version: Specific Unity version (empty for latest)
                vrm_version: "vrm0" for VRM 0.x (default) or "vrm1" for VRM 1.0

            Returns:
                Dictionary containing:
                - success: Boolean indicating if creation succeeded
                - project_path: Full path to created project
                - unity_version: Unity version used
                - vrm_version: VRM version installed
                - installed_packages: List of installed packages
                - error: Error message if failed

            Examples:
                # Basic VRM-ready project
                create_unity_project_with_univrm("MyAvatar", "D:/Projects")

                # VRM 1.0 with specific Unity version
                create_unity_project_with_univrm(
                    project_name="VRM1Avatar",
                    project_path="D:/VRM",
                    unity_version="2022.3.15f1",
                    vrm_version="vrm1"
                )

                # URP project with VRM
                create_unity_project_with_univrm(
                    project_name="VRChatAvatar",
                    project_path="D:/VRChat",
                    template="3D (URP)"
                )
            """
            return await self.project_manager.create_project_with_univrm(
                project_name, project_path, template, unity_version, vrm_version
            )

    def _register_avatar_tools(self):
        """Register VRM avatar and animation tools."""

        @self.app.tool
        async def import_vrm_avatar(
            vrm_path: str,
            project_path: str,
            optimize_for_vrchat: bool = True,
            create_prefab: bool = True,
        ) -> Dict[str, Any]:
            """Import VRM avatar into Unity project.

            Imports a VRM format avatar file into Unity, optionally optimizing it
            for VRChat specifications and creating a prefab for easy reuse.

            Args:
                vrm_path: Path to .vrm file to import
                project_path: Unity project path to import into
                optimize_for_vrchat: Apply VRChat optimization (materials, shaders, performance)
                create_prefab: Create Unity prefab from imported avatar

            Returns:
                Dictionary containing:
                - success: Boolean indicating if import succeeded
                - imported_path: Asset path in Unity project
                - prefab_path: Path to created prefab (if create_prefab=True)
                - optimization_report: Dict with optimization details
                - polygon_count: Triangle count after optimization
                - error: Error message if failed

            Examples:
                # Basic import
                import_vrm_avatar(
                    vrm_path="D:/Avatars/model.vrm",
                    project_path="D:/Projects/VRChat"
                )

                # Import without VRChat optimization
                import_vrm_avatar(
                    vrm_path="D:/Models/character.vrm",
                    project_path="D:/Projects/Game",
                    optimize_for_vrchat=False
                )

                # Import without creating prefab
                import_vrm_avatar(
                    vrm_path="D:/Avatars/test.vrm",
                    project_path="D:/Projects/Test",
                    create_prefab=False
                )
            """
            return await self.vrm_avatar.import_vrm(
                vrm_path, project_path, optimize_for_vrchat, create_prefab
            )

        @self.app.tool
        async def setup_avatar_animator(
            avatar_path: str, animator_type: str = "humanoid", include_facial: bool = True
        ) -> Dict[str, Any]:
            """Setup animator controller for avatar.

            Configures Unity animator controller for avatar with appropriate animation
            layers, parameters, and state machines. Supports humanoid and generic rigs.

            Args:
                avatar_path: Asset path to avatar in Unity project
                animator_type: Animator rig type ("humanoid" or "generic")
                include_facial: Add facial animation blend shapes support

            Returns:
                Dictionary containing:
                - success: Boolean indicating if setup succeeded
                - controller_path: Path to created animator controller
                - animator_type: Type of animator created
                - layers: List of animation layers created
                - parameters: List of animator parameters
                - facial_support: Boolean indicating if facial animations are supported
                - error: Error message if failed

            Examples:
                # Basic humanoid setup
                setup_avatar_animator("Assets/Models/Avatar.prefab")

                # Generic rig without facial
                setup_avatar_animator(
                    avatar_path="Assets/Characters/Monster.fbx",
                    animator_type="generic",
                    include_facial=False
                )

                # Full humanoid with facial animations
                setup_avatar_animator(
                    avatar_path="Assets/VRM/Character.prefab",
                    animator_type="humanoid",
                    include_facial=True
                )
            """
            return await self.animation.setup_animator(avatar_path, animator_type, include_facial)

    def _register_asset_tools(self):
        """Register asset management tools."""

        @self.app.tool
        async def import_asset_package(
            package_path: str, project_path: str, interactive: bool = False
        ) -> Dict[str, Any]:
            """Import Unity asset package.

            Imports a .unitypackage file into Unity project, extracting all assets
            and preserving folder structure.

            Args:
                package_path: Path to .unitypackage file
                project_path: Unity project path to import into
                interactive: Show Unity import dialog (requires GUI)

            Returns:
                Dictionary containing:
                - success: Boolean indicating if import succeeded
                - imported_count: Number of assets imported
                - asset_paths: List of imported asset paths
                - package_name: Name of imported package
                - error: Error message if failed

            Examples:
                # Automated import
                import_asset_package(
                    package_path="D:/Downloads/MyAssets.unitypackage",
                    project_path="D:/Projects/Game"
                )

                # Interactive import (shows Unity dialog)
                import_asset_package(
                    package_path="D:/Assets/Effects.unitypackage",
                    project_path="D:/Projects/Game",
                    interactive=True
                )
            """
            return await self.asset_manager.import_package(package_path, project_path, interactive)

        @self.app.tool
        async def optimize_textures(
            texture_paths: List[str], platform: str = "PC", quality: str = "High"
        ) -> Dict[str, Any]:
            """Optimize textures for target platform.

            Configures texture import settings for optimal performance and quality
            on target platform (compression, max size, mipmaps, etc.).

            Args:
                texture_paths: List of texture asset paths in Unity project
                platform: Target platform ("PC", "Android", "iOS", "WebGL", "Quest")
                quality: Quality preset ("Low", "Medium", "High", "Ultra")

            Returns:
                Dictionary containing:
                - success: Boolean indicating if optimization succeeded
                - optimized_count: Number of textures optimized
                - original_size: Total size before optimization (bytes)
                - optimized_size: Total size after optimization (bytes)
                - savings_percent: Percentage reduction in size
                - settings_applied: Dict with compression settings used
                - error: Error message if failed

            Examples:
                # Optimize for PC high quality
                optimize_textures(
                    texture_paths=["Assets/Textures/Albedo.png", "Assets/Textures/Normal.png"],
                    platform="PC",
                    quality="High"
                )

                # Optimize for Quest (aggressive compression)
                optimize_textures(
                    texture_paths=["Assets/Materials/AvatarTexture.png"],
                    platform="Quest",
                    quality="Medium"
                )

                # Mobile optimization
                optimize_textures(
                    texture_paths=["Assets/UI/Icons/*.png"],
                    platform="Android",
                    quality="Low"
                )
            """
            return await self.asset_manager.optimize_textures(texture_paths, platform, quality)

    def _register_build_tools(self):
        """Register build pipeline tools."""

        @self.app.tool
        async def build_unity_project(
            project_path: str, build_target: str, output_path: str, development_build: bool = False
        ) -> Dict[str, Any]:
            """Build Unity project for target platform.

            Compiles Unity project into standalone executable for target platform.
            Supports Windows, macOS, Linux, Android, iOS, and WebGL builds.

            Args:
                project_path: Unity project path to build
                build_target: Target platform
                    ("StandaloneWindows64", "Android", "iOS", "WebGL", etc.)
                output_path: Directory where build will be created
                development_build: Enable development build (debugging, profiler)

            Returns:
                Dictionary containing:
                - success: Boolean indicating if build succeeded
                - build_path: Full path to build output
                - build_size: Size of build in bytes
                - build_time: Build duration in seconds
                - build_target: Platform that was built
                - warnings: List of build warnings
                - error: Error message if failed

            Examples:
                # Windows build
                build_unity_project(
                    project_path="D:/Projects/Game",
                    build_target="StandaloneWindows64",
                    output_path="D:/Builds/Windows"
                )

                # Development build for testing
                build_unity_project(
                    project_path="D:/Projects/Game",
                    build_target="Android",
                    output_path="D:/Builds/Android",
                    development_build=True
                )

                # WebGL production build
                build_unity_project(
                    project_path="D:/Projects/WebGame",
                    build_target="WebGL",
                    output_path="D:/Builds/Web"
                )
            """
            return await self.build_manager.build_project(
                project_path, build_target, output_path, development_build
            )

    def _register_vrchat_tools(self):
        """Register VRChat SDK integration tools."""

        @self.app.tool
        async def vrchat_check_auth() -> Dict[str, Any]:
            """Check VRChat authentication status.

            Verifies whether VRChat API credentials are configured and valid.
            Required before uploading avatars or worlds to VRChat.

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - authenticated: Boolean indicating if credentials are valid
                - username: VRChat username if authenticated
                - requires_2fa: Boolean indicating if 2FA is needed
                - error: Error message if failed

            Examples:
                # Check auth status
                vrchat_check_auth()

                # Returns: {"success": True, "authenticated": True, "username": "MyVRChatName"}
            """
            return await self.vrchat_sdk.check_authentication()

        @self.app.tool
        async def vrchat_authenticate(
            username: str = "",
            password: str = "",
            totp_code: str = "",
        ) -> Dict[str, Any]:
            """Authenticate with VRChat.

            Logs into VRChat API to enable avatar and world uploads. Supports 2FA/TOTP
            authentication. Can also use VRCHAT_USERNAME/VRCHAT_PASSWORD environment variables.

            Args:
                username: VRChat account username (empty to use env var)
                password: VRChat account password (empty to use env var)
                totp_code: 2FA/TOTP code if 2FA is enabled

            Returns:
                Dictionary containing:
                - success: Boolean indicating if authentication succeeded
                - authenticated: Boolean indicating current auth status
                - username: Authenticated username
                - requires_2fa: Boolean indicating if 2FA code is needed
                - auth_token: Authentication token (for internal use)
                - error: Error message if failed

            Examples:
                # Authenticate with credentials
                vrchat_authenticate(
                    username="myusername",
                    password="mypassword"
                )

                # Authenticate with 2FA
                vrchat_authenticate(
                    username="myusername",
                    password="mypassword",
                    totp_code="123456"
                )

                # Use environment variables
                vrchat_authenticate()  # Uses VRCHAT_USERNAME and VRCHAT_PASSWORD
            """
            return await self.vrchat_sdk.authenticate(
                username=username or None,
                password=password or None,
                totp_code=totp_code or None,
            )

        @self.app.tool
        async def vrchat_check_sdk(project_path: str) -> Dict[str, Any]:
            """Check if VRChat SDK is installed in Unity project.

            Verifies whether VRChat SDK (VRCSDK3) is present in Unity project
            by checking package manifest and SDK directories.

            Args:
                project_path: Unity project path to check

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - installed: Boolean indicating if SDK is installed
                - sdk_version: VRChat SDK version if installed
                - sdk_type: SDK type ("Avatars", "Worlds", or "Both")
                - package_path: Path to SDK package
                - error: Error message if failed

            Examples:
                # Check SDK installation
                vrchat_check_sdk("D:/Projects/VRChatWorld")

                # Returns: {"success": True, "installed": True,
                #           "sdk_version": "3.5.0", "sdk_type": "Avatars"}
            """
            return await self.vrchat_sdk.check_sdk_installed(project_path)

        @self.app.tool
        async def vrchat_validate_avatar(
            avatar_prefab: str,
            project_path: str = "",
        ) -> Dict[str, Any]:
            """Validate avatar against VRChat requirements.

            Checks avatar against VRChat technical requirements (polygon count, material slots,
            shader compatibility, physics components, etc.). Required before upload.

            Args:
                avatar_prefab: Path to avatar prefab in Unity project
                project_path: Unity project path (empty for default)

            Returns:
                Dictionary containing:
                - success: Boolean indicating validation completed
                - valid: Boolean indicating if avatar passes all checks
                - performance_rank: VRChat performance rank
                    ("Excellent", "Good", "Medium", "Poor", "Very Poor")
                - polygon_count: Total triangle count
                - material_slots: Number of material slots
                - validation_errors: List of blocking errors
                - validation_warnings: List of non-blocking warnings
                - suggestions: List of optimization suggestions
                - error: Error message if failed

            Examples:
                # Validate avatar
                vrchat_validate_avatar(
                    avatar_prefab="Assets/Avatars/MyAvatar.prefab",
                    project_path="D:/Projects/VRChat"
                )

                # Use default project path
                vrchat_validate_avatar("Assets/MyCharacter.prefab")
            """
            project = project_path or self.config.project_path
            return await self.vrchat_sdk.validate_avatar(avatar_prefab, project)

        @self.app.tool
        async def upload_vrchat_avatar(
            avatar_prefab: str,
            avatar_name: str,
            description: str = "",
            tags: List[str] = [],
            project_path: str = "",
            release_status: str = "private",
        ) -> Dict[str, Any]:
            """Upload avatar to VRChat using SDK.

            Uploads avatar to VRChat platform. Requires VRChat authentication and
            SDK installation. Avatar must pass validation before upload.

            Args:
                avatar_prefab: Path to avatar prefab in Unity project
                avatar_name: Name for avatar on VRChat platform
                description: Description text for avatar page
                tags: List of tags for avatar categorization
                project_path: Unity project path (empty for default)
                release_status: Release status ("private" or "public")

            Returns:
                Dictionary containing:
                - success: Boolean indicating if upload succeeded
                - avatar_id: VRChat avatar ID
                - avatar_name: Name of uploaded avatar
                - avatar_url: URL to avatar page on VRChat
                - release_status: Release status
                - upload_time: Time taken to upload
                - thumbnail_url: URL to avatar thumbnail
                - error: Error message if failed

            Examples:
                # Upload private avatar
                upload_vrchat_avatar(
                    avatar_prefab="Assets/Avatars/MyAvatar.prefab",
                    avatar_name="My Cool Avatar",
                    description="A cool avatar I made",
                    project_path="D:/Projects/VRChat"
                )

                # Upload with tags
                upload_vrchat_avatar(
                    avatar_prefab="Assets/Characters/Robot.prefab",
                    avatar_name="Robot Avatar",
                    tags=["robot", "mecha", "scifi"],
                    release_status="private"
                )

                # Public release
                upload_vrchat_avatar(
                    avatar_prefab="Assets/PublicAvatars/Generic.prefab",
                    avatar_name="Generic Avatar",
                    description="Free to use avatar",
                    release_status="public"
                )
            """
            return await self.vrchat_sdk.upload_avatar(
                avatar_prefab=avatar_prefab,
                avatar_name=avatar_name,
                description=description,
                tags=tags,
                project_path=project_path or None,
                release_status=release_status,
            )

    def _register_worldlabs_tools(self):
        """Register World Labs (Marble/Chisel) integration tools."""

        @self.app.tool
        async def import_marble_world(
            source_path: str,
            project_path: str,
            asset_name: str = "",
            include_colliders: bool = True,
            optimize_for_vrchat: bool = False,
        ) -> Dict[str, Any]:
            """Import World Labs Marble-generated 3D world into Unity.

            Imports 3D world generated by World Labs Marble AI (meshes, Gaussian splats,
            textures) into Unity project. Supports both mesh colliders and splat visuals.

            Args:
                source_path: Path to Marble export directory or zip
                project_path: Unity project path to import into
                asset_name: Name for imported assets (empty for auto-generate)
                include_colliders: Generate collision meshes from Marble collider export
                optimize_for_vrchat: Apply VRChat world optimization (polygon reduction)

            Returns:
                Dictionary containing:
                - success: Boolean indicating if import succeeded
                - asset_paths: Dict with paths to imported assets (meshes, splats, textures)
                - collider_path: Path to collision mesh (if include_colliders=True)
                - polygon_count: Total triangle count
                - splat_count: Number of Gaussian splats (if applicable)
                - optimization_report: Dict with optimization details (if optimize_for_vrchat=True)
                - error: Error message if failed

            Examples:
                # Basic import
                import_marble_world(
                    source_path="D:/Marble/exports/tokyo_street",
                    project_path="D:/Projects/VRChat"
                )

                # Import with VRChat optimization
                import_marble_world(
                    source_path="D:/Marble/room.zip",
                    project_path="D:/VRChat/Worlds",
                    asset_name="LivingRoom",
                    optimize_for_vrchat=True
                )

                # Visual only (no colliders)
                import_marble_world(
                    source_path="D:/Marble/scene.zip",
                    project_path="D:/Projects/Background",
                    include_colliders=False
                )
            """
            return await self.worldlabs.import_marble_world(
                source_path, project_path, asset_name, include_colliders, optimize_for_vrchat
            )

        @self.app.tool
        async def check_gaussian_splatting(project_path: str) -> Dict[str, Any]:
            """Check if Gaussian Splatting renderer is installed.

            Verifies whether Gaussian Splatting package (gsplat-unity) is installed
            in Unity project for rendering .ply/.splat files from World Labs Marble.

            Args:
                project_path: Unity project path to check

            Returns:
                Dictionary containing:
                - success: Boolean indicating check completed
                - installed: Boolean indicating if package is installed
                - package_version: Version string if installed
                - package_path: Path to package in project
                - error: Error message if failed

            Examples:
                # Check installation
                check_gaussian_splatting("D:/Projects/VRChat")

                # Returns: {"success": True, "installed": True, "package_version": "1.2.3"}
            """
            return await self.worldlabs.check_gaussian_splatting_installed(project_path)

        @self.app.tool
        async def install_gaussian_splatting(project_path: str) -> Dict[str, Any]:
            """Install Gaussian Splatting renderer for .ply/.splat files.

            Installs gsplat-unity package via Unity Package Manager to enable
            rendering of Gaussian splat files exported from World Labs Marble.

            Args:
                project_path: Unity project path to install into

            Returns:
                Dictionary containing:
                - success: Boolean indicating if installation succeeded
                - package_version: Installed version string
                - package_path: Path to installed package
                - dependencies: List of installed dependencies
                - error: Error message if failed

            Examples:
                # Install Gaussian Splatting
                install_gaussian_splatting("D:/Projects/VRChat")

                # Returns: {"success": True, "package_version": "1.2.3"}
            """
            return await self.worldlabs.install_gaussian_splatting(project_path)

        @self.app.tool
        async def optimize_worldlabs_for_vrchat(
            project_path: str,
            asset_folder: str,
            target_polygon_count: int = 50000,
        ) -> Dict[str, Any]:
            """Get VRChat optimization recommendations for World Labs assets.

            Analyzes imported World Labs Marble assets and provides detailed
            optimization recommendations for VRChat worlds (polygon reduction,
            texture optimization, LOD setup, etc.).

            Args:
                project_path: Unity project path
                asset_folder: Folder containing World Labs assets
                target_polygon_count: Target polygon count for VRChat optimization

            Returns:
                Dictionary containing:
                - success: Boolean indicating analysis completed
                - current_polygon_count: Current triangle count
                - target_polygon_count: Target triangle count
                - reduction_percent: Percentage reduction needed
                - recommendations: List of optimization recommendations
                - estimated_performance: Estimated VRChat world performance rank
                - lod_suggestions: LOD (Level of Detail) setup suggestions
                - texture_optimizations: Texture compression recommendations
                - error: Error message if failed

            Examples:
                # Analyze for VRChat
                optimize_worldlabs_for_vrchat(
                    project_path="D:/Projects/VRChat",
                    asset_folder="Assets/Worlds/TokyoStreet"
                )

                # Custom polygon target
                optimize_worldlabs_for_vrchat(
                    project_path="D:/VRChat/Worlds",
                    asset_folder="Assets/Marble/Room",
                    target_polygon_count=30000
                )
            """
            return await self.worldlabs.optimize_for_vrchat(
                project_path, asset_folder, target_polygon_count
            )

    def _register_platform_tools(self):
        """Register multi-platform social VR tools (ChilloutVR, Resonite, Cluster)."""

        @self.app.tool
        async def list_vr_platforms() -> Dict[str, Any]:
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
            return await self.platforms.chillout.setup_cvr_avatar(
                avatar_object, project_path, eye_height
            )

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

    async def run_stdio(self):
        """Run server in stdio mode."""
        # Updated for fastmcp 2.13+
        await self.app.run_async()

    async def run_http(self, host: str = "0.0.0.0", port: int = 8080):
        """Run server in HTTP mode."""
        # Updated for fastmcp 2.13+ - attempting to use SSE transport if available, or just run
        try:
            # Assuming 'sse' is the transport for HTTP/SSE
            await self.app.run_async(transport="sse")
        except Exception as e:
            logger.error("Failed to run HTTP mode", error=str(e))
            raise

    async def run_dual(self):
        """Run server in dual stdio + HTTP mode."""
        # Dual mode might not be supported in the same way.
        # Fallback to stdio for now to ensure basic functionality.
        logger.warning("Dual mode not fully supported - falling back to stdio")
        await self.run_stdio()


def create_app(config: Optional[Unity3DConfig] = None) -> Unity3DMCP:
    """Create Unity3D MCP application instance."""
    return Unity3DMCP(config)


async def async_main():
    """Main entry point for Unity3D MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="Unity3D MCP Server")
    parser.add_argument(
        "--mode", choices=["stdio", "http", "dual"], default="stdio", help="Server mode"
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port")
    parser.add_argument("--config", help="Configuration file path")

    args = parser.parse_args()

    # Load configuration
    config = Unity3DConfig()
    if args.config:
        # Load from file
        pass

    # Create and run server
    server = create_app(config)

    try:
        if args.mode == "stdio":
            await server.run_stdio()
        elif args.mode == "http":
            await server.run_http(host=args.host, port=args.port)
        else:  # dual
            await server.run_dual()
    except KeyboardInterrupt:
        logger.info("Shutting down Unity3D MCP server")
    except Exception as e:
        logger.exception("Server error", error=str(e))


def main():
    """Synchronous entry point."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
