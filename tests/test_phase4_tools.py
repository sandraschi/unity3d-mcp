"""Tests for Phase 4 validation, platform audit, and tool registration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestSceneValidator:
    def test_list_platform_limits(self):
        from unity3d_mcp.utils.scene_validator import list_platform_limits

        result = list_platform_limits()
        assert result["success"] is True
        assert "vrchat" in result["platforms"]

    def test_evaluate_scene_metrics_blocks_over_limit(self):
        from unity3d_mcp.utils.scene_validator import evaluate_scene_metrics

        report = evaluate_scene_metrics(
            {"triangle_count": 90000, "material_count": 40, "missing_script_count": 1},
            target_platform="vrchat",
        )
        assert report["valid"] is False
        assert report["performance_rank"] == "Poor"
        assert len(report["errors"]) >= 2

    def test_validate_model_file(self, tmp_path):
        from unity3d_mcp.utils.scene_validator import validate_model_file

        model = tmp_path / "prop.glb"
        model.write_bytes(b"glb")
        result = validate_model_file(str(model), target_platform="resonite")
        assert result["success"] is True
        assert result["format"] == "glb"

    @pytest.mark.asyncio
    async def test_validate_scene_via_bridge(self):
        from unity3d_mcp.utils.scene_validator import validate_scene_via_bridge

        bridge = MagicMock()
        bridge.validate_scene = AsyncMock(
            return_value={
                "scene_name": "SampleScene",
                "triangle_count": 1200,
                "material_count": 3,
                "missing_script_count": 0,
                "mesh_count": 2,
                "object_count": 5,
            }
        )
        report = await validate_scene_via_bridge(bridge, target_platform="vrchat")
        assert report["success"] is True
        assert report["valid"] is True
        assert report["mode"] == "bridge"


class TestPlatformAudit:
    @pytest.mark.asyncio
    async def test_run_unified_audit(self, tmp_path):
        from unity3d_mcp.utils.platform_audit import run_unified_audit

        project = tmp_path / "Proj"
        (project / "Packages").mkdir(parents=True)
        (project / "Packages" / "manifest.json").write_text('{"dependencies": {}}', encoding="utf-8")
        model = tmp_path / "avatar.glb"
        model.write_bytes(b"glb")

        platforms = MagicMock()
        platforms.chillout.check_cck_installed = AsyncMock(return_value={"installed": False})
        platforms.cluster.check_cluster_kit_installed = AsyncMock(return_value={"installed": False})
        platforms.chillout.validate_for_chillout = AsyncMock(return_value={"status": "success"})
        platforms.resonite.check_resonite_compatibility = AsyncMock(
            return_value={"compatible": True, "recommendations": []}
        )

        vrchat = MagicMock()
        vrchat.check_sdk_installed = AsyncMock(return_value={"installed": False})
        vrchat.validate_avatar = AsyncMock(return_value={"valid": True, "errors": [], "warnings": []})

        result = await run_unified_audit(
            platforms=platforms,
            vrchat_sdk=vrchat,
            project_path=str(project),
            model_path=str(model),
            scene_metrics={"triangle_count": 1000, "material_count": 2, "missing_script_count": 0},
        )
        assert result["success"] is True
        assert "platform_scores" in result
        assert "vrchat" in result["platform_scores"]


class TestPhase4ToolRegistration:
    @pytest.mark.asyncio
    async def test_unity_validation_registered(self, mcp_server):
        tools = await mcp_server.app.list_tools()
        names = {tool.name for tool in tools}
        assert "unity_validation" in names
