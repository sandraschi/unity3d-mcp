"""Unit tests for multi-platform social VR integrations."""

import json

import pytest


class TestPlatformManager:
    """Test unified platform manager."""

    @pytest.mark.asyncio
    async def test_list_platforms(self, mock_config):
        """Test listing all supported platforms."""
        from unity3d_mcp.platforms import PlatformManager

        manager = PlatformManager(mock_config)
        result = await manager.list_supported_platforms()

        assert result["status"] == "success"
        assert "platforms" in result
        assert "vrchat" in result["platforms"]
        assert "chilloutvr" in result["platforms"]
        assert "resonite" in result["platforms"]
        assert "cluster" in result["platforms"]

    @pytest.mark.asyncio
    async def test_check_platform_sdk_resonite(self, mock_unity_project, mock_config):
        """Test checking Resonite SDK (should always return success)."""
        from unity3d_mcp.platforms import PlatformManager

        manager = PlatformManager(mock_config)
        result = await manager.check_platform_sdk("resonite", str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is True
        assert "doesn't require" in result["message"]

    @pytest.mark.asyncio
    async def test_check_platform_sdk_unknown(self, mock_unity_project, mock_config):
        """Test checking unknown platform."""
        from unity3d_mcp.platforms import PlatformManager

        manager = PlatformManager(mock_config)
        result = await manager.check_platform_sdk("unknown_platform", str(mock_unity_project))

        assert result["status"] == "error"
        assert "Unknown platform" in result["message"]


class TestChilloutVRManager:
    """Test ChilloutVR integration."""

    @pytest.mark.asyncio
    async def test_check_cck_not_installed(self, mock_unity_project, mock_config):
        """Test checking CCK when not installed."""
        from unity3d_mcp.platforms import ChilloutVRManager

        manager = ChilloutVRManager(mock_config)
        result = await manager.check_cck_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is False
        assert "install_url" in result

    @pytest.mark.asyncio
    async def test_check_cck_installed(self, mock_unity_project, mock_config):
        """Test checking CCK when installed."""
        from unity3d_mcp.platforms import ChilloutVRManager

        # Add CCK to manifest
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        manifest["dependencies"]["com.abi.cck"] = "https://github.com/ABI-Software/CCK.git"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        manager = ChilloutVRManager(mock_config)
        result = await manager.check_cck_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is True
        assert result["package"] == "com.abi.cck"

    @pytest.mark.asyncio
    async def test_install_cck_instructions(self, mock_unity_project, mock_config):
        """Test CCK installation provides instructions."""
        from unity3d_mcp.platforms import ChilloutVRManager

        manager = ChilloutVRManager(mock_config)
        result = await manager.install_cck(str(mock_unity_project))

        assert result["status"] == "info"
        assert "instructions" in result
        assert "documentation" in result

    @pytest.mark.asyncio
    async def test_setup_cvr_avatar(self, mock_unity_project, mock_config):
        """Test CVRAvatar setup configuration."""
        from unity3d_mcp.platforms import ChilloutVRManager

        manager = ChilloutVRManager(mock_config)
        result = await manager.setup_cvr_avatar(
            avatar_object="TestAvatar",
            project_path=str(mock_unity_project),
            eye_height=1.65,
        )

        assert result["status"] == "success"
        assert "configuration" in result
        assert result["configuration"]["eye_height"] == 1.65

    @pytest.mark.asyncio
    async def test_validate_for_chillout(self, mock_unity_project, mock_config):
        """Test ChilloutVR validation."""
        from unity3d_mcp.platforms import ChilloutVRManager

        manager = ChilloutVRManager(mock_config)
        result = await manager.validate_for_chillout(
            avatar_name="TestAvatar",
            project_path=str(mock_unity_project),
        )

        assert result["status"] == "success"
        assert result["platform"] == "ChilloutVR"
        assert "performance_limits" in result


class TestResoniteManager:
    """Test Resonite integration."""

    @pytest.fixture
    def vrm_file(self, tmp_path):
        """Create a mock VRM file."""
        vrm = tmp_path / "avatar.vrm"
        vrm.write_bytes(b"glTF" + b"\x00" * 100)  # GLB/VRM magic
        return vrm

    @pytest.fixture
    def glb_file(self, tmp_path):
        """Create a mock GLB file."""
        glb = tmp_path / "model.glb"
        glb.write_bytes(b"glTF" + b"\x00" * 50)
        return glb

    @pytest.mark.asyncio
    async def test_prepare_vrm_for_resonite(self, vrm_file, mock_config):
        """Test preparing VRM for Resonite."""
        from unity3d_mcp.platforms import ResoniteManager

        manager = ResoniteManager(mock_config)
        result = await manager.prepare_for_resonite(str(vrm_file))

        assert result["status"] == "success"
        assert result["format"] == ".vrm"
        assert "import_instructions" in result
        assert len(result["vrm_notes"]) > 0

    @pytest.mark.asyncio
    async def test_prepare_glb_for_resonite(self, glb_file, mock_config):
        """Test preparing GLB for Resonite."""
        from unity3d_mcp.platforms import ResoniteManager

        manager = ResoniteManager(mock_config)
        result = await manager.prepare_for_resonite(str(glb_file))

        assert result["status"] == "success"
        assert result["format"] == ".glb"

    @pytest.mark.asyncio
    async def test_prepare_unsupported_format(self, tmp_path, mock_config):
        """Test preparing unsupported format."""
        from unity3d_mcp.platforms import ResoniteManager

        bad_file = tmp_path / "model.xyz"
        bad_file.write_text("unsupported")

        manager = ResoniteManager(mock_config)
        result = await manager.prepare_for_resonite(str(bad_file))

        assert result["status"] == "error"
        assert "Unsupported format" in result["message"]

    @pytest.mark.asyncio
    async def test_check_resonite_compatibility(self, vrm_file, mock_config):
        """Test Resonite compatibility check."""
        from unity3d_mcp.platforms import ResoniteManager

        manager = ResoniteManager(mock_config)
        result = await manager.check_resonite_compatibility(str(vrm_file))

        assert result["status"] == "success"
        assert result["compatible"] is True
        assert "details" in result

    @pytest.mark.asyncio
    async def test_check_large_file_warning(self, tmp_path, mock_config):
        """Test warning for large files."""
        from unity3d_mcp.platforms import ResoniteManager

        # Create a 60MB file
        large_file = tmp_path / "large.glb"
        large_file.write_bytes(b"glTF" + b"\x00" * (60 * 1024 * 1024))

        manager = ResoniteManager(mock_config)
        result = await manager.check_resonite_compatibility(str(large_file))

        assert result["status"] == "success"
        assert any("optimizing" in r.lower() for r in result["recommendations"])


class TestClusterManager:
    """Test Cluster integration."""

    @pytest.mark.asyncio
    async def test_check_cluster_kit_not_installed(self, mock_unity_project, mock_config):
        """Test checking Cluster Kit when not installed."""
        from unity3d_mcp.platforms import ClusterManager

        manager = ClusterManager(mock_config)
        result = await manager.check_cluster_kit_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is False
        assert "install_url" in result

    @pytest.mark.asyncio
    async def test_check_cluster_kit_installed(self, mock_unity_project, mock_config):
        """Test checking Cluster Kit when installed."""
        from unity3d_mcp.platforms import ClusterManager

        # Add Cluster package to manifest
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        manifest["dependencies"]["mu.cluster.cluster-creator-kit"] = "1.0.0"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        manager = ClusterManager(mock_config)
        result = await manager.check_cluster_kit_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is True

    @pytest.mark.asyncio
    async def test_prepare_for_cluster(self, mock_unity_project, mock_config):
        """Test preparing avatar for Cluster."""
        from unity3d_mcp.platforms import ClusterManager

        manager = ClusterManager(mock_config)
        result = await manager.prepare_for_cluster(
            avatar_path="Assets/avatar.vrm",
            project_path=str(mock_unity_project),
        )

        assert result["status"] == "success"
        assert result["platform"] == "Cluster"
        assert "upload_steps" in result
        assert "VRM" in str(result["requirements"])
