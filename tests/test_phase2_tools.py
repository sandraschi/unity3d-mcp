"""Tests for Phase 2 jobs, prefab, and simulation wiring."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestJobQueue:
    @pytest.mark.asyncio
    async def test_submit_batch_import_job(self, tmp_path):
        from unity3d_mcp.utils.job_queue import configure_job_runners, get_job, submit_unity_job

        model = tmp_path / "crate.glb"
        model.write_bytes(b"glb")

        async def fake_import(**kwargs):
            return {"success": True, "model_path": kwargs.get("model_path")}

        configure_job_runners(import_runner=fake_import)

        job_id = await submit_unity_job(
            "batch_import",
            name="test_import",
            params={"input_dir": str(tmp_path), "pattern": "*.glb"},
        )
        await __import__("asyncio").sleep(0.05)
        job = get_job(job_id)
        assert job is not None
        assert job.status.value in ("completed", "running", "pending")
        if job.status.value == "completed":
            assert job.output.get("imported_count") == 1

    @pytest.mark.asyncio
    async def test_unknown_job_type_fails_fast(self):
        from unity3d_mcp.utils.job_queue import get_job, submit_unity_job

        job_id = await submit_unity_job("unknown_type", params={})
        job = get_job(job_id)
        assert job is not None
        assert job.status.value == "failed"


class TestUnityApiPhase2:
    @pytest.mark.asyncio
    async def test_create_prefab_via_bridge(self):
        from unity3d_mcp.tools.portmanteau.unity_api import UnityAPIToolManager

        manager = UnityAPIToolManager(MagicMock())
        with patch(
            "unity3d_mcp.tools.portmanteau.unity_api.execute_bridge_action",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "result": {"status": "success", "prefab_path": "Assets/Prefabs/Cube.prefab"},
                }
            ),
        ) as mock_exec:
            result = await manager._api_create_prefab("Cube", "Cube.prefab", None, None)
        assert result["success"] is True
        mock_exec.assert_awaited_once()
        assert mock_exec.await_args.kwargs["target"] == "Cube"

    @pytest.mark.asyncio
    async def test_run_simulation_delegates(self):
        from unity3d_mcp.tools.portmanteau.unity_api import UnityAPIToolManager

        manager = UnityAPIToolManager(MagicMock())
        with patch(
            "unity3d_mcp.utils.simulation_runner.run_bridge_simulation",
            new=AsyncMock(return_value={"success": True, "mode": "bridge"}),
        ) as mock_sim:
            result = await manager._api_run_simulation(2.0, None, None, False)
        assert result["success"] is True
        mock_sim.assert_awaited_once()


class TestPhase2ToolRegistration:
    @pytest.mark.asyncio
    async def test_unity_jobs_registered(self, mcp_server):
        tools = await mcp_server.app.list_tools()
        tool_names = {tool.name for tool in tools}
        assert "unity_jobs" in tool_names
