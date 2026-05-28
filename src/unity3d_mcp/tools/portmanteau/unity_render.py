"""Unity render and vision capture portmanteau tool."""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...utils.unity_runtime import bridge_available, execute_bridge_action, get_bridge_client
from .unity_api_bridge import UnityBridgeClient

logger = logging.getLogger(__name__)


class UnityRenderToolManager:
    """Portmanteau tool for agent vision capture from Unity Editor."""

    def __init__(self, app: FastMCP, bridge: UnityBridgeClient | None = None) -> None:
        self.app = app
        self.bridge = bridge or get_bridge_client()

    def register_tools(self) -> None:
        @self.app.tool
        async def unity_render(
            operation: str,
            output_path: Optional[str] = None,
            output_dir: Optional[str] = None,
            width: int = 1920,
            height: int = 1080,
            angles: int = 4,
            include_base64: bool = False,
        ) -> Dict[str, Any]:
            """Capture Unity scene views for agent vision loops.

            Args:
                operation: capture_game_view | capture_multi_angle | get_scene_summary | bridge_status
                output_path: PNG output path (capture_game_view)
                output_dir: Directory for multi-angle stills
                width: Capture width in pixels
                height: Capture height in pixels
                angles: Number of angles for capture_multi_angle
                include_base64: Include base64 PNG in response for LLM vision
            """
            if operation == "bridge_status":
                alive = await bridge_available(self.bridge)
                return {
                    "success": True,
                    "bridge_connected": alive,
                    "port": self.bridge.port,
                }

            if operation == "get_scene_summary":
                result = await execute_bridge_action("get_scene_summary", bridge=self.bridge)
                if result.get("success"):
                    return {"success": True, "scene_summary": result.get("result")}
                return result

            if operation == "capture_multi_angle":
                if not output_dir:
                    return {"success": False, "error": "output_dir required for capture_multi_angle"}
                out = Path(output_dir)
                try:
                    out.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    return {"success": False, "error": f"Cannot create output directory: {exc}"}
                result = await execute_bridge_action(
                    "capture_multi_angle",
                    bridge=self.bridge,
                    output_dir=str(out),
                    angles=angles,
                    width=width,
                    height=height,
                )
                if not result.get("success"):
                    return result
                return {
                    "success": True,
                    "mode": "bridge",
                    "output_dir": str(out),
                    "angles": angles,
                    "bridge_result": result.get("result"),
                }

            if operation != "capture_game_view":
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "capture_game_view",
                        "capture_multi_angle",
                        "get_scene_summary",
                        "bridge_status",
                    ],
                }

            if not output_path:
                return {"success": False, "error": "output_path required for capture_game_view"}

            path = Path(output_path)
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                return {"success": False, "error": f"Cannot create output directory: {exc}"}

            result = await execute_bridge_action(
                "capture_game_view",
                bridge=self.bridge,
                output_path=str(path),
                width=width,
                height=height,
            )
            if not result.get("success"):
                return result

            payload: Dict[str, Any] = {
                "success": True,
                "mode": "bridge",
                "operation": operation,
                "output_path": str(path),
                "width": width,
                "height": height,
                "bridge_result": result.get("result"),
            }

            if include_base64 and path.is_file():
                try:
                    payload["image_base64"] = base64.b64encode(path.read_bytes()).decode("ascii")
                    payload["mime_type"] = "image/png"
                except OSError as exc:
                    logger.warning("Failed to read capture for base64: %s", exc)
                    payload["base64_error"] = str(exc)

            return payload
