"""
Root pytest configuration and shared fixtures for unity3d-mcp tests.

This file contains fixtures that are shared across all test types.
For test-type specific fixtures, see:
- tests/unit/conftest.py
- tests/integration/conftest.py
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# Add src directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Import fixture factories
from fixtures.factories import (
    MOCK_VRCHAT_2FA_RESPONSE,
    MOCK_VRCHAT_USER_RESPONSE,
    VRM_TEST_FILE,
    create_avatar_prefab,
    create_mock_unity_executable,
    create_unity_project_structure,
)

# ============================================================================
# Event Loop Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def mock_config():
    """Create a mock Unity3DConfig with test defaults."""
    from unity3d_mcp.server import Unity3DConfig

    return Unity3DConfig(
        unity_editor_path="",
        project_path="",
        auto_detect_unity=False,
        enable_http=False,
        http_port=8080,
        log_level="DEBUG",
    )


@pytest.fixture
def mock_config_with_project(mock_unity_project: Path):
    """Create a mock config with project path set."""
    from unity3d_mcp.server import Unity3DConfig

    return Unity3DConfig(
        unity_editor_path="C:\\Program Files\\Unity\\Editor\\Unity.exe",
        project_path=str(mock_unity_project),
        auto_detect_unity=False,
        enable_http=False,
    )


# ============================================================================
# Unity Project Fixtures
# ============================================================================


@pytest.fixture
def mock_unity_project(tmp_path: Path) -> Path:
    """Create a mock Unity project structure."""
    return create_unity_project_structure(tmp_path, include_vrchat=False)


@pytest.fixture
def mock_vrchat_project(tmp_path: Path) -> Path:
    """Create a mock Unity project with VRChat SDK installed."""
    return create_unity_project_structure(tmp_path, include_vrchat=True)


@pytest.fixture
def mock_avatar_prefab(mock_vrchat_project: Path) -> Path:
    """Create a mock avatar prefab file."""
    return create_avatar_prefab(mock_vrchat_project, "TestAvatar")


@pytest.fixture
def mock_unity_exe(tmp_path: Path) -> Path:
    """Create a mock Unity executable."""
    return create_mock_unity_executable(tmp_path)


@pytest.fixture
def vrm_test_file() -> Path:
    """Get path to VRM test file (Nekomimi-chan.vrm).

    Use with @requires_vrm_file decorator to skip if missing.
    """
    return VRM_TEST_FILE


# ============================================================================
# Manager Fixtures
# ============================================================================


@pytest.fixture
def mcp_server(mock_config):
    """Create a Unity3DMCP server instance."""
    from unity3d_mcp.server import Unity3DMCP

    return Unity3DMCP(mock_config)


@pytest.fixture
def vrchat_manager(mock_config):
    """Create a VRChatSDKManager instance."""
    from unity3d_mcp.vrchat import VRChatSDKManager

    return VRChatSDKManager(mock_config)


# OSC fixture removed - use oscmcp for OSC testing
# @pytest.fixture
# def osc_manager(mock_config):
#     """OSCManager moved to oscmcp - use server composition."""
#     pass


# ============================================================================
# Environment Fixtures
# ============================================================================


@pytest.fixture
def vrchat_env_credentials(monkeypatch):
    """Set VRChat credentials in environment."""
    monkeypatch.setenv("VRCHAT_USERNAME", "test_user")
    monkeypatch.setenv("VRCHAT_PASSWORD", "test_pass")
    monkeypatch.setenv("VRCHAT_TOTP_SECRET", "test_totp")


@pytest.fixture
def clean_env(monkeypatch):
    """Clear VRChat credentials from environment."""
    monkeypatch.setenv("VRCHAT_USERNAME", "")
    monkeypatch.setenv("VRCHAT_PASSWORD", "")
    monkeypatch.setenv("VRCHAT_TOTP_SECRET", "")
    monkeypatch.delenv("VRCHAT_USERNAME", raising=False)
    monkeypatch.delenv("VRCHAT_PASSWORD", raising=False)
    monkeypatch.delenv("VRCHAT_TOTP_SECRET", raising=False)
    yield


# ============================================================================
# Mock Response Fixtures
# ============================================================================


@pytest.fixture
def mock_vrchat_auth_response():
    """Mock VRChat API authentication response."""
    return MOCK_VRCHAT_USER_RESPONSE.copy()


@pytest.fixture
def mock_vrchat_2fa_response():
    """Mock VRChat API 2FA required response."""
    return MOCK_VRCHAT_2FA_RESPONSE.copy()


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture
def async_mock():
    """Helper to create async mock functions."""

    def _create_async_mock(return_value=None):
        mock = AsyncMock()
        mock.return_value = return_value
        return mock

    return _create_async_mock


@pytest.fixture
def capture_logs(caplog):
    """Capture log output at DEBUG level."""
    import logging

    caplog.set_level(logging.DEBUG)
    return caplog
