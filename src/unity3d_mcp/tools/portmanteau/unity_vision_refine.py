"""Unity agent vision refinement portmanteau tool."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...utils.vision_refine import (
    apply_bridge_commands,
    build_review_bundle,
    capture_viewport,
)
from .unity_api_bridge import UnityBridgeClient
from ...utils.unity_runtime import get_bridge_client

logger = logging.getLogger(__name__)


class UnityVisionRefineToolManager:
    """Portmanteau tool for agent vision review loops in Unity."""

    def __init__(self, app: FastMCP, bridge: UnityBridgeClient | None = None) -> None:
        self.app = app
        self.bridge = bridge or get_bridge_client()

    def register_tools(self) -> None:
        @self.app.tool
        async def unity_vision_refine(
            operation: str = "capture",
            output_path: str = "",
            output_dir: str = "",
            goal: str = "",
            commands_json: str = "",
            include_multi_angle: bool = True,
            angles: int = 4,
            width: int = 1280,
            height: int = 720,
            include_base64: bool = True,
        ) -> Dict[str, Any]:
            """Agent vision refinement: capture, review bundle, apply bridge fixes.

            Operations:
            - capture: single viewport PNG (+ optional base64)
            - review_bundle: screenshot + multi-angle stills + scene summary + prompt
            - apply_bridge_commands: JSON list of bridge actions after vision review
            """
            try:
                if operation == "capture":
                    if not output_path:
                        return {"success": False, "error": "output_path required for capture"}
                    return await capture_viewport(
                        output_path=output_path,
                        width=width,
                        height=height,
                        include_base64=include_base64,
                        bridge=self.bridge,
                    )

                if operation == "review_bundle":
                    if not output_dir:
                        return {"success": False, "error": "output_dir required for review_bundle"}
                    return await build_review_bundle(
                        output_dir=output_dir,
                        goal=goal,
                        include_multi_angle=include_multi_angle,
                        angles=angles,
                        width=width,
                        height=height,
                        bridge=self.bridge,
                    )

                if operation == "apply_bridge_commands":
                    if not commands_json.strip():
                        return {"success": False, "error": "commands_json required"}
                    try:
                        parsed = json.loads(commands_json)
                    except json.JSONDecodeError as exc:
                        return {"success": False, "error": f"Invalid JSON: {exc}"}
                    if isinstance(parsed, dict) and "commands" in parsed:
                        commands = parsed["commands"]
                    elif isinstance(parsed, list):
                        commands = parsed
                    else:
                        return {"success": False, "error": "commands_json must be a list or {commands: [...]}"}
                    return await apply_bridge_commands(commands, bridge=self.bridge)

                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["capture", "review_bundle", "apply_bridge_commands"],
                }
            except Exception as exc:
                logger.exception("unity_vision_refine failed: %s", exc)
                return {"success": False, "error": str(exc), "operation": operation}
