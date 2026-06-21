"""Unity Editor bridge portmanteau tool."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

from ...utils.execution_mode import describe_execution_mode
from ...utils.telemetry import set_bridge_connected, set_execution_mode
from ...utils.unity_runtime import bridge_available, execute_bridge_action, get_bridge_client
from .unity_api_bridge import UnityBridgeClient

logger = logging.getLogger(__name__)


class UnityBridgeToolManager:
    """Portmanteau tool for live Unity Editor bridge operations."""

    def __init__(self, app: FastMCP, bridge: UnityBridgeClient | None = None) -> None:
        self.app = app
        self.bridge = bridge or get_bridge_client()

    def register_tools(self) -> None:
        @self.app.tool
        async def unity_bridge(
            operation: str,
            target: str | None = None,
            name: str | None = None,
            object_type: str = "GameObject",
            position: list[float] | None = None,
            rotation: list[float] | None = None,
        ) -> dict[str, Any]:
            """Live Unity Editor bridge (MCPBridge.cs on port 10835).

            Args:
                operation: status | execution_mode | ping | get_hierarchy
                    | create_object | delete_object | transform_object
                target: GameObject name or instance ID
                name: Name for create_object
                object_type: GameObject | Light | Camera
                position: [x, y, z] world position
                rotation: [x, y, z] euler rotation
            """
            if operation == "status":
                alive = await bridge_available(self.bridge)
                set_bridge_connected(alive)
                set_execution_mode(alive)
                return {
                    "success": True,
                    "status": "connected" if alive else "disconnected",
                    "mode": "hands_in" if alive else "hands_off",
                    "port": self.bridge.port,
                    "bridge_script": "MCPBridge.cs",
                    "instruction": "Copy src/unity3d_mcp/resources/MCPBridge.cs to Assets/Editor/",
                }

            if operation == "execution_mode":
                return await describe_execution_mode()

            action_map = {
                "ping": "ping",
                "get_hierarchy": "get_hierarchy",
                "create_object": "create_object",
                "delete_object": "delete_object",
                "transform_object": "transform_object",
            }
            if operation not in action_map:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [*list(action_map.keys()), "status", "execution_mode"],
                }

            kwargs: dict[str, Any] = {}
            if target is not None:
                kwargs["target"] = target
            if name is not None:
                kwargs["name"] = name
            if object_type:
                kwargs["type"] = object_type
            if position is not None:
                kwargs["position"] = position
            if rotation is not None:
                kwargs["rotation"] = rotation

            result = await execute_bridge_action(action_map[operation], bridge=self.bridge, **kwargs)
            if operation == "ping" and result.get("success"):
                set_bridge_connected(True)
            return result
