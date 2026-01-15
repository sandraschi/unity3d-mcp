"""
Unity Avatar Portmanteau Tool Manager

Consolidates VRM avatar and animation operations into a unified portmanteau interface.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from ...avatar import AnimationManager, VRMAvatarManager

logger = logging.getLogger(__name__)


class UnityAvatarToolManager:
    """Portmanteau tool manager for Unity avatar operations."""

    def __init__(self, app: FastMCP, vrm_avatar: VRMAvatarManager, animation: AnimationManager):
        """Initialize the Unity Avatar tool manager."""
        self.app = app
        self.vrm_avatar = vrm_avatar
        self.animation = animation

    def register_tools(self):
        """Register all Unity Avatar portmanteau tools."""

        @self.app.tool
        async def unity_avatar(
            operation: str,
            vrm_path: Optional[str] = None,
            project_path: Optional[str] = None,
            optimize_for_vrchat: bool = True,
            create_prefab: bool = True,
            avatar_path: Optional[str] = None,
            animator_type: str = "humanoid",
            include_facial: bool = True,
        ) -> Dict[str, Any]:
            """Unity Avatar operations portmanteau tool.

            Consolidates VRM avatar import and animation setup operations.

            Args:
                operation: Operation to perform
                    - "import_vrm": Import VRM avatar into Unity project
                    - "setup_animator": Setup animator controller for avatar
                vrm_path: Path to .vrm file to import (required for import_vrm)
                project_path: Unity project path (required for import_vrm)
                optimize_for_vrchat: Apply VRChat optimization for import_vrm
                create_prefab: Create Unity prefab from imported avatar
                avatar_path: Asset path to avatar in Unity project (required for setup_animator)
                animator_type: Animator rig type ("humanoid" or "generic")
                include_facial: Add facial animation blend shapes support

            Returns:
                Operation-specific result dictionary
            """

            if operation == "import_vrm":
                if not vrm_path or not project_path:
                    return {"success": False, "error": "vrm_path and project_path required for import_vrm"}
                return await self.vrm_avatar.import_vrm(
                    vrm_path, project_path, optimize_for_vrchat, create_prefab
                )

            elif operation == "setup_animator":
                if not avatar_path:
                    return {"success": False, "error": "avatar_path required for setup_animator"}
                return await self.animation.setup_animator(avatar_path, animator_type, include_facial)

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["import_vrm", "setup_animator"]
                }