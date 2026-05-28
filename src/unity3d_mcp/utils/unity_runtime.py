"""Bridge-first Unity Editor execution helpers."""

from __future__ import annotations

import logging
import os
from typing import Any

from unity3d_mcp.tools.portmanteau.unity_api_bridge import UnityBridgeClient

logger = logging.getLogger(__name__)

_default_bridge: UnityBridgeClient | None = None


def get_bridge_client() -> UnityBridgeClient:
    """Return shared bridge client (configurable via env)."""
    global _default_bridge
    if _default_bridge is None:
        host = os.getenv("UNITY3D_MCP_BRIDGE_HOST", "localhost")
        port = int(os.getenv("UNITY3D_MCP_BRIDGE_PORT", "10835"))
        _default_bridge = UnityBridgeClient(host=host, port=port)
    return _default_bridge


async def bridge_available(bridge: UnityBridgeClient | None = None) -> bool:
    """True when MCPBridge.cs HTTP listener responds to ping."""
    client = bridge or get_bridge_client()
    try:
        return await client.is_alive()
    except Exception as exc:
        logger.warning("Bridge availability check failed: %s", exc)
        return False


async def execute_bridge_action(
    action: str,
    *,
    prefer_bridge: bool = True,
    bridge: UnityBridgeClient | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a bridge action when live Editor session is available."""
    if not prefer_bridge:
        return {
            "success": False,
            "mode": "bridge_skipped",
            "error": "Bridge execution disabled (prefer_bridge=False)",
        }

    client = bridge or get_bridge_client()
    if not await bridge_available(client):
        return {
            "success": False,
            "mode": "bridge",
            "error": (
                "Unity Editor bridge not connected. "
                "Install MCPBridge.cs under Assets/Editor and open Unity."
            ),
            "bridge_port": client.port if hasattr(client, "port") else 10835,
        }

    try:
        result = await client.execute_command(action, **kwargs)
    except Exception as exc:
        logger.exception("Bridge action %s failed", action)
        return {"success": False, "mode": "bridge", "error": str(exc), "action": action}

    if isinstance(result, dict) and result.get("error"):
        return {"success": False, "mode": "bridge", "action": action, **result}

    return {"success": True, "mode": "bridge", "action": action, "result": result}
