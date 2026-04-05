"""
World Labs Portmanteau Tool Manager

Consolidates World Labs (Marble/Chisel) integration operations into a unified portmanteau interface.
"""

import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...worldlabs import WorldLabsManager

logger = logging.getLogger(__name__)


class WorldLabsToolManager:
    """Portmanteau tool manager for World Labs operations."""

    def __init__(self, app: FastMCP, worldlabs: WorldLabsManager):
        """Initialize the World Labs tool manager."""
        self.app = app
        self.worldlabs = worldlabs

    def register_tools(self):
        """Register all World Labs portmanteau tools."""

        @self.app.tool
        async def worldlabs(
            operation: str,
            source_path: Optional[str] = None,
            project_path: Optional[str] = None,
            asset_name: str = "",
            include_colliders: bool = True,
            optimize_for_vrchat: bool = False,
            target_polygon_count: int = 50000,
        ) -> Dict[str, Any]:
            """World Labs operations portmanteau tool.

            Consolidates World Labs Marble/Chisel operations for 3D world import
            and Gaussian splatting integration.

            Args:
                operation: Operation to perform
                    - "import_marble": Import Marble-generated 3D world
                    - "check_gaussian": Check if Gaussian Splatting renderer is installed
                    - "install_gaussian": Install Gaussian Splatting renderer
                    - "optimize_for_vrchat": Get VRChat optimization recommendations
                source_path: Path to Marble export directory or zip (required for import_marble)
                project_path: Unity project path (required for most operations)
                asset_name: Name for imported assets (empty for auto-generate)
                include_colliders: Generate collision meshes from Marble collider export
                optimize_for_vrchat: Apply VRChat world optimization
                target_polygon_count: Target polygon count for VRChat optimization

            Returns:
                Operation-specific result dictionary
            """

            if operation == "import_marble":
                if not source_path or not project_path:
                    return {"success": False, "error": "source_path and project_path required for import_marble"}
                return await self.worldlabs.import_marble_world(
                    source_path, project_path, asset_name, include_colliders, optimize_for_vrchat
                )

            elif operation == "check_gaussian":
                if not project_path:
                    return {"success": False, "error": "project_path required for check_gaussian"}
                return await self.worldlabs.check_gaussian_splatting_installed(project_path)

            elif operation == "install_gaussian":
                if not project_path:
                    return {"success": False, "error": "project_path required for install_gaussian"}
                return await self.worldlabs.install_gaussian_splatting(project_path)

            elif operation == "optimize_for_vrchat":
                if not project_path or not asset_name:
                    return {"success": False, "error": "project_path and asset_name required for optimize_for_vrchat"}
                return await self.worldlabs.optimize_for_vrchat(project_path, asset_name, target_polygon_count)

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "import_marble",
                        "check_gaussian",
                        "install_gaussian",
                        "optimize_for_vrchat",
                    ],
                }
