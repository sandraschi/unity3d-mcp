"""Integration tests for Unity3D MCP Server."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestServerIntegration:
    """Integration tests for the MCP server."""

    @pytest.mark.asyncio
    async def test_full_server_initialization(self):
        """Test complete server initialization flow."""
        from unity3d_mcp.server import Unity3DConfig, Unity3DMCP

        config = Unity3DConfig(
            auto_detect_unity=False,
            enable_http=False,
        )

        server = Unity3DMCP(config)

        # Verify all components initialized
        assert server.app is not None
        assert server.unity_editor is not None
        assert server.project_manager is not None
        assert server.vrchat_sdk is not None
        # OSC moved to oscmcp

    @pytest.mark.asyncio
    async def test_tool_chain_vrchat_upload(self, mock_vrchat_project, mock_avatar_prefab, vrchat_env_credentials):
        """Test complete VRChat upload workflow."""
        from unity3d_mcp.server import Unity3DConfig
        from unity3d_mcp.vrchat import VRChatSDKManager

        config = Unity3DConfig(project_path=str(mock_vrchat_project))
        manager = VRChatSDKManager(config)

        # Step 1: Check SDK
        sdk_result = await manager.check_sdk_installed(str(mock_vrchat_project))
        assert sdk_result["installed"] is True

        # Step 2: Check auth
        auth_result = await manager.check_authentication()
        assert auth_result["authenticated"] is True

        # Step 3: Validate avatar (will succeed with mock)
        validate_result = await manager.validate_avatar("Assets/Prefabs/TestAvatar.prefab", str(mock_vrchat_project))
        assert "valid" in validate_result


# TestOSCIntegration removed - OSC moved to oscmcp
# Use FastMCP server composition to combine unity3d-mcp with oscmcp


class TestProjectWorkflow:
    """Integration tests for project workflows."""

    @pytest.mark.asyncio
    async def test_create_and_configure_project(self, mock_unity_exe, tmp_path):
        """Test creating and configuring a Unity project."""
        from unity3d_mcp.core import ProjectManager
        from unity3d_mcp.server import Unity3DConfig

        config = Unity3DConfig(unity_editor_path=str(mock_unity_exe))
        manager = ProjectManager(config)

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            # Create project
            result = await manager.create_project("IntegrationTest", str(tmp_path), template="3D")

            assert result["status"] == "success"


class TestErrorHandling:
    """Integration tests for error handling."""

    @pytest.mark.asyncio
    async def test_graceful_unity_not_found(self):
        """Test graceful handling when Unity not installed."""
        from unity3d_mcp.core import UnityEditorManager
        from unity3d_mcp.server import Unity3DConfig

        config = Unity3DConfig(
            unity_editor_path="",
            auto_detect_unity=False,
        )
        manager = UnityEditorManager(config)

        result = await manager.launch_editor("D:\\Project")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_graceful_auth_failure(self, mock_config):
        """Test graceful handling of auth failure."""
        from unity3d_mcp.vrchat import VRChatSDKManager

        manager = VRChatSDKManager(mock_config)

        with patch.dict("os.environ", {}, clear=True), patch.object(
            manager, "_check_unity_editorprefs", return_value={"authenticated": False}
        ), patch("pathlib.Path.exists", return_value=False):
            result = await manager.check_authentication()

        assert result["authenticated"] is False
        assert "solutions" in result

    @pytest.mark.asyncio
    async def test_graceful_invalid_project(self, vrchat_manager, tmp_path):
        """Test graceful handling of invalid project."""
        result = await vrchat_manager.check_sdk_installed(str(tmp_path / "nonexistent"))

        assert result["installed"] is False
        assert "error" in result


class TestConcurrency:
    """Tests for concurrent operations."""

    # test_concurrent_osc_sends removed - OSC moved to oscmcp

    @pytest.mark.asyncio
    async def test_concurrent_validations(self, vrchat_manager, mock_vrchat_project):
        """Test concurrent avatar validations."""
        tasks = [vrchat_manager.check_sdk_installed(str(mock_vrchat_project)) for _ in range(5)]

        results = await asyncio.gather(*tasks)

        assert all(r["installed"] is True for r in results)
