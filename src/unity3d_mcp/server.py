"""
Unity3D MCP Server Implementation

FastMCP 3.2.0+ compliant server with comprehensive Unity 3D automation,
VRM avatar pipeline, and VRChat integration.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import structlog
from fastmcp import FastMCP
from fastmcp.server import create_proxy
from fastmcp.server.providers.skills import SkillsDirectoryProvider
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
    from unity3d_mcp import __version__
    from unity3d_mcp.utils.telemetry import init_metrics, install_tool_call_wrapper, start_metrics_server

    if os.getenv("UNITY3D_MCP_LOG_FORMAT", "").strip().lower() == "json":
        from unity3d_mcp.utils.structured_logging import configure_json_logging

        configure_json_logging(logging.getLogger())
    init_metrics()
    install_tool_call_wrapper(mcp_instance)
    if os.getenv("UNITY3D_MCP_START_METRICS_SERVER", "true").strip().lower() not in {"0", "false", "no", "off"}:
        start_metrics_server()
    logger.info("Unity3D MCP server starting up", version=__version__)
    yield
    logger.info("Unity3D MCP server shutting down")


class Unity3DMCP:
    """Unity3D MCP Server with comprehensive automation capabilities."""

    def __init__(self, config: Unity3DConfig | None = None):
        """Initialize Unity3D MCP server."""
        self.config = config or Unity3DConfig()

        # Initialize FastMCP with lifespan (FastMCP 3.2.0+)
        self.app = FastMCP(name="Unity3D-MCP", version="1.5.0", lifespan=server_lifespan)

        _bridge_proxies: list[str] = []
        bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
        if bridge_urls:
            for url in bridge_urls.split(","):
                url = url.strip()
                if url:
                    try:
                        self.app.add_provider(create_proxy(url))
                        _bridge_proxies.append(url)
                    except Exception as exc:
                        logger.warning("Bridge proxy failed", url=url, error=str(exc))

        # Register skills
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
        if skills_dir.is_dir():
            try:
                self.app.add_provider(SkillsDirectoryProvider(roots=[skills_dir]))
                logger.info("Skills provider registered from %s", skills_dir)
            except Exception as exc:
                logger.warning("Skills provider skipped", error=str(exc))

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
            UnityBridgeToolManager,
            UnityBuildToolManager,
            UnityCoreToolManager,
            UnityImportToolManager,
            UnityJobsToolManager,
            UnityRenderToolManager,
            UnitySceneToolManager,
            UnityValidationToolManager,
            UnityVisionRefineToolManager,
            VRChatToolManager,
            WorldLabsToolManager,
        )
        from .utils.job_queue import configure_job_runners
        from .utils.simulation_runner import run_bridge_simulation

        self.bridge_client = UnityBridgeClient()
        self.unity_core_manager = UnityCoreToolManager(self.app, self.unity_editor, self.project_manager)
        self.unity_scene_manager = UnitySceneToolManager(self.app, self.scene_manager)
        self.unity_avatar_manager = UnityAvatarToolManager(self.app, self.vrm_avatar, self.animation)
        self.unity_asset_manager = UnityAssetToolManager(self.app, self.asset_manager)
        self.unity_build_manager = UnityBuildToolManager(self.app, self.build_manager)
        self.vrchat_manager = VRChatToolManager(self.app, self.vrchat_sdk, self.config)
        self.worldlabs_manager = WorldLabsToolManager(self.app, self.worldlabs)
        self.platform_manager = PlatformToolManager(
            self.app, self.platforms, self.vrchat_sdk, self.bridge_client
        )
        self.unity_bridge_manager = UnityBridgeToolManager(self.app, self.bridge_client)
        self.unity_render_manager = UnityRenderToolManager(self.app, self.bridge_client)
        self.unity_api_manager = UnityAPIToolManager(self.app, self.bridge_client)
        self.unity_jobs_manager = UnityJobsToolManager(self.app)
        self.unity_import_manager = UnityImportToolManager(self.app, self.import_export_manager)
        self.unity_vision_refine_manager = UnityVisionRefineToolManager(self.app, self.bridge_client)
        self.unity_validation_manager = UnityValidationToolManager(
            self.app, self.bridge_client, self.vrchat_sdk, self.platforms
        )

        configure_job_runners(
            build_runner=self.build_manager.build_project,
            import_runner=self.import_export_manager.import_3d_model,
            simulation_runner=run_bridge_simulation,
        )

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
        self.unity_bridge_manager.register_tools()
        self.unity_render_manager.register_tools()
        self.unity_api_manager.register_tools()
        self.unity_jobs_manager.register_tools()
        self.unity_import_manager.register_tools()
        self.unity_vision_refine_manager.register_tools()
        self.unity_validation_manager.register_tools()

        logger.info("Portmanteau tools registered successfully")

        # NOTE (2026-07-18): the 9 flat platform-helper tools (list_vr_platforms,
        # check_platform_sdk, check_cck_installed, setup_cvr_avatar,
        # validate_for_chilloutvr, prepare_for_resonite, check_resonite_compatibility,
        # check_cluster_kit, prepare_for_cluster) and the 11 flat api_* tools
        # (api_execute_method, api_get_scene_objects, api_modify_object,
        # api_create_prefab, api_run_simulation, api_batch_operations,
        # api_move_along_path, api_create_path_visualization, api_follow_path_2d,
        # api_follow_path_3d, api_stop_path_movement) were removed here.
        # Reasons: the platform-helper set duplicated `multiplatform`'s operations
        # one-for-one; the api_* set duplicated `unity_api`'s operations but was
        # strictly worse (every flat version unconditionally returned "not
        # implemented", even for get_scene_objects/modify_object, which unity_api
        # now actually performs via the live bridge). Their private backing
        # methods on this class (_api_execute_method etc., all equally stale
        # stubs) were removed with them; the real, live implementations remain in
        # tools/portmanteau/unity_api.py, untouched. Use `multiplatform(operation=...)`
        # and `unity_api(operation=...)` instead. See TODO.md for the full record.


    async def run_stdio(self):
        """Run server in stdio mode."""
        # Updated for fastmcp 3.2.0+
        await run_server_async(self.app, server_name="unity3d-mcp")

    async def run_http(self, host: str = "127.0.0.1", port: int = 10831):
        """Run server in HTTP mode with combined MCP + Chat API."""
        try:
            import uvicorn
            from starlette.applications import Starlette
            from starlette.routing import Mount, Route

            from unity3d_mcp.chat_api import chat_app as _chat_app

            mcp_asgi = self.app.http_app()

            # Quick health endpoint
            async def _health(request):
                from starlette.responses import JSONResponse
                return JSONResponse({"status": "ok", "server": "unity3d-mcp"})

            combined = Starlette(routes=[
                Mount("/mcp", app=mcp_asgi),
                Mount("/api", app=_chat_app),
                Route("/api/health", endpoint=_health, methods=["GET"]),
                Route("/health", endpoint=_health, methods=["GET"]),
            ])

            logger.info(f"Starting Unity3D MCP + Chat on http://{host}:{port}")
            config = uvicorn.Config(combined, host=host, port=port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
        except Exception as e:
            logger.error("Failed to run HTTP mode", error=str(e))
            raise

    async def run_dual(self):
        """Run server in dual stdio + HTTP mode."""
        # Dual mode might not be supported in the same way.
        # Fallback to stdio for now to ensure basic functionality.
        logger.warning("Dual mode not fully supported - falling back to stdio")
        run_server(self, server_name="unity3d-mcp")


def create_app(config: Unity3DConfig | None = None) -> Unity3DMCP:
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
1. Create the project directory using `unity_core(operation="create_project")`.
2. Launch the Unity Editor via `unity_core(operation="launch_editor")`.
3. Set the build target to 'StandaloneWindows64' if applicable (`unity_build(operation="build_project")`).
4. Verify project health after initialization.
"""


@app.prompt()
async def vrc_avatar_workflow(avatar_name: str, vrm_path: str) -> str:
    """Step-by-step instructions for the VRM-to-VRChat avatar optimization pipeline."""
    return f"""Optimize the VRM avatar '{avatar_name}' from '{vrm_path}' for VRChat.
Workflow:
1. Import the VRM asset using `unity_avatar(operation="import_vrm")`.
2. Apply texture/platform optimizations via `unity_asset(operation="optimize_textures")`.
3. Run a preflight check via `unity_validation(operation="validate_avatar")`, then
   confirm upload readiness with `vrchat(operation="validate_avatar")`.
4. Report any validation errors that might block the upload.
"""


# --- SOTA 2026 Agentic Workflow (FastMCP 3.2.0+ SEP-1577) ---

# --- SOTA 2026 Dual-Mode Tools (Hands-In / Hands-Off) ---

_bridge_client = UnityBridgeClient()

# NOTE (2026-07-18): unity3d_bridge_status and unity3d_editor_api were removed
# from here. Both duplicated the `unity_bridge` portmanteau tool
# (tools/portmanteau/unity_bridge.py) almost exactly (status/ping/get_hierarchy/
# create_object/delete_object/transform_object). The one real gap,
# capture_game_view, has been ported into unity_bridge as an operation.
# Use unity_bridge(operation="status") and unity_bridge(operation=...) instead.
# See TODO.md for the full record.


@app.tool()
async def unity3d_disk_api(
    operation: str,
    file_path: str,
    component_type: str | None = None,
    property_name: str | None = None,
    new_value: str | None = None,
) -> dict[str, Any]:
    """[Hands-Off] Manipulate Unity project assets directly on disk without Unity running.

    Args:
        operation: inspect_file, list_textures, modify_yaml
        file_path: Absolute path to the .unity, .prefab, or .asset file
        component_type: YAML component type for modify_yaml
        property_name: Property name for modify_yaml
        new_value: New property value for modify_yaml
    """
    if operation == "inspect_file":
        return UnityDiskOps.inspect_file(file_path)
    elif operation == "list_textures":
        return {"textures": UnityDiskOps.list_textures(file_path)}
    elif operation == "modify_yaml":
        return UnityDiskOps.modify_yaml_property(file_path, component_type, property_name, new_value)
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
    * unity_bridge: Real-time session control (requires bridge; operations include capture_game_view)
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
        error_msg = f"Agentic workflow failed: {e!s}"
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
