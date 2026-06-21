"""
Multi-Platform Portmanteau Tool Manager

Consolidates multi-platform social VR operations into a unified portmanteau interface.
Supports ChilloutVR, Resonite, and Cluster platforms.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from ...platforms import PlatformManager

logger = logging.getLogger(__name__)


class PlatformToolManager:
    """Portmanteau tool manager for multi-platform social VR operations."""

    def __init__(self, app: FastMCP, platforms: PlatformManager, vrchat_sdk=None, bridge=None):
        """Initialize the Platform tool manager."""
        self.app = app
        self.platforms = platforms
        self.vrchat_sdk = vrchat_sdk
        self.bridge = bridge

    def register_tools(self):
        """Register all multi-platform portmanteau tools."""

        @self.app.tool
        async def multiplatform(
            operation: str,
            platform: str = "",
            project_path: str | None = None,
            avatar_object: str | None = None,
            avatar_name: str | None = None,
            eye_height: float = 1.6,
            model_path: str | None = None,
            optimize: bool = True,
            asset_folder: str | None = None,
        ) -> dict[str, Any]:
            """Multi-platform social VR operations portmanteau tool.

            Consolidates operations for ChilloutVR, Resonite, and Cluster platforms.

            Args:
                operation: Operation to perform
                    - "list_platforms": List all supported social VR platforms
                    - "check_sdk": Check if platform SDK is installed
                    - "check_cck": Check if ChilloutVR CCK is installed
                    - "setup_cvr_avatar": Setup CVR Avatar component
                    - "validate_cvr": Validate avatar for ChilloutVR
                    - "prepare_resonite": Prepare model for Resonite import
                    - "check_resonite_compat": Check Resonite compatibility
                    - "check_cluster_kit": Check if Cluster Creator Kit is installed
                    - "prepare_cluster": Prepare avatar for Cluster upload
                    - "audit_all": Unified VRChat + CVR + Resonite + Cluster preflight audit
                platform: Platform name ("vrchat", "chilloutvr", "cluster", "resonite")
                project_path: Unity project path (required for most operations)
                avatar_object: Avatar GameObject name (for CVR operations)
                avatar_name: Avatar name (for validation operations)
                eye_height: Avatar eye height in meters (for CVR setup)
                model_path: Path to .vrm or .glb file (for Resonite operations)
                optimize: Apply optimization (for Resonite operations)
                asset_folder: Folder containing assets (for Cluster operations)

            Returns:
                Operation-specific result dictionary
            """

            if operation == "list_platforms":
                return await self.platforms.list_supported_platforms()

            elif operation == "check_sdk":
                if not platform or not project_path:
                    return {"success": False, "error": "platform and project_path required for check_sdk"}
                return await self.platforms.check_platform_sdk(platform, project_path)

            elif operation == "check_cck":
                if not project_path:
                    return {"success": False, "error": "project_path required for check_cck"}
                return await self.platforms.chillout.check_cck_installed(project_path)

            elif operation == "setup_cvr_avatar":
                if not avatar_object or not project_path:
                    return {"success": False, "error": "avatar_object and project_path required for setup_cvr_avatar"}
                return await self.platforms.chillout.setup_cvr_avatar(avatar_object, project_path, eye_height)

            elif operation == "validate_cvr":
                if not avatar_name or not project_path:
                    return {"success": False, "error": "avatar_name and project_path required for validate_cvr"}
                return await self.platforms.chillout.validate_for_chillout(avatar_name, project_path)

            elif operation == "prepare_resonite":
                if not model_path:
                    return {"success": False, "error": "model_path required for prepare_resonite"}
                return await self.platforms.resonite.prepare_for_resonite(model_path, optimize)

            elif operation == "check_resonite_compat":
                if not model_path:
                    return {"success": False, "error": "model_path required for check_resonite_compat"}
                return await self.platforms.resonite.check_resonite_compatibility(model_path)

            elif operation == "check_cluster_kit":
                if not project_path:
                    return {"success": False, "error": "project_path required for check_cluster_kit"}
                return await self.platforms.cluster.check_cluster_kit_installed(project_path)

            elif operation == "prepare_cluster":
                if not asset_folder or not project_path:
                    return {"success": False, "error": "asset_folder and project_path required for prepare_cluster"}
                return await self.platforms.cluster.prepare_for_cluster(asset_folder, project_path)

            elif operation == "audit_all":
                from ...utils.platform_audit import run_unified_audit
                from ...utils.scene_validator import validate_scene_via_bridge

                if self.vrchat_sdk is None:
                    return {"success": False, "error": "VRChat SDK manager not configured for audit_all"}

                scene_metrics = None
                if self.bridge is not None:
                    bridge_report = await validate_scene_via_bridge(self.bridge, target_platform=platform or "vrchat")
                    if bridge_report.get("success") and bridge_report.get("metrics"):
                        scene_metrics = {
                            "triangle_count": bridge_report["metrics"].get("polygons", 0),
                            "material_count": bridge_report["metrics"].get("materials", 0),
                            "missing_script_count": bridge_report["metrics"].get("missing_scripts", 0),
                            "mesh_count": bridge_report["metrics"].get("mesh_count", 0),
                            "object_count": bridge_report["metrics"].get("object_count", 0),
                            "objects_with_missing_scripts": bridge_report.get(
                                "objects_with_missing_scripts", []
                            ),
                        }

                return await run_unified_audit(
                    platforms=self.platforms,
                    vrchat_sdk=self.vrchat_sdk,
                    project_path=project_path,
                    avatar_prefab=avatar_object or avatar_name,
                    model_path=model_path,
                    scene_metrics=scene_metrics,
                )

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "list_platforms",
                        "check_sdk",
                        "check_cck",
                        "setup_cvr_avatar",
                        "validate_cvr",
                        "prepare_resonite",
                        "check_resonite_compat",
                        "check_cluster_kit",
                        "prepare_cluster",
                        "audit_all",
                    ],
                }
