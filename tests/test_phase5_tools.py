"""Tests for Phase 5 telemetry, execution mode, and smoke helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestExecutionMode:
    @pytest.mark.asyncio
    async def test_hands_off_when_bridge_down(self):
        from unity3d_mcp.utils.execution_mode import describe_execution_mode

        with patch(
            "unity3d_mcp.utils.execution_mode.bridge_available",
            new=AsyncMock(return_value=False),
        ):
            result = await describe_execution_mode()
        assert result["mode"] == "hands_off"
        assert result["bridge_connected"] is False

    @pytest.mark.asyncio
    async def test_hands_in_when_bridge_up(self):
        from unity3d_mcp.utils.execution_mode import describe_execution_mode

        with patch(
            "unity3d_mcp.utils.execution_mode.bridge_available",
            new=AsyncMock(return_value=True),
        ):
            result = await describe_execution_mode()
        assert result["mode"] == "hands_in"
        assert result["bridge_connected"] is True


class TestTelemetry:
    def test_render_metrics_when_disabled(self):
        from unity3d_mcp.utils import telemetry

        telemetry._metrics_initialized = False
        with patch.object(telemetry, "metrics_enabled", return_value=False):
            telemetry.init_metrics()
        body = telemetry.render_metrics()
        assert b"metrics disabled" in body

    def test_json_log_formatter(self):
        import logging

        from unity3d_mcp.utils.structured_logging import JsonLogFormatter

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        line = JsonLogFormatter().format(record)
        assert '"service": "unity3d-mcp"' in line
        assert "hello" in line
