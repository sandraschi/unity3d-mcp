"""Bridge-backed play mode simulation runner for unity_jobs."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from unity3d_mcp.tools.portmanteau.unity_api_bridge import UnityBridgeClient
from unity3d_mcp.utils.unity_runtime import bridge_available, get_bridge_client

logger = logging.getLogger(__name__)


async def run_bridge_simulation(
    *,
    duration: float = 1.0,
    record_data: bool = False,
    timeout: float = 60.0,
    bridge: UnityBridgeClient | None = None,
    poll_interval: float = 0.25,
) -> dict[str, Any]:
    """Start play mode simulation via bridge and poll until complete."""
    client = bridge or get_bridge_client()
    if not await bridge_available(client):
        return {
            "success": False,
            "mode": "bridge",
            "error": "Unity Editor bridge not connected for simulation",
        }

    start = await client.execute_command(
        "run_simulation",
        duration=duration,
        record_data=1 if record_data else 0,
    )
    if start.get("error"):
        return {"success": False, "mode": "bridge", "error": start.get("error"), "start": start}

    deadline = asyncio.get_event_loop().time() + timeout
    last_status: dict[str, Any] = start
    saw_running = start.get("state") == "running" or start.get("status") == "simulation_started"

    while asyncio.get_event_loop().time() < deadline:
        status = await client.execute_command("simulation_status")
        last_status = status
        if status.get("error"):
            return {"success": False, "mode": "bridge", "error": status["error"], "status": status}
        state = status.get("state") or status.get("status")
        if state == "running":
            saw_running = True
        if saw_running and state == "idle":
            return {
                "success": True,
                "mode": "bridge",
                "duration": duration,
                "record_data": record_data,
                "status": status,
            }
        if state == "failed":
            return {
                "success": False,
                "mode": "bridge",
                "error": status.get("message") or "Simulation failed",
                "status": status,
            }
        await asyncio.sleep(poll_interval)

    await client.execute_command("stop_simulation")
    return {
        "success": False,
        "mode": "bridge",
        "error": f"Simulation timed out after {timeout}s",
        "last_status": last_status,
    }
