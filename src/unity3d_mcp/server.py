"""
Unity3D MCP Server Implementation

FastMCP 2.10 compliant server with dual stdio/HTTP interface for comprehensive
Unity 3D automation, VRM avatar pipeline, and VRChat integration.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .assets import AssetManager, MaterialManager
from .avatar import AnimationManager, VRMAvatarManager
from .build import BuildManager, PlatformManager
from .core import ProjectManager, SceneManager, UnityEditorManager
from .utils import ConfigManager, LogManager, UnityPathResolver
from .vrchat import VRChatSDKManager
# NOTE: OSC functionality moved to oscmcp - use server composition for VRChat OSC
from .worldlabs import WorldLabsManager
from .platforms import PlatformManager, ChilloutVRManager, ResoniteManager, ClusterManager

# Configure logging
logger = logging.getLogger(__name__)


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


class Unity3DMCP:
    """Unity3D MCP Server with comprehensive automation capabilities."""

    def __init__(self, config: Optional[Unity3DConfig] = None):
        """Initialize Unity3D MCP server."""
        self.config = config or Unity3DConfig()

        # Initialize FastMCP
        # Removed invalid arguments for newer fastmcp versions
        self.app = FastMCP(name="Unity3D-MCP", version="1.0.0")

        # Initialize managers
        self._init_managers()

        # Register all tools
        self._register_tools()

        logger.info("Unity3D MCP server initialized")

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

        @self.app.tool(
            name="launch_unity_editor", description="Launch Unity Editor with specified project"
        )
        async def launch_unity_editor(
            project_path: str,
            unity_version: str = "",
            batch_mode: bool = False,
            no_graphics: bool = False,
        ) -> Dict[str, Any]:
            """Launch Unity Editor with comprehensive options."""
            return await self.unity_editor.launch_editor(
                project_path, unity_version, batch_mode, no_graphics
            )

        @self.app.tool(
            name="create_unity_project", description="Create new Unity project with template"
        )
        async def create_unity_project(
            project_name: str, project_path: str, template: str = "3D", unity_version: str = ""
        ) -> Dict[str, Any]:
            """Create new Unity project with specified template."""
            return await self.project_manager.create_project(
                project_name, project_path, template, unity_version
            )

        @self.app.tool(
            name="execute_unity_method", description="Execute Unity Editor method via command line"
        )
        async def execute_unity_method(
            class_name: str,
            method_name: str,
            parameters: Dict[str, Any] = {},
            project_path: str = "",
        ) -> Dict[str, Any]:
            """Execute Unity Editor method with parameters."""
            return await self.unity_editor.execute_method(
                class_name, method_name, parameters, project_path
            )

        @self.app.tool(
            name="check_univrm_installed",
            description="Check if UniVRM is installed in a Unity project"
        )
        async def check_univrm_installed(project_path: str) -> Dict[str, Any]:
            """Check UniVRM installation status in a Unity project."""
            return await self.project_manager.check_univrm_installed(project_path)

        @self.app.tool(
            name="install_univrm",
            description="Install UniVRM packages into a Unity project"
        )
        async def install_univrm(
            project_path: str,
            vrm_version: str = "vrm0",
            refresh_unity: bool = True,
        ) -> Dict[str, Any]:
            """Install UniVRM packages (VRM 0.x or 1.0) via Unity Package Manager.
            
            Args:
                project_path: Path to Unity project
                vrm_version: "vrm0" for VRM 0.x (default) or "vrm1" for VRM 1.0
                refresh_unity: Whether to refresh Unity after install
            """
            return await self.project_manager.install_univrm(
                project_path, vrm_version, refresh_unity
            )

        @self.app.tool(
            name="create_unity_project_with_univrm",
            description="Create new Unity project with UniVRM pre-installed"
        )
        async def create_unity_project_with_univrm(
            project_name: str,
            project_path: str,
            template: str = "3D",
            unity_version: str = "",
            vrm_version: str = "vrm0",
        ) -> Dict[str, Any]:
            """Create new Unity project with UniVRM already configured."""
            return await self.project_manager.create_project_with_univrm(
                project_name, project_path, template, unity_version, vrm_version
            )

    def _register_avatar_tools(self):
        """Register VRM avatar and animation tools."""

        @self.app.tool(name="import_vrm_avatar", description="Import VRM avatar into Unity project")
        async def import_vrm_avatar(
            vrm_path: str,
            project_path: str,
            optimize_for_vrchat: bool = True,
            create_prefab: bool = True,
        ) -> Dict[str, Any]:
            """Import and configure VRM avatar for Unity."""
            return await self.vrm_avatar.import_vrm(
                vrm_path, project_path, optimize_for_vrchat, create_prefab
            )

        @self.app.tool(
            name="setup_avatar_animator", description="Setup animator controller for avatar"
        )
        async def setup_avatar_animator(
            avatar_path: str, animator_type: str = "humanoid", include_facial: bool = True
        ) -> Dict[str, Any]:
            """Setup animator controller for avatar."""
            return await self.animation.setup_animator(avatar_path, animator_type, include_facial)

    def _register_asset_tools(self):
        """Register asset management tools."""

        @self.app.tool(name="import_asset_package", description="Import Unity asset package")
        async def import_asset_package(
            package_path: str, project_path: str, interactive: bool = False
        ) -> Dict[str, Any]:
            """Import Unity asset package."""
            return await self.asset_manager.import_package(package_path, project_path, interactive)

        @self.app.tool(
            name="optimize_textures", description="Optimize textures for target platform"
        )
        async def optimize_textures(
            texture_paths: List[str], platform: str = "PC", quality: str = "High"
        ) -> Dict[str, Any]:
            """Optimize textures for target platform."""
            return await self.asset_manager.optimize_textures(texture_paths, platform, quality)

    def _register_build_tools(self):
        """Register build pipeline tools."""

        @self.app.tool(
            name="build_unity_project", description="Build Unity project for target platform"
        )
        async def build_unity_project(
            project_path: str, build_target: str, output_path: str, development_build: bool = False
        ) -> Dict[str, Any]:
            """Build Unity project for target platform."""
            return await self.build_manager.build_project(
                project_path, build_target, output_path, development_build
            )

    def _register_vrchat_tools(self):
        """Register VRChat SDK integration tools."""

        @self.app.tool(
            name="vrchat_check_auth",
            description="Check VRChat authentication status"
        )
        async def vrchat_check_auth() -> Dict[str, Any]:
            """Check if authenticated with VRChat SDK."""
            return await self.vrchat_sdk.check_authentication()

        @self.app.tool(
            name="vrchat_authenticate",
            description="Authenticate with VRChat (or set VRCHAT_USERNAME/VRCHAT_PASSWORD env vars)"
        )
        async def vrchat_authenticate(
            username: str = "",
            password: str = "",
            totp_code: str = "",
        ) -> Dict[str, Any]:
            """Authenticate with VRChat API."""
            return await self.vrchat_sdk.authenticate(
                username=username or None,
                password=password or None,
                totp_code=totp_code or None,
            )

        @self.app.tool(
            name="vrchat_check_sdk",
            description="Check if VRChat SDK is installed in Unity project"
        )
        async def vrchat_check_sdk(project_path: str) -> Dict[str, Any]:
            """Check VRChat SDK installation status."""
            return await self.vrchat_sdk.check_sdk_installed(project_path)

        @self.app.tool(
            name="vrchat_validate_avatar",
            description="Validate avatar against VRChat requirements"
        )
        async def vrchat_validate_avatar(
            avatar_prefab: str,
            project_path: str = "",
        ) -> Dict[str, Any]:
            """Validate avatar for VRChat upload."""
            project = project_path or self.config.project_path
            return await self.vrchat_sdk.validate_avatar(avatar_prefab, project)

        @self.app.tool(
            name="upload_vrchat_avatar",
            description="Upload avatar to VRChat using SDK (requires authentication)"
        )
        async def upload_vrchat_avatar(
            avatar_prefab: str,
            avatar_name: str,
            description: str = "",
            tags: List[str] = [],
            project_path: str = "",
            release_status: str = "private",
        ) -> Dict[str, Any]:
            """Upload avatar to VRChat using SDK."""
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

        @self.app.tool(
            name="import_marble_world",
            description="Import World Labs Marble-generated 3D world into Unity"
        )
        async def import_marble_world(
            source_path: str,
            project_path: str,
            asset_name: str = "",
            include_colliders: bool = True,
            optimize_for_vrchat: bool = False,
        ) -> Dict[str, Any]:
            """Import Marble world (meshes, splats, textures) into Unity project."""
            return await self.worldlabs.import_marble_world(
                source_path, project_path, asset_name, include_colliders, optimize_for_vrchat
            )

        @self.app.tool(
            name="check_gaussian_splatting",
            description="Check if Gaussian Splatting renderer is installed"
        )
        async def check_gaussian_splatting(project_path: str) -> Dict[str, Any]:
            """Check if Gaussian Splatting package is installed in Unity project."""
            return await self.worldlabs.check_gaussian_splatting_installed(project_path)

        @self.app.tool(
            name="install_gaussian_splatting",
            description="Install Gaussian Splatting renderer for .ply/.splat files"
        )
        async def install_gaussian_splatting(project_path: str) -> Dict[str, Any]:
            """Install Gaussian Splatting package for rendering World Labs splat exports."""
            return await self.worldlabs.install_gaussian_splatting(project_path)

        @self.app.tool(
            name="optimize_worldlabs_for_vrchat",
            description="Get VRChat optimization recommendations for World Labs assets"
        )
        async def optimize_worldlabs_for_vrchat(
            project_path: str,
            asset_folder: str,
            target_polygon_count: int = 50000,
        ) -> Dict[str, Any]:
            """Analyze World Labs assets and provide VRChat optimization recommendations."""
            return await self.worldlabs.optimize_for_vrchat(
                project_path, asset_folder, target_polygon_count
            )

    def _register_platform_tools(self):
        """Register multi-platform social VR tools (ChilloutVR, Resonite, Cluster)."""

        @self.app.tool(
            name="list_vr_platforms",
            description="List all supported social VR platforms"
        )
        async def list_vr_platforms() -> Dict[str, Any]:
            """List supported social VR platforms and their requirements."""
            return await self.platforms.list_supported_platforms()

        @self.app.tool(
            name="check_platform_sdk",
            description="Check if a social VR platform SDK is installed"
        )
        async def check_platform_sdk(
            platform: str,
            project_path: str,
        ) -> Dict[str, Any]:
            """Check SDK installation for VRChat, ChilloutVR, Cluster, or Resonite."""
            return await self.platforms.check_platform_sdk(platform, project_path)

        # ChilloutVR Tools
        @self.app.tool(
            name="check_cck_installed",
            description="Check if ChilloutVR CCK (Content Creation Kit) is installed"
        )
        async def check_cck_installed(project_path: str) -> Dict[str, Any]:
            """Check ChilloutVR CCK installation status."""
            return await self.platforms.chillout.check_cck_installed(project_path)

        @self.app.tool(
            name="setup_cvr_avatar",
            description="Setup CVRAvatar component for ChilloutVR"
        )
        async def setup_cvr_avatar(
            avatar_object: str,
            project_path: str,
            eye_height: float = 1.6,
        ) -> Dict[str, Any]:
            """Configure avatar for ChilloutVR upload."""
            return await self.platforms.chillout.setup_cvr_avatar(
                avatar_object, project_path, eye_height
            )

        @self.app.tool(
            name="validate_for_chilloutvr",
            description="Validate avatar for ChilloutVR upload"
        )
        async def validate_for_chilloutvr(
            avatar_name: str,
            project_path: str,
        ) -> Dict[str, Any]:
            """Validate avatar meets ChilloutVR requirements."""
            return await self.platforms.chillout.validate_for_chillout(
                avatar_name, project_path
            )

        # Resonite Tools
        @self.app.tool(
            name="prepare_for_resonite",
            description="Prepare model for Resonite import (VRM/GLB direct import)"
        )
        async def prepare_for_resonite(
            model_path: str,
            optimize: bool = True,
        ) -> Dict[str, Any]:
            """Prepare a VRM/GLB model for direct import into Resonite."""
            return await self.platforms.resonite.prepare_for_resonite(model_path, optimize)

        @self.app.tool(
            name="check_resonite_compatibility",
            description="Check if model is compatible with Resonite"
        )
        async def check_resonite_compatibility(model_path: str) -> Dict[str, Any]:
            """Check model compatibility for Resonite import."""
            return await self.platforms.resonite.check_resonite_compatibility(model_path)

        # Cluster Tools
        @self.app.tool(
            name="check_cluster_kit",
            description="Check if Cluster Creator Kit is installed"
        )
        async def check_cluster_kit(project_path: str) -> Dict[str, Any]:
            """Check Cluster Creator Kit installation status."""
            return await self.platforms.cluster.check_cluster_kit_installed(project_path)

        @self.app.tool(
            name="prepare_for_cluster",
            description="Prepare avatar for Cluster upload"
        )
        async def prepare_for_cluster(
            avatar_path: str,
            project_path: str,
        ) -> Dict[str, Any]:
            """Prepare avatar for Cluster (Japanese social VR) upload."""
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
            logger.error(f"Failed to run HTTP mode: {e}")
            raise

    async def run_dual(self):
        """Run server in dual stdio + HTTP mode."""
        # Dual mode might not be supported in the same way.
        # Fallback to stdio for now to ensure basic functionality.
        logger.warning("Dual mode not fully supported in this version. Falling back to stdio.")
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
        logger.exception("Server error: %s", e)


def main():
    """Synchronous entry point."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
