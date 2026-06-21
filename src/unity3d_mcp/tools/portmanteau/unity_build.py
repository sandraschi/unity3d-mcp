"""
Unity Build Portmanteau Tool Manager

Consolidates build pipeline operations into a unified portmanteau interface.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from ...build import BuildManager

logger = logging.getLogger(__name__)


class UnityBuildToolManager:
    """Portmanteau tool manager for Unity build operations."""

    def __init__(self, app: FastMCP, build_manager: BuildManager):
        """Initialize the Unity Build tool manager."""
        self.app = app
        self.build_manager = build_manager

    def register_tools(self):
        """Register all Unity Build portmanteau tools."""

        @self.app.tool
        async def unity_build(
            operation: str,
            project_path: str | None = None,
            build_target: str | None = None,
            output_path: str | None = None,
            development_build: bool = False,
        ) -> dict[str, Any]:
            """Unity Build operations portmanteau tool.

            Consolidates build pipeline operations for Unity projects.

            Args:
                operation: Operation to perform
                    - "build_project": Build Unity project for target platform
                project_path: Unity project path to build (required for build_project)
                build_target: Target platform ("StandaloneWindows64", "Android", "iOS", "WebGL", etc.)
                output_path: Directory where build will be created
                development_build: Enable development build (debugging, profiler)

            Returns:
                Operation-specific result dictionary
            """

            if operation == "build_project":
                if not project_path or not build_target or not output_path:
                    return {
                        "success": False,
                        "error": "project_path, build_target, and output_path required for build_project",
                    }
                return await self.build_manager.build_project(
                    project_path, build_target, output_path, development_build
                )

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["build_project"],
                }
