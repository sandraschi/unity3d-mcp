"""Tests for Phase 3 fleet import, vision refine, and worldlabs assemble."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestFleetImport:
    @pytest.mark.asyncio
    async def test_import_blender_glb(self, tmp_path):
        from unity3d_mcp.utils.fleet_import import import_blender_asset

        project = tmp_path / "MyProject"
        (project / "Assets").mkdir(parents=True)
        model = tmp_path / "robot.glb"
        model.write_bytes(b"glb")

        manager = MagicMock()
        manager.import_3d_model = AsyncMock(
            return_value={"success": True, "destination_path": str(project / "Assets/BlenderImports/robot.glb")}
        )

        result = await import_blender_asset(
            manager,
            file_path=str(model),
            project_path=str(project),
        )
        assert result["success"] is True
        assert result["format"] == "glb"
        manager.import_3d_model.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_import_fleet_batch(self, tmp_path):
        from unity3d_mcp.utils.fleet_import import import_fleet_batch

        project = tmp_path / "Proj"
        (project / "Assets").mkdir(parents=True)
        exports = tmp_path / "exports"
        exports.mkdir()
        (exports / "a.glb").write_bytes(b"a")
        (exports / "b.glb").write_bytes(b"b")

        manager = MagicMock()
        manager.import_3d_model = AsyncMock(return_value={"success": True})

        result = await import_fleet_batch(
            manager,
            input_dir=str(exports),
            project_path=str(project),
        )
        assert result["imported_count"] == 2


class TestVisionRefine:
    @pytest.mark.asyncio
    async def test_build_refinement_prompt(self):
        from unity3d_mcp.utils.vision_refine import build_refinement_prompt

        text = build_refinement_prompt("Better lighting", {"object_count": 2, "objects": [{"name": "Cube"}]})
        assert "Better lighting" in text
        assert "Cube" in text

    @pytest.mark.asyncio
    async def test_apply_bridge_commands(self):
        from unity3d_mcp.utils.vision_refine import apply_bridge_commands

        bridge = MagicMock()
        with patch(
            "unity3d_mcp.utils.vision_refine.bridge_available",
            new=AsyncMock(return_value=True),
        ), patch(
            "unity3d_mcp.utils.vision_refine.execute_bridge_action",
            new=AsyncMock(return_value={"success": True, "mode": "bridge"}),
        ):
            result = await apply_bridge_commands(
                [{"action": "transform_object", "target": "Cube", "position": [0, 1, 0]}],
                bridge=bridge,
            )
        assert result["success"] is True
        assert result["applied"] == 1


class TestPhase3ToolRegistration:
    @pytest.mark.asyncio
    async def test_new_tools_registered(self, mcp_server):
        tools = await mcp_server.app.list_tools()
        names = {tool.name for tool in tools}
        assert "unity_import" in names
        assert "unity_vision_refine" in names
