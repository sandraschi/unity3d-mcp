"""
VRChat Portmanteau Tool Manager

Consolidates VRChat SDK integration operations into a unified portmanteau interface.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from ...vrchat import VRChatSDKManager

logger = logging.getLogger(__name__)


class VRChatToolManager:
    """Portmanteau tool manager for VRChat operations."""

    def __init__(self, app: FastMCP, vrchat_sdk: VRChatSDKManager, config):
        """Initialize the VRChat tool manager."""
        self.app = app
        self.vrchat_sdk = vrchat_sdk
        self.config = config

    def register_tools(self):
        """Register all VRChat portmanteau tools."""

        @self.app.tool
        async def vrchat(
            operation: str,
            username: str = "",
            password: str = "",
            totp_code: str = "",
            project_path: str | None = None,
            avatar_prefab: str | None = None,
            avatar_name: str | None = None,
            description: str = "",
            tags: list[str] | None = None,
            release_status: str = "private",
            viewpoint_position: list[float] | None = None,
        ) -> dict[str, Any]:
            """VRChat operations portmanteau tool.

            Consolidates VRChat SDK integration including authentication,
            validation, and avatar uploading.

            Args:
                operation: Operation to perform
                    - "check_auth": Check VRChat authentication status
                    - "authenticate": Authenticate with VRChat
                    - "check_sdk": Check if VRChat SDK is installed
                    - "validate_avatar": Validate avatar against VRChat requirements
                    - "setup_descriptor": Setup VRC Avatar Descriptor component
                    - "upload_avatar": Upload avatar to VRChat platform
                username: VRChat account username (for authenticate)
                password: VRChat account password (for authenticate)
                totp_code: 2FA/TOTP code if 2FA is enabled (for authenticate)
                project_path: Unity project path (required for SDK/avatar operations)
                avatar_prefab: Path to avatar prefab (required for validate/setup/upload)
                avatar_name: Name for avatar on VRChat platform (required for upload)
                description: Description text for avatar page
                tags: List of tags for avatar categorization
                release_status: Release status ("private" or "public")
                viewpoint_position: Viewpoint position [x, y, z] (for setup_descriptor)

            Returns:
                Operation-specific result dictionary
            """

            if operation == "check_auth":
                return await self.vrchat_sdk.check_authentication()

            elif operation == "authenticate":
                return await self.vrchat_sdk.authenticate(
                    username=username or None,
                    password=password or None,
                    totp_code=totp_code or None,
                )

            elif operation == "check_sdk":
                if not project_path:
                    return {"success": False, "error": "project_path required for check_sdk"}
                return await self.vrchat_sdk.check_sdk_installed(project_path)

            elif operation == "validate_avatar":
                if not avatar_prefab:
                    return {"success": False, "error": "avatar_prefab required for validate_avatar"}
                project = project_path or self.config.project_path
                return await self.vrchat_sdk.validate_avatar(avatar_prefab, project)

            elif operation == "setup_descriptor":
                if not avatar_prefab:
                    return {"success": False, "error": "avatar_prefab required for setup_descriptor"}
                if viewpoint_position is None:
                    viewpoint_position = [0, 1.6, 0]
                return await self.vrchat_sdk.setup_avatar_descriptor(avatar_prefab, viewpoint_position)

            elif operation == "upload_avatar":
                if not avatar_prefab or not avatar_name:
                    return {"success": False, "error": "avatar_prefab and avatar_name required for upload_avatar"}
                return await self.vrchat_sdk.upload_avatar(
                    avatar_prefab=avatar_prefab,
                    avatar_name=avatar_name,
                    description=description,
                    tags=tags or [],
                    project_path=project_path or None,
                    release_status=release_status,
                )

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "check_auth",
                        "authenticate",
                        "check_sdk",
                        "validate_avatar",
                        "setup_descriptor",
                        "upload_avatar",
                    ],
                }
