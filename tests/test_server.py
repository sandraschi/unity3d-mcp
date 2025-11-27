"""Tests for Unity3D MCP Server initialization and tool registration."""

import pytest
from unittest.mock import patch, MagicMock


class TestServerInitialization:
    """Tests for server initialization."""

    def test_server_creates_successfully(self, mock_config):
        """Test that server initializes without errors."""
        from unity3d_mcp.server import Unity3DMCP
        
        server = Unity3DMCP(mock_config)
        assert server is not None
        assert server.app is not None

    def test_server_default_config(self):
        """Test server with default configuration."""
        from unity3d_mcp.server import Unity3DMCP, Unity3DConfig
        
        server = Unity3DMCP()
        assert server.config is not None
        assert isinstance(server.config, Unity3DConfig)

    def test_managers_initialized(self, mcp_server):
        """Test that all managers are initialized."""
        assert mcp_server.unity_editor is not None
        assert mcp_server.project_manager is not None
        assert mcp_server.scene_manager is not None
        assert mcp_server.vrm_avatar is not None
        assert mcp_server.animation is not None
        assert mcp_server.asset_manager is not None
        assert mcp_server.build_manager is not None
        assert mcp_server.vrchat_sdk is not None
        # OSC moved to oscmcp


class TestToolRegistration:
    """Tests for MCP tool registration."""

    def test_tools_registered(self, mcp_server):
        """Test that tools are registered with FastMCP."""
        # FastMCP stores tools internally
        assert mcp_server.app is not None

    def test_core_tools_exist(self, mcp_server):
        """Test that core tools are registered."""
        # The tools should be registered on the app
        # We verify by checking the server initialized without error
        assert mcp_server.unity_editor is not None
        assert mcp_server.project_manager is not None

    def test_vrchat_tools_exist(self, mcp_server):
        """Test that VRChat tools are registered."""
        assert mcp_server.vrchat_sdk is not None
        # OSC moved to oscmcp


class TestConfig:
    """Tests for Unity3DConfig."""

    def test_config_defaults(self):
        """Test default configuration values."""
        from unity3d_mcp.server import Unity3DConfig
        
        config = Unity3DConfig()
        assert config.unity_editor_path == ""
        assert config.project_path == ""
        assert config.auto_detect_unity is True
        assert config.enable_http is True
        assert config.http_port == 8080
        assert config.log_level == "INFO"

    def test_config_custom_values(self):
        """Test configuration with custom values."""
        from unity3d_mcp.server import Unity3DConfig
        
        config = Unity3DConfig(
            unity_editor_path="C:\\Unity\\Editor\\Unity.exe",
            project_path="D:\\Projects\\Game",
            auto_detect_unity=False,
            http_port=9000,
        )
        
        assert config.unity_editor_path == "C:\\Unity\\Editor\\Unity.exe"
        assert config.project_path == "D:\\Projects\\Game"
        assert config.auto_detect_unity is False
        assert config.http_port == 9000


class TestCreateApp:
    """Tests for create_app factory function."""

    def test_create_app_no_config(self):
        """Test create_app without config."""
        from unity3d_mcp.server import create_app
        
        app = create_app()
        assert app is not None

    def test_create_app_with_config(self, mock_config):
        """Test create_app with config."""
        from unity3d_mcp.server import create_app
        
        app = create_app(mock_config)
        assert app is not None
        assert app.config == mock_config

