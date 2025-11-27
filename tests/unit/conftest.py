"""
Unit test specific fixtures.

These fixtures are only available to tests in the unit/ directory.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for Unity command tests."""
    mock = MagicMock()
    mock.returncode = 0
    mock.communicate = AsyncMock(return_value=(b"Success", b""))
    return mock


@pytest.fixture
def mock_osc_client():
    """Mock OSC UDP client."""
    mock = MagicMock()
    mock.send_message = MagicMock()
    return mock


@pytest.fixture
def editor_manager(mock_config):
    """Create UnityEditorManager for unit testing."""
    from unity3d_mcp.core import UnityEditorManager
    return UnityEditorManager(mock_config)


@pytest.fixture
def project_manager(mock_config):
    """Create ProjectManager for unit testing."""
    from unity3d_mcp.core import ProjectManager
    return ProjectManager(mock_config)


@pytest.fixture
def scene_manager(mock_config):
    """Create SceneManager for unit testing."""
    from unity3d_mcp.core import SceneManager
    return SceneManager(mock_config)

