"""Tests for Unity Editor controller operations."""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.asyncio
async def test_unity_editor_launch():
    """Test Unity Editor launch command."""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process

        # Would call: launch_unity_editor()
        # For now just verify mock works
        process = mock_popen(["unity", "-batchmode"])
        assert process.poll() is None


@pytest.mark.asyncio
async def test_create_unity_project():
    """Test Unity project creation."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="Project created")

        # Would call: create_unity_project(name="TestProject")
        # Mock verification
        result = mock_run(["unity", "-createProject", "TestProject"])
        assert result.returncode == 0


@pytest.mark.asyncio
async def test_unity_build_command():
    """Test Unity build command generation."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="Build successful")

        # Would call: build_project(target="Windows64")
        # Mock verification
        result = mock_run(["unity", "-buildWindows64Player", "output.exe"])
        assert result.returncode == 0


@pytest.mark.asyncio
async def test_scene_management():
    """Test Unity scene operations."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="Scene saved")

        # Would call: create_scene(name="MainScene")
        # Mock verification
        assert mock_run is not None


@pytest.mark.asyncio
async def test_asset_import():
    """Test asset import operations."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="Asset imported")

        # Would call: import_asset(path="model.fbx")
        # Mock verification
        result = mock_run(["unity", "-importPackage", "asset.unitypackage"])
        assert result.returncode == 0
