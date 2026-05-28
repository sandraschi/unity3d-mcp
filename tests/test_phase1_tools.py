"""Tests for Phase 1 bridge wiring, vision capture, and telemetry."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestUnityRuntime:
    @pytest.mark.asyncio
    async def test_bridge_unavailable_returns_error(self):
        from unity3d_mcp.utils.unity_runtime import execute_bridge_action

        bridge = MagicMock()
        bridge.is_alive = AsyncMock(return_value=False)
        bridge.port = 10835

        result = await execute_bridge_action("ping", bridge=bridge)
        assert result["success"] is False
        assert result["mode"] == "bridge"

    @pytest.mark.asyncio
    async def test_bridge_action_success(self):
        from unity3d_mcp.utils.unity_runtime import execute_bridge_action

        bridge = MagicMock()
        bridge.is_alive = AsyncMock(return_value=True)
        bridge.execute_command = AsyncMock(return_value={"status": "ok"})
        bridge.port = 10835

        result = await execute_bridge_action("ping", bridge=bridge)
        assert result["success"] is True
        assert result["result"]["status"] == "ok"


class TestUnityApiBridgeWiring:
    @pytest.mark.asyncio
    async def test_get_scene_objects_uses_hierarchy(self):
        from unity3d_mcp.tools.portmanteau.unity_api import UnityAPIToolManager

        app = MagicMock()
        manager = UnityAPIToolManager(app)
        with patch(
            "unity3d_mcp.tools.portmanteau.unity_api.execute_bridge_action",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "result": {"objects": [{"name": "Main Camera", "id": "1"}]},
                }
            ),
        ):
            result = await manager._api_get_scene_objects(None, None, None)
        assert result["success"] is True
        assert result["object_count"] == 1

    @pytest.mark.asyncio
    async def test_modify_object_transform(self):
        from unity3d_mcp.tools.portmanteau.unity_api import UnityAPIToolManager

        app = MagicMock()
        manager = UnityAPIToolManager(app)
        with patch(
            "unity3d_mcp.tools.portmanteau.unity_api.execute_bridge_action",
            new=AsyncMock(return_value={"success": True, "result": {"status": "success"}}),
        ) as mock_exec:
            result = await manager._api_modify_object(
                "Player",
                {"position": [0, 1, 0]},
                None,
                None,
            )
        assert result["success"] is True
        mock_exec.assert_awaited_once()
        call_kwargs = mock_exec.await_args.kwargs
        assert call_kwargs["target"] == "Player"
        assert call_kwargs["position"] == [0, 1, 0]


class TestTelemetry:
    def test_metrics_init_idempotent(self):
        from unity3d_mcp.utils import telemetry

        telemetry._metrics_initialized = False
        with patch.dict("os.environ", {"UNITY3D_MCP_METRICS_ENABLED": "false"}):
            telemetry.init_metrics()
        assert telemetry._metrics_initialized is False


class TestPhase1ToolRegistration:
    @pytest.mark.asyncio
    async def test_new_tools_registered(self, mcp_server):
        tools = await mcp_server.app.list_tools()
        tool_names = {tool.name for tool in tools}
        assert "unity_bridge" in tool_names
        assert "unity_render" in tool_names
