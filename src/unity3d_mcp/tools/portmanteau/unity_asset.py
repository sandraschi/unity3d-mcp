"""
Unity Asset Portmanteau Tool Manager

Consolidates asset management operations into a unified portmanteau interface.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from ...assets import AssetManager

logger = logging.getLogger(__name__)


class UnityAssetToolManager:
    """Portmanteau tool manager for Unity asset operations."""

    def __init__(self, app: FastMCP, asset_manager: AssetManager):
        """Initialize the Unity Asset tool manager."""
        self.app = app
        self.asset_manager = asset_manager

    def register_tools(self):
        """Register all Unity Asset portmanteau tools."""

        @self.app.tool
        async def unity_asset(
            operation: str,
            texture_paths: Optional[List[str]] = None,
            platform: str = "PC",
            quality: str = "High",
        ) -> Dict[str, Any]:
            """Unity Asset operations portmanteau tool.

            Consolidates asset management operations including texture optimization.

            Args:
                operation: Operation to perform
                    - "optimize_textures": Optimize textures for target platform
                texture_paths: List of texture asset paths in Unity project (required for optimize_textures)
                platform: Target platform ("PC", "Android", "iOS", "WebGL", "Quest")
                quality: Quality preset ("Low", "Medium", "High", "Ultra")

            Returns:
                Operation-specific result dictionary
            """

            if operation == "optimize_textures":
                if not texture_paths:
                    return {"success": False, "error": "texture_paths required for optimize_textures"}
                return await self.asset_manager.optimize_textures(texture_paths, platform, quality)

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["optimize_textures"]
                }