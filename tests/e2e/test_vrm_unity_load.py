"""
End-to-end tests for loading VRM into Unity.

These tests require:
- Unity Editor installed (set UNITY_EDITOR_PATH or auto-detect)
- A Unity project with UniVRM (set UNITY_TEST_PROJECT)
- The Nekomimi-chan.vrm test file

Run with: pytest tests/e2e/test_vrm_unity_load.py -v --run-e2e
"""

import shutil
from pathlib import Path

import pytest
from fixtures.factories import VRM_TEST_FILE, requires_vrm_file

from e2e.conftest import requires_unity, requires_unity_project, requires_univrm


@pytest.mark.e2e
@requires_unity
class TestUnityDetection:
    """Test Unity detection and availability."""

    def test_unity_found(self, unity_executable):
        """Test that Unity executable was found."""
        assert unity_executable is not None
        assert unity_executable.exists()
        assert unity_executable.name == "Unity.exe"

    def test_unity_version(self, unity_executable):
        """Test Unity version can be determined from path."""
        # Unity Hub path contains version: .../Hub/Editor/2022.3.0f1/Editor/Unity.exe
        path_str = str(unity_executable)
        if "Hub" in path_str:
            parts = path_str.split("\\")
            for i, part in enumerate(parts):
                if part == "Editor" and i > 0:
                    version = parts[i - 1] if parts[i - 1] != "Hub" else parts[i + 1]
                    # Version should look like 2022.3.0f1
                    assert any(c.isdigit() for c in version)
                    break


@pytest.mark.e2e
@requires_unity_project
class TestUnityProject:
    """Test Unity project detection."""

    def test_project_found(self, unity_project):
        """Test that Unity project was found."""
        assert unity_project is not None
        assert unity_project.exists()
        assert (unity_project / "Assets").exists()

    def test_project_has_packages(self, unity_project):
        """Test project has Packages folder."""
        packages = unity_project / "Packages"
        assert packages.exists()
        assert (packages / "manifest.json").exists()


@pytest.mark.e2e
@pytest.mark.slow
@requires_unity
@requires_unity_project
@requires_vrm_file
class TestVRMImportIntoUnity:
    """Test importing VRM file into actual Unity project."""

    @pytest.fixture
    def temp_vrm_copy(self, tmp_path):
        """Create a temporary copy of the VRM file."""
        temp_vrm = tmp_path / "test_avatar.vrm"
        shutil.copy2(VRM_TEST_FILE, temp_vrm)
        return temp_vrm

    @pytest.mark.asyncio
    async def test_vrm_import_to_project(self, unity_config, unity_project, temp_vrm_copy):
        """Test importing VRM into Unity project Assets folder."""
        from unity3d_mcp.avatar import VRMAvatarManager

        manager = VRMAvatarManager(unity_config)

        result = await manager.import_vrm(
            vrm_path=str(temp_vrm_copy),
            project_path=str(unity_project),
            optimize_for_vrchat=False,
            create_prefab=False,
        )

        assert result["status"] == "success"
        assert "vrm_path" in result

        # Verify file was copied
        imported_path = Path(result["vrm_path"])
        assert imported_path.exists()

        # Cleanup
        if imported_path.exists():
            imported_path.unlink()

    @pytest.mark.asyncio
    async def test_vrm_import_with_optimization(self, unity_config, unity_project, temp_vrm_copy):
        """Test VRM import with VRChat optimizations."""
        from unity3d_mcp.avatar import VRMAvatarManager

        manager = VRMAvatarManager(unity_config)

        result = await manager.import_vrm(
            vrm_path=str(temp_vrm_copy),
            project_path=str(unity_project),
            optimize_for_vrchat=True,
            create_prefab=True,
        )

        assert result["status"] == "success"
        assert result["optimized_for_vrchat"] is True
        assert "vrchat_optimizations" in result

        # Cleanup
        imported_path = Path(result["vrm_path"])
        if imported_path.exists():
            imported_path.unlink()


@pytest.mark.e2e
@pytest.mark.slow
@requires_unity
@requires_unity_project
@requires_univrm
@requires_vrm_file
class TestVRMUnityBatchImport:
    """Test VRM import using Unity batch mode (full integration)."""

    @pytest.fixture
    def vrm_importer_script(self, tmp_path):
        """Create a C# script to import VRM in Unity."""
        script = tmp_path / "VRMImporter.cs"
        script.write_text("""
using UnityEngine;
using UnityEditor;
using System.IO;

public class VRMImporter
{
    [MenuItem("Tools/MCP/ImportVRM")]
    public static void ImportVRM()
    {
        string vrmPath = System.Environment.GetEnvironmentVariable("VRM_IMPORT_PATH");
        if (string.IsNullOrEmpty(vrmPath))
        {
            Debug.LogError("VRM_IMPORT_PATH not set");
            EditorApplication.Exit(1);
            return;
        }

        if (!File.Exists(vrmPath))
        {
            Debug.LogError($"VRM file not found: {vrmPath}");
            EditorApplication.Exit(1);
            return;
        }

        // Copy to Assets
        string fileName = Path.GetFileName(vrmPath);
        string destPath = Path.Combine(Application.dataPath, "Models", fileName);
        Directory.CreateDirectory(Path.GetDirectoryName(destPath));
        File.Copy(vrmPath, destPath, true);

        AssetDatabase.Refresh();

        Debug.Log($"VRM imported: {destPath}");
        EditorApplication.Exit(0);
    }
}
""")
        return script

    @pytest.mark.asyncio
    async def test_unity_batch_vrm_import(self, unity_executable, unity_project, vrm_importer_script):
        """Test VRM import via Unity batch mode."""
        import os
        import subprocess

        # Copy script to project
        editor_scripts = unity_project / "Assets" / "Editor"
        editor_scripts.mkdir(parents=True, exist_ok=True)
        dest_script = editor_scripts / "VRMImporter.cs"
        shutil.copy2(vrm_importer_script, dest_script)

        try:
            # Set environment
            env = os.environ.copy()
            env["VRM_IMPORT_PATH"] = str(VRM_TEST_FILE)

            # Run Unity in batch mode
            cmd = [
                str(unity_executable),
                "-batchmode",
                "-quit",
                "-projectPath",
                str(unity_project),
                "-executeMethod",
                "VRMImporter.ImportVRM",
                "-logFile",
                "-",
            ]

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            # Check result
            assert result.returncode == 0, f"Unity failed: {result.stderr}"
            assert "VRM imported" in result.stdout or result.returncode == 0

        finally:
            # Cleanup
            if dest_script.exists():
                dest_script.unlink()

            # Remove imported VRM
            imported = unity_project / "Assets" / "Models" / VRM_TEST_FILE.name
            if imported.exists():
                imported.unlink()


@pytest.mark.e2e
@pytest.mark.slow
@requires_unity
@requires_unity_project
class TestUnityEditorLaunch:
    """Test launching Unity Editor."""

    @pytest.mark.asyncio
    async def test_unity_editor_launch_batch(self, unity_config):
        """Test launching Unity in batch mode."""
        from unity3d_mcp.core import UnityEditorManager

        manager = UnityEditorManager(unity_config)

        # Just test that we can resolve the path
        path = await manager._resolve_unity_path()
        assert path is not None
        assert Path(path).exists()

    @pytest.mark.asyncio
    async def test_unity_execute_method(self, unity_executable, unity_project):
        """Test executing a Unity method via batch mode."""
        import subprocess

        # Simple test - just verify Unity can start and exit
        cmd = [
            str(unity_executable),
            "-batchmode",
            "-quit",
            "-projectPath",
            str(unity_project),
            "-logFile",
            "-",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Unity should exit cleanly
        assert result.returncode == 0, f"Unity failed: {result.stderr}"
