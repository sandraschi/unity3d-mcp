"""Tests for fleet E2E pipeline helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestGazeboImport:
    @pytest.mark.asyncio
    async def test_import_gazebo_via_unity(self):
        from unity3d_mcp.utils.fleet_pipeline import import_gazebo_via_unity

        with patch("unity3d_mcp.utils.fleet_pipeline.httpx.AsyncClient") as mock_client:
            instance = mock_client.return_value.__aenter__.return_value
            response = MagicMock()
            response.json.return_value = {
                "success": True,
                "count": 1,
                "models": {"scout": "imported"},
            }
            response.raise_for_status = MagicMock()
            instance.post = AsyncMock(return_value=response)

            result = await import_gazebo_via_unity(
                unity_url="http://127.0.0.1:10831",
                models=["scout"],
                file_path_template="gazebo_models/{model}.fbx",
            )
        assert result["success"] is True
        assert result["models"]["scout"] == "imported"


class TestFleetPipelineHelpers:
    def test_parse_tool_payload_from_dict(self):
        from unity3d_mcp.utils.fleet_pipeline import parse_tool_payload

        assert parse_tool_payload({"success": True, "valid": True})["valid"] is True

    def test_parse_tool_payload_from_http_wrapper(self):
        from unity3d_mcp.utils.fleet_pipeline import parse_tool_payload

        data = parse_tool_payload({"success": True, "data": {"valid": True}})
        assert data["valid"] is True

    @pytest.mark.asyncio
    async def test_export_from_blender_success(self, tmp_path):
        from unity3d_mcp.utils.fleet_pipeline import export_from_blender

        out = tmp_path / "handoff.glb"
        out.write_bytes(b"glb")

        with patch(
            "unity3d_mcp.utils.fleet_pipeline.call_http_tool",
            new=AsyncMock(return_value={"success": True, "message": "exported"}),
        ):
            result = await export_from_blender(
                blender_url="http://127.0.0.1:10849",
                output_path=out,
            )
        assert result["success"] is True
        assert result["output_path"] == str(out)

    @pytest.mark.asyncio
    async def test_run_fleet_pipeline_import_only(self, tmp_path):
        from unity3d_mcp.utils.fleet_pipeline import run_fleet_pipeline

        project = tmp_path / "UnityProj"
        (project / "Assets").mkdir(parents=True)
        model = tmp_path / "prop.glb"
        model.write_bytes(b"glb")

        mock_server = MagicMock()
        mock_server.import_export_manager.import_3d_model = AsyncMock(
            return_value={"success": True, "destination_path": str(project / "Assets/BlenderImports/prop.glb")}
        )
        mock_app = MagicMock()
        mock_app.call_tool = AsyncMock(
            side_effect=[
                MagicMock(content=[MagicMock(text='{"valid": true, "success": true}')]),
                MagicMock(content=[MagicMock(text='{"success": false, "mode": "bridge", "error": "no bridge"}')]),
                MagicMock(content=[MagicMock(text='{"valid": true, "success": true}')]),
            ]
        )
        mock_server.app = mock_app

        with patch("unity3d_mcp.server.server_instance", mock_server), patch(
            "unity3d_mcp.utils.execution_mode.describe_execution_mode",
            new=AsyncMock(return_value={"mode": "hands_off"}),
        ), patch(
            "unity3d_mcp.utils.fleet_import.import_blender_asset",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "file_path": str(model),
                    "destination_path": str(project / "Assets/BlenderImports/prop.glb"),
                }
            ),
        ):
            report = await run_fleet_pipeline(
                project_path=str(project),
                model_path=str(model),
                skip_export=True,
                skip_build=True,
            )

        assert report.model_path == str(model)
        assert any(s.name == "unity_import" and s.success for s in report.steps)
        assert report.success is True
