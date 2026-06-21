"""Fleet import portmanteau tool (Blender -> Unity handoff)."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

from ...tools.import_export_manager import ImportExportManager
from ...utils.fleet_import import SUPPORTED_FLEET_FORMATS, import_blender_asset, import_fleet_batch

logger = logging.getLogger(__name__)


class UnityImportToolManager:
    """Portmanteau tool for fleet asset import into Unity projects."""

    def __init__(self, app: FastMCP, import_export_manager: ImportExportManager) -> None:
        self.app = app
        self.import_export = import_export_manager

    def register_tools(self) -> None:
        @self.app.tool
        async def unity_import(
            operation: str,
            file_path: str | None = None,
            project_path: str | None = None,
            input_dir: str | None = None,
            pattern: str = "*.glb",
            assets_subdir: str = "BlenderImports",
            model_format: str | None = None,
        ) -> dict[str, Any]:
            """Import assets from Blender/fleet export paths into a Unity project.

            Operations:
            - import_blender: single GLB/VRM/FBX/OBJ from blender-mcp export
            - import_fleet_batch: glob import from export directory
            - list_formats: supported fleet interchange formats
            """
            try:
                if operation == "list_formats":
                    return {
                        "success": True,
                        "formats": list(SUPPORTED_FLEET_FORMATS),
                        "default_assets_subdir": assets_subdir,
                        "hint": "Export from blender-mcp with blender_export (GLB/VRM), then import here.",
                    }

                if operation == "import_blender":
                    if not file_path or not project_path:
                        return {
                            "success": False,
                            "error": "file_path and project_path required for import_blender",
                        }
                    return await import_blender_asset(
                        self.import_export,
                        file_path=file_path,
                        project_path=project_path,
                        assets_subdir=assets_subdir,
                    )

                if operation == "import_fleet_batch":
                    if not input_dir or not project_path:
                        return {
                            "success": False,
                            "error": "input_dir and project_path required for import_fleet_batch",
                        }
                    return await import_fleet_batch(
                        self.import_export,
                        input_dir=input_dir,
                        project_path=project_path,
                        pattern=pattern,
                        assets_subdir=assets_subdir,
                    )

                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["import_blender", "import_fleet_batch", "list_formats"],
                }
            except Exception as exc:
                logger.exception("unity_import failed: %s", exc)
                return {"success": False, "error": str(exc), "operation": operation}
