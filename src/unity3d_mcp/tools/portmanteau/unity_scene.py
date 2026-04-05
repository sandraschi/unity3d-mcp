"""
Unity Scene Portmanteau Tool Manager

Consolidates scene management operations into a unified portmanteau interface.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from ...core import SceneManager

logger = logging.getLogger(__name__)


class UnitySceneToolManager:
    """Portmanteau tool manager for Unity scene operations."""

    def __init__(self, app: FastMCP, scene_manager: SceneManager):
        """Initialize the Unity Scene tool manager."""
        self.app = app
        self.scene_manager = scene_manager

    def register_tools(self):
        """Register all Unity Scene portmanteau tools."""

        @self.app.tool
        async def unity_scene(
            operation: str,
            light_name: Optional[str] = None,
            light_type: str = "Spot",
            color: List[float] = None,
            intensity: float = 1.0,
            position: Optional[Dict[str, float]] = None,
        ) -> Dict[str, Any]:
            """Unity Scene operations portmanteau tool.

            Consolidates scene management operations including lighting and scene objects.

            Args:
                operation: Operation to perform
                    - "create_light": Create a light in the current scene
                light_name: Name of the light GameObject (required for create_light)
                light_type: Type of light ("Spot", "Directional", "Point", "Area")
                color: RGBA color values [r, g, b, a] (default: [1.0, 1.0, 1.0, 1.0])
                intensity: Light intensity value
                position: Position dictionary {"x": 0, "y": 0, "z": 0}

            Returns:
                Operation-specific result dictionary
            """

            if color is None:
                color = [1.0, 1.0, 1.0, 1.0]

            if operation == "create_light":
                if not light_name:
                    return {"success": False, "error": "light_name required for create_light"}
                return await self.scene_manager.create_light(light_name, light_type, color, intensity, position)

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["create_light"],
                }
