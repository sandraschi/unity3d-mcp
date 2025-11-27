"""Unit tests for World Labs (Marble/Chisel) integration."""

import json
from pathlib import Path

import pytest


class TestWorldLabsImport:
    """Test World Labs asset imports."""

    @pytest.fixture
    def marble_export_folder(self, tmp_path):
        """Create a mock Marble export folder."""
        export_dir = tmp_path / "marble_export"
        export_dir.mkdir()

        # Create mock mesh files
        (export_dir / "world_visual.fbx").write_bytes(b"mock fbx data")
        (export_dir / "world_collider.obj").write_text("# mock collider mesh")

        # Create mock splat file
        (export_dir / "world.ply").write_bytes(b"mock ply gaussian splat")

        # Create mock textures
        (export_dir / "diffuse.png").write_bytes(b"mock png")
        (export_dir / "normal.jpg").write_bytes(b"mock jpg")

        return export_dir

    @pytest.mark.asyncio
    async def test_import_marble_folder(
        self, mock_unity_project, mock_config, marble_export_folder
    ):
        """Test importing a Marble export folder."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        manager = WorldLabsManager(mock_config)
        result = await manager.import_marble_world(
            source_path=str(marble_export_folder),
            project_path=str(mock_unity_project),
            asset_name="TestWorld",
            include_colliders=True,
        )

        assert result["status"] == "success"
        assert result["asset_name"] == "TestWorld"
        assert result["file_counts"]["meshes"] >= 1
        assert result["file_counts"]["colliders"] >= 1
        assert result["file_counts"]["splats"] >= 1
        assert result["file_counts"]["textures"] >= 1

        # Verify files were copied
        dest = Path(result["destination"])
        assert dest.exists()
        assert (dest / "Visuals").exists()
        assert (dest / "Colliders").exists()
        assert (dest / "Splats").exists()

    @pytest.mark.asyncio
    async def test_import_single_mesh(self, mock_unity_project, mock_config, tmp_path):
        """Test importing a single mesh file."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        # Create mock mesh file
        mesh_file = tmp_path / "world.glb"
        mesh_file.write_bytes(b"mock glb data")

        manager = WorldLabsManager(mock_config)
        result = await manager.import_marble_world(
            source_path=str(mesh_file),
            project_path=str(mock_unity_project),
            asset_name="SingleMesh",
        )

        assert result["status"] == "success"
        assert "mesh_path" in result
        assert result["format"] == ".glb"

    @pytest.mark.asyncio
    async def test_import_gaussian_splat(self, mock_unity_project, mock_config, tmp_path):
        """Test importing a Gaussian Splat file."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        # Create mock splat file
        splat_file = tmp_path / "world.ply"
        splat_file.write_bytes(b"mock gaussian splat data")

        manager = WorldLabsManager(mock_config)
        result = await manager.import_marble_world(
            source_path=str(splat_file),
            project_path=str(mock_unity_project),
        )

        assert result["status"] == "success"
        assert "splat_path" in result
        assert result["gaussian_splatting_installed"] is False
        assert "warning" in result

    @pytest.mark.asyncio
    async def test_import_unsupported_format(self, mock_unity_project, mock_config, tmp_path):
        """Test importing unsupported file format."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        # Create unsupported file
        bad_file = tmp_path / "world.xyz"
        bad_file.write_text("unsupported format")

        manager = WorldLabsManager(mock_config)
        result = await manager.import_marble_world(
            source_path=str(bad_file),
            project_path=str(mock_unity_project),
        )

        assert result["status"] == "error"
        assert "Unsupported format" in result["message"]

    @pytest.mark.asyncio
    async def test_import_nonexistent_source(self, mock_unity_project, mock_config):
        """Test importing from nonexistent path."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        manager = WorldLabsManager(mock_config)
        result = await manager.import_marble_world(
            source_path="/nonexistent/path",
            project_path=str(mock_unity_project),
        )

        assert result["status"] == "error"
        assert "not found" in result["message"]


class TestGaussianSplatting:
    """Test Gaussian Splatting package management."""

    @pytest.mark.asyncio
    async def test_check_not_installed(self, mock_unity_project, mock_config):
        """Test checking Gaussian Splatting when not installed."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        manager = WorldLabsManager(mock_config)
        result = await manager.check_gaussian_splatting_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is False

    @pytest.mark.asyncio
    async def test_check_installed(self, mock_unity_project, mock_config):
        """Test checking Gaussian Splatting when installed."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        # Add package to manifest
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        manifest["dependencies"]["com.aras-p.gaussian-splatting"] = "https://github.com/..."
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        manager = WorldLabsManager(mock_config)
        result = await manager.check_gaussian_splatting_installed(str(mock_unity_project))

        assert result["status"] == "success"
        assert result["installed"] is True
        assert result["package"] == "com.aras-p.gaussian-splatting"

    @pytest.mark.asyncio
    async def test_install_gaussian_splatting(self, mock_unity_project, mock_config):
        """Test installing Gaussian Splatting package."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        manager = WorldLabsManager(mock_config)
        result = await manager.install_gaussian_splatting(str(mock_unity_project))

        assert result["status"] == "success"
        assert "package" in result
        assert "next_steps" in result

        # Verify manifest was updated
        manifest_path = mock_unity_project / "Packages" / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert "com.aras-p.gaussian-splatting" in manifest["dependencies"]

    @pytest.mark.asyncio
    async def test_install_already_installed(self, mock_unity_project, mock_config):
        """Test installing when already present."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        manager = WorldLabsManager(mock_config)

        # Install first time
        await manager.install_gaussian_splatting(str(mock_unity_project))

        # Try again
        result = await manager.install_gaussian_splatting(str(mock_unity_project))

        assert result["status"] == "success"
        assert result.get("already_installed") is True


class TestVRChatOptimization:
    """Test VRChat optimization recommendations."""

    @pytest.fixture
    def worldlabs_assets(self, mock_unity_project):
        """Create mock World Labs assets in project."""
        assets_dir = mock_unity_project / "Assets" / "WorldLabs" / "TestWorld"
        assets_dir.mkdir(parents=True)

        visuals = assets_dir / "Visuals"
        visuals.mkdir()
        (visuals / "world.fbx").write_bytes(b"mock mesh")
        (visuals / "texture.png").write_bytes(b"x" * 1024 * 1024)  # 1MB texture

        splats = assets_dir / "Splats"
        splats.mkdir()
        (splats / "world.ply").write_bytes(b"mock splat")

        return "WorldLabs/TestWorld"

    @pytest.mark.asyncio
    async def test_vrchat_optimization_analysis(
        self, mock_unity_project, mock_config, worldlabs_assets
    ):
        """Test VRChat optimization recommendations."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        manager = WorldLabsManager(mock_config)
        result = await manager.optimize_for_vrchat(
            project_path=str(mock_unity_project),
            asset_folder=worldlabs_assets,
            target_polygon_count=50000,
        )

        assert result["status"] == "success"
        assert "recommendations" in result
        assert len(result["recommendations"]) >= 1

        # Check for Gaussian Splat warning
        splat_rec = next(
            (r for r in result["recommendations"] if r["category"] == "Gaussian Splats"),
            None
        )
        assert splat_rec is not None
        assert "warning" in splat_rec

    @pytest.mark.asyncio
    async def test_optimization_nonexistent_folder(self, mock_unity_project, mock_config):
        """Test optimization on nonexistent folder."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        manager = WorldLabsManager(mock_config)
        result = await manager.optimize_for_vrchat(
            project_path=str(mock_unity_project),
            asset_folder="NonExistent/Folder",
        )

        assert result["status"] == "error"
        assert "not found" in result["message"]


class TestImportWithVRChatOptimization:
    """Test importing with VRChat optimization flags."""

    @pytest.mark.asyncio
    async def test_import_with_vrchat_flag(
        self, mock_unity_project, mock_config, tmp_path
    ):
        """Test import with VRChat optimization enabled."""
        from unity3d_mcp.worldlabs import WorldLabsManager

        # Create mock mesh
        mesh_file = tmp_path / "world.obj"
        mesh_file.write_text("# mock obj")

        manager = WorldLabsManager(mock_config)
        result = await manager.import_marble_world(
            source_path=str(mesh_file),
            project_path=str(mock_unity_project),
            optimize_for_vrchat=True,
        )

        assert result["status"] == "success"
        assert "vrchat_optimization" in result
        assert "recommended_actions" in result["vrchat_optimization"]

