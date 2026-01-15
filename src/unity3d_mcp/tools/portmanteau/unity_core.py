"""
Unity Core Portmanteau Tool Manager

Consolidates core Unity Editor operations into a unified portmanteau interface.
"""

import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...core import ProjectManager, UnityEditorManager

logger = logging.getLogger(__name__)


class UnityCoreToolManager:
    """Portmanteau tool manager for core Unity operations."""

    def __init__(self, app: FastMCP, unity_editor: UnityEditorManager, project_manager: ProjectManager):
        """Initialize the Unity Core tool manager."""
        self.app = app
        self.unity_editor = unity_editor
        self.project_manager = project_manager

    def register_tools(self):
        """Register all Unity Core portmanteau tools."""

        @self.app.tool
        async def unity_core(
            operation: str,
            project_path: Optional[str] = None,
            project_name: Optional[str] = None,
            template: str = "3D",
            unity_version: str = "",
            batch_mode: bool = False,
            no_graphics: bool = False,
            class_name: Optional[str] = None,
            method_name: Optional[str] = None,
            parameters: Optional[Dict[str, Any]] = None,
            vrm_version: str = "vrm0",
            refresh_unity: bool = True,
        ) -> Dict[str, Any]:
            """Unity Core operations portmanteau tool.

            Consolidates core Unity Editor operations including project management,
            editor launching, method execution, and UniVRM handling.

            Args:
                operation: Operation to perform
                    - "launch_editor": Launch Unity Editor
                    - "create_project": Create new Unity project
                    - "execute_method": Execute Unity Editor method
                    - "check_univrm": Check if UniVRM is installed
                    - "install_univrm": Install UniVRM packages
                    - "create_project_with_univrm": Create project with UniVRM pre-installed
                project_path: Unity project path (required for most operations)
                project_name: Name for new project (for create operations)
                template: Project template ("3D", "2D", "URP", "HDRP", "VR")
                unity_version: Specific Unity version (empty for auto-detect)
                batch_mode: Run Unity in batch mode (no GUI)
                no_graphics: Run without graphics device
                class_name: C# class name (for execute_method)
                method_name: Method name (for execute_method)
                parameters: Parameters for method execution
                vrm_version: "vrm0" or "vrm1" (for VRM operations)
                refresh_unity: Whether to refresh Unity after install

            Returns:
                Operation-specific result dictionary
            """

            if operation == "launch_editor":
                if not project_path:
                    return {"success": False, "error": "project_path required for launch_editor"}
                return await self.unity_editor.launch_editor(
                    project_path, unity_version, batch_mode, no_graphics
                )

            elif operation == "create_project":
                if not project_name or not project_path:
                    return {"success": False, "error": "project_name and project_path required for create_project"}
                return await self.project_manager.create_project(
                    project_name, project_path, template, unity_version
                )

            elif operation == "execute_method":
                if not class_name or not method_name:
                    return {"success": False, "error": "class_name and method_name required for execute_method"}
                return await self.unity_editor.execute_method(
                    class_name, method_name, parameters or {}, project_path or ""
                )

            elif operation == "check_univrm":
                if not project_path:
                    return {"success": False, "error": "project_path required for check_univrm"}
                return await self.project_manager.check_univrm_installed(project_path)

            elif operation == "install_univrm":
                if not project_path:
                    return {"success": False, "error": "project_path required for install_univrm"}
                return await self.project_manager.install_univrm(
                    project_path, vrm_version, refresh_unity
                )

            elif operation == "create_project_with_univrm":
                if not project_name or not project_path:
                    return {"success": False, "error": "project_name and project_path required for create_project_with_univrm"}
                return await self.project_manager.create_project_with_univrm(
                    project_name, project_path, template, unity_version, vrm_version
                )

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "launch_editor", "create_project", "execute_method",
                        "check_univrm", "install_univrm", "create_project_with_univrm"
                    ]
                }