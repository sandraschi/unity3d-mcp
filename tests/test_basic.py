"""Basic tests for unity3d-mcp package."""

import pytest


class TestPackageImport:
    """Tests for package imports."""

    def test_package_import(self):
        """Test that package can be imported."""
        import unity3d_mcp

        assert unity3d_mcp is not None

    def test_package_version(self):
        """Test that package has version."""
        import unity3d_mcp

        assert hasattr(unity3d_mcp, "__version__")
        assert unity3d_mcp.__version__ == "1.0.0"

    def test_package_author(self):
        """Test that package has author."""
        import unity3d_mcp

        assert hasattr(unity3d_mcp, "__author__")
        assert unity3d_mcp.__author__ == "Sandra"

    def test_module_structure(self):
        """Test that expected modules exist."""
        import unity3d_mcp

        assert unity3d_mcp.__name__ == "unity3d_mcp"


class TestModuleImports:
    """Tests for submodule imports."""

    def test_import_server(self):
        """Test server module import."""
        from unity3d_mcp import server

        assert server is not None

    def test_import_server_classes(self):
        """Test server class imports."""
        from unity3d_mcp.server import Unity3DConfig, Unity3DMCP, create_app

        assert Unity3DMCP is not None
        assert Unity3DConfig is not None
        assert create_app is not None

    def test_import_core(self):
        """Test core module import."""
        from unity3d_mcp import core

        assert core is not None

    def test_import_core_classes(self):
        """Test core class imports."""
        from unity3d_mcp.core import ProjectManager, SceneManager, UnityEditorManager

        assert UnityEditorManager is not None
        assert ProjectManager is not None
        assert SceneManager is not None

    def test_import_vrchat(self):
        """Test VRChat module import."""
        from unity3d_mcp import vrchat

        assert vrchat is not None

    def test_import_vrchat_classes(self):
        """Test VRChat class imports."""
        from unity3d_mcp.vrchat import VRChatSDKManager

        assert VRChatSDKManager is not None
        # OSCManager moved to oscmcp

    def test_import_avatar(self):
        """Test avatar module import."""
        from unity3d_mcp import avatar

        assert avatar is not None

    def test_import_assets(self):
        """Test assets module import."""
        from unity3d_mcp import assets

        assert assets is not None

    def test_import_build(self):
        """Test build module import."""
        from unity3d_mcp import build

        assert build is not None

    def test_import_utils(self):
        """Test utils module import."""
        from unity3d_mcp import utils

        assert utils is not None


class TestMainEntry:
    """Tests for __main__ entry point."""

    def test_main_module_exists(self):
        """Test that __main__.py exists and is importable."""
        import unity3d_mcp.__main__ as main_module

        assert main_module is not None

    def test_main_function_exists(self):
        """Test that main function exists."""
        from unity3d_mcp.__main__ import main

        assert callable(main)


class TestExports:
    """Tests for package exports."""

    def test_all_exports(self):
        """Test __all__ exports."""
        import unity3d_mcp

        assert hasattr(unity3d_mcp, "__all__")
        assert "Unity3DMCP" in unity3d_mcp.__all__
        assert "create_app" in unity3d_mcp.__all__

    def test_exported_classes_accessible(self):
        """Test that exported classes are accessible."""
        from unity3d_mcp import Unity3DMCP, create_app

        assert Unity3DMCP is not None
        assert create_app is not None


class TestDependencies:
    """Tests for required dependencies."""

    def test_fastmcp_installed(self):
        """Test FastMCP is available."""
        import fastmcp

        assert fastmcp is not None

    def test_pydantic_installed(self):
        """Test Pydantic is available."""
        import pydantic

        assert pydantic is not None

    def test_python_osc_installed(self):
        """Test python-osc is available."""
        try:
            import pythonosc

            assert pythonosc is not None
        except ImportError:
            pytest.skip("python-osc not installed")

    def test_aiohttp_installed(self):
        """Test aiohttp is available."""
        try:
            import aiohttp

            assert aiohttp is not None
        except ImportError:
            pytest.skip("aiohttp not installed")
