"""Tests for core Unity Editor management."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestUnityEditorManager:
    """Tests for UnityEditorManager."""

    @pytest.fixture
    def editor_manager(self, mock_config):
        """Create UnityEditorManager instance."""
        from unity3d_mcp.core import UnityEditorManager

        return UnityEditorManager(mock_config)

    @pytest.mark.asyncio
    async def test_launch_editor_unity_not_found(self, editor_manager):
        """Test launch fails when Unity not found."""
        result = await editor_manager.launch_editor("D:\\Project")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_launch_editor_success(self, editor_manager, mock_unity_exe):
        """Test successful editor launch."""
        editor_manager.config.unity_editor_path = str(mock_unity_exe)

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_exec.return_value = mock_process

            result = await editor_manager.launch_editor("D:\\Project")

            assert result["status"] == "success"
            assert result["process_id"] == 12345

    @pytest.mark.asyncio
    async def test_launch_editor_batch_mode(self, editor_manager, mock_unity_exe):
        """Test launching in batch mode."""
        editor_manager.config.unity_editor_path = str(mock_unity_exe)

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_exec.return_value = mock_process

            result = await editor_manager.launch_editor("D:\\Project", batch_mode=True, no_graphics=True)

            assert result["status"] == "success"
            # Verify batch mode args were passed
            call_args = mock_exec.call_args[0]
            assert "-batchmode" in call_args
            assert "-nographics" in call_args

    @pytest.mark.asyncio
    async def test_execute_method_success(self, editor_manager, mock_unity_exe):
        """Test executing Unity method."""
        editor_manager.config.unity_editor_path = str(mock_unity_exe)

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Success", b""))
            mock_exec.return_value = mock_process

            result = await editor_manager.execute_method("MyClass", "MyMethod", {"param1": "value1"})

            assert result["status"] == "success"
            assert result["method"] == "MyClass.MyMethod"

    @pytest.mark.asyncio
    async def test_execute_method_failure(self, editor_manager, mock_unity_exe):
        """Test method execution failure."""
        editor_manager.config.unity_editor_path = str(mock_unity_exe)

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = MagicMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(b"", b"Error"))
            mock_exec.return_value = mock_process

            result = await editor_manager.execute_method("MyClass", "MyMethod")

            assert result["status"] == "error"


class TestProjectManager:
    """Tests for ProjectManager."""

    @pytest.fixture
    def project_manager(self, mock_config):
        """Create ProjectManager instance."""
        from unity3d_mcp.core import ProjectManager

        return ProjectManager(mock_config)

    @pytest.mark.asyncio
    async def test_create_project_unity_not_found(self, project_manager):
        """Test project creation fails when Unity not found."""
        result = await project_manager.create_project("TestProject", "D:\\Projects")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_create_project_success(self, project_manager, mock_unity_exe, tmp_path):
        """Test successful project creation."""
        project_manager.config.unity_editor_path = str(mock_unity_exe)

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            result = await project_manager.create_project("NewProject", str(tmp_path), template="3D")

            assert result["status"] == "success"
            assert "NewProject" in result["project_path"]

    @pytest.mark.asyncio
    async def test_create_project_templates(self, project_manager, mock_unity_exe, tmp_path):
        """Test different project templates."""
        project_manager.config.unity_editor_path = str(mock_unity_exe)

        templates = ["3D", "2D", "3D (URP)", "VR"]

        for template in templates:
            with patch("asyncio.create_subprocess_exec") as mock_exec:
                mock_process = MagicMock()
                mock_process.returncode = 0
                mock_process.communicate = AsyncMock(return_value=(b"", b""))
                mock_exec.return_value = mock_process

                result = await project_manager.create_project(f"Project_{template}", str(tmp_path), template=template)

                assert result["template"] == template


class TestSceneManager:
    """Tests for SceneManager."""

    @pytest.fixture
    def scene_manager(self, mock_config):
        """Create SceneManager instance."""
        from unity3d_mcp.core import SceneManager

        return SceneManager(mock_config)

    @pytest.mark.asyncio
    async def test_create_scene(self, scene_manager):
        """Test scene creation."""
        result = await scene_manager.create_scene("TestScene", "D:\\Project", template="Basic")

        assert result["status"] == "success"
        assert "TestScene" in result["scene_path"]


class TestUnityPathResolution:
    """Tests for Unity path resolution."""

    @pytest.fixture
    def editor_manager(self, mock_config):
        """Create UnityEditorManager instance."""
        from unity3d_mcp.core import UnityEditorManager

        return UnityEditorManager(mock_config)

    @pytest.mark.asyncio
    async def test_resolve_configured_path(self, editor_manager, mock_unity_exe):
        """Test resolving configured Unity path."""
        editor_manager.config.unity_editor_path = str(mock_unity_exe)

        path = await editor_manager._resolve_unity_path()

        assert path == str(mock_unity_exe)

    @pytest.mark.asyncio
    async def test_resolve_auto_detect_disabled(self, editor_manager):
        """Test path resolution with auto-detect disabled."""
        editor_manager.config.auto_detect_unity = False
        editor_manager.config.unity_editor_path = ""

        path = await editor_manager._resolve_unity_path()

        assert path is None

    @pytest.mark.asyncio
    async def test_resolve_with_version(self, editor_manager):
        """Test path resolution with specific version."""
        editor_manager.config.auto_detect_unity = True

        # This will likely return None in test environment
        path = await editor_manager._resolve_unity_path("2022.3.0f1")

        # Just verify it doesn't crash
        assert path is None or isinstance(path, str)
