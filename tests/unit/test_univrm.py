"""Unit tests for UniVRM installation and detection."""

import json
from pathlib import Path

import pytest


class TestUniVRMDetection:
    """Test UniVRM installation detection."""

    @pytest.mark.asyncio
    async def test_check_univrm_not_installed(self, mock_unity_project, mock_config):
        """Test detecting UniVRM is not installed."""
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)
        result = await manager.check_univrm_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is False
        assert result["packages"] == {}

    @pytest.mark.asyncio
    async def test_check_univrm_installed(self, mock_unity_project, mock_config):
        """Test detecting UniVRM is installed."""
        from unity3d_mcp.core import ProjectManager

        # Add UniVRM to manifest
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        manifest["dependencies"]["com.vrmc.univrm"] = "https://github.com/vrm-c/UniVRM.git"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        manager = ProjectManager(mock_config)
        result = await manager.check_univrm_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is True
        assert "vrm0" in result["packages"]

    @pytest.mark.asyncio
    async def test_check_univrm_invalid_project(self, tmp_path, mock_config):
        """Test checking UniVRM on invalid project."""
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)
        result = await manager.check_univrm_installed(str(tmp_path))

        assert result["status"] == "error"
        assert result["installed"] is False
        assert "manifest.json" in result["message"]


class TestUniVRMInstallation:
    """Test UniVRM installation."""

    @pytest.mark.asyncio
    async def test_install_univrm_vrm0(self, mock_unity_project, mock_config):
        """Test installing UniVRM 0.x."""
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)
        result = await manager.install_univrm(
            str(mock_unity_project), vrm_version="vrm0", refresh_unity=False
        )

        assert result["status"] == "success"
        assert len(result["packages_installed"]) >= 3  # univrm, univrm-core, vrm0

        # Verify manifest was updated
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert "com.vrmc.univrm" in manifest["dependencies"]
        assert "com.vrmc.vrmshaders" in manifest["dependencies"]

    @pytest.mark.asyncio
    async def test_install_univrm_vrm1(self, mock_unity_project, mock_config):
        """Test installing UniVRM 1.0."""
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)
        result = await manager.install_univrm(
            str(mock_unity_project), vrm_version="vrm1", refresh_unity=False
        )

        assert result["status"] == "success"

        # Verify VRM 1.0 package added
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert "com.vrmc.vrm" in manifest["dependencies"]

    @pytest.mark.asyncio
    async def test_install_univrm_already_installed(self, mock_unity_project, mock_config):
        """Test installing UniVRM when already present."""
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)

        # Install first time
        await manager.install_univrm(str(mock_unity_project), refresh_unity=False)

        # Try to install again
        result = await manager.install_univrm(str(mock_unity_project), refresh_unity=False)

        assert result["status"] == "success"
        assert result.get("already_installed") is True

    @pytest.mark.asyncio
    async def test_install_univrm_invalid_project(self, tmp_path, mock_config):
        """Test installing UniVRM on invalid project."""
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)
        result = await manager.install_univrm(str(tmp_path), refresh_unity=False)

        assert result["status"] == "error"


class TestUniVRMUninstallation:
    """Test UniVRM uninstallation."""

    @pytest.mark.asyncio
    async def test_uninstall_univrm(self, mock_unity_project, mock_config):
        """Test uninstalling UniVRM."""
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)

        # Install first
        await manager.install_univrm(str(mock_unity_project), refresh_unity=False)

        # Uninstall
        result = await manager.uninstall_univrm(str(mock_unity_project))

        assert result["status"] == "success"
        assert len(result["removed_packages"]) >= 1

        # Verify manifest was cleaned
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        for pkg in ["com.vrmc.univrm", "com.vrmc.vrm", "com.vrmc.vrmshaders"]:
            assert pkg not in manifest["dependencies"]


class TestProjectWithUniVRM:
    """Test creating projects with UniVRM."""

    @pytest.mark.asyncio
    async def test_create_project_with_univrm(self, tmp_path, mock_config, monkeypatch):
        """Test creating project with UniVRM pre-installed."""
        from unittest.mock import AsyncMock, MagicMock
        from unity3d_mcp.core import ProjectManager

        manager = ProjectManager(mock_config)

        # Mock create_project to simulate project creation
        async def mock_create_project(*args, **kwargs):
            project_path = tmp_path / args[0]
            project_path.mkdir(exist_ok=True)
            (project_path / "Assets").mkdir()
            (project_path / "Packages").mkdir()
            (project_path / "Packages" / "manifest.json").write_text('{"dependencies": {}}')
            return {
                "status": "success",
                "project_path": str(project_path),
            }

        manager.create_project = mock_create_project

        result = await manager.create_project_with_univrm(
            "TestVRMProject", str(tmp_path), vrm_version="vrm0"
        )

        assert result["status"] == "success"
        assert result["univrm_installed"] is True
        assert "TestVRMProject" in result["project_path"]

