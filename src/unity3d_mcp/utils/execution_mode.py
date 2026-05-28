"""Dual-mode execution helpers (Hands-In live GUI vs Hands-Off headless/disk)."""

from __future__ import annotations

from typing import Any

from unity3d_mcp.utils.telemetry import set_bridge_connected, set_execution_mode
from unity3d_mcp.utils.unity_runtime import bridge_available, get_bridge_client


async def describe_execution_mode() -> dict[str, Any]:
    """Return current Hands-In vs Hands-Off mode for agents and webapp."""
    bridge = get_bridge_client()
    alive = await bridge_available(bridge)
    set_bridge_connected(alive)
    set_execution_mode(alive)

    if alive:
        return {
            "success": True,
            "mode": "hands_in",
            "label": "Hands-In (Live GUI)",
            "bridge_connected": True,
            "bridge_port": bridge.port,
            "live_capabilities": [
                "Watch hierarchy/transform changes in Unity Editor",
                "Play-mode simulation (unity_jobs simulation / unity_api run_simulation)",
                "Game view and multi-angle captures",
                "validate_scene with live poly/material counts",
            ],
            "headless_note": "Build jobs still spawn Unity -batchmode (no Editor GUI for builds).",
        }

    return {
        "success": True,
        "mode": "hands_off",
        "label": "Hands-Off (Headless / Disk)",
        "bridge_connected": False,
        "bridge_port": bridge.port,
        "available_capabilities": [
            "unity3d_disk_api / UnityPy asset inspection and edits",
            "unity_import file copy into Assets/",
            "unity_jobs build (Unity -batchmode -nographics)",
            "Disk validation and fleet HTTP import/export",
        ],
        "live_gui_hint": (
            "Open Unity Editor, copy MCPBridge.cs to Assets/Editor/, "
            "then unity_bridge operation=execution_mode should report hands_in."
        ),
    }
