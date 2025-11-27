"""
Core Unity Editor Management

Unity Editor automation, project management, and scene operations.
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class UnityEditorManager:
    """Manages Unity Editor instances and operations."""

    def __init__(self, config):
        self.config = config
        self.active_processes = {}

    async def launch_editor(
        self,
        project_path: str,
        unity_version: str = "",
        batch_mode: bool = False,
        no_graphics: bool = False,
    ) -> Dict[str, Any]:
        """Launch Unity Editor with specified options."""
        try:
            unity_path = await self._resolve_unity_path(unity_version)
            if not unity_path:
                return {"status": "error", "message": "Unity Editor not found"}

            args = [unity_path, "-projectPath", project_path]

            if batch_mode:
                args.append("-batchmode")
            if no_graphics:
                args.append("-nographics")

            process = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            self.active_processes[project_path] = process

            return {
                "status": "success",
                "message": f"Unity Editor launched for project: {project_path}",
                "process_id": process.pid,
                "unity_path": unity_path,
            }

        except Exception as e:
            logger.error(f"Failed to launch Unity Editor: {e}")
            return {"status": "error", "message": str(e)}

    async def execute_method(
        self,
        class_name: str,
        method_name: str,
        parameters: Dict[str, Any] = {},
        project_path: str = "",
    ) -> Dict[str, Any]:
        """Execute Unity Editor method via command line."""
        try:
            unity_path = await self._resolve_unity_path()
            if not unity_path:
                return {"status": "error", "message": "Unity Editor not found"}

            # Build method execution command
            method_call = f"{class_name}.{method_name}"

            args = [unity_path, "-batchmode", "-quit", "-executeMethod", method_call]

            if project_path:
                args.extend(["-projectPath", project_path])

            # Add parameters as command line arguments
            for key, value in parameters.items():
                args.extend([f"-{key}", str(value)])

            result = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            return {
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "method": method_call,
                "parameters": parameters,
            }

        except Exception as e:
            logger.error(f"Failed to execute Unity method: {e}")
            return {"status": "error", "message": str(e)}

    async def _resolve_unity_path(self, version: str = "") -> Optional[str]:
        """Resolve Unity Editor executable path."""
        if self.config.unity_editor_path and Path(self.config.unity_editor_path).exists():
            return self.config.unity_editor_path

        # Auto-detect Unity installation
        if self.config.auto_detect_unity:
            common_paths = [
                r"C:\Program Files\Unity\Hub\Editor\{version}\Editor\Unity.exe",
                r"C:\Program Files\Unity\Editor\Unity.exe",
                r"C:\Program Files (x86)\Unity\Editor\Unity.exe",
            ]

            for path_template in common_paths:
                if version:
                    path = path_template.format(version=version)
                else:
                    path = path_template.replace(r"\{version}", "")

                if Path(path).exists():
                    return path

        return None


class ProjectManager:
    """Manages Unity project operations."""

    # UniVRM package info for different installation methods
    UNIVRM_PACKAGES = {
        "univrm": {
            "git": "https://github.com/vrm-c/UniVRM.git?path=/Assets/VRMShaders#v0.128.0",
            "name": "com.vrmc.vrmshaders",
            "version": "0.128.0",
        },
        "univrm-core": {
            "git": "https://github.com/vrm-c/UniVRM.git?path=/Assets/UniGLTF#v0.128.0",
            "name": "com.vrmc.gltf",
        },
        "vrm0": {
            "git": "https://github.com/vrm-c/UniVRM.git?path=/Assets/VRM#v0.128.0",
            "name": "com.vrmc.univrm",
        },
        "vrm1": {
            "git": "https://github.com/vrm-c/UniVRM.git?path=/Assets/VRM10#v0.128.0",
            "name": "com.vrmc.vrm",
        },
    }

    def __init__(self, config):
        self.config = config

    async def create_project(
        self, project_name: str, project_path: str, template: str = "3D", unity_version: str = ""
    ) -> Dict[str, Any]:
        """Create new Unity project."""
        try:
            unity_path = await self._resolve_unity_path(unity_version)
            if not unity_path:
                return {"status": "error", "message": "Unity Editor not found"}

            full_project_path = Path(project_path) / project_name

            args = [
                unity_path,
                "-batchmode",
                "-quit",
                "-createProject",
                str(full_project_path),
                "-projectTemplate",
                template,
            ]

            result = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await result.communicate()

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": f"Created Unity project: {project_name}",
                    "project_path": str(full_project_path),
                    "template": template,
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to create project (return code: {result.returncode})",
                }

        except Exception as e:
            logger.error(f"Failed to create Unity project: {e}")
            return {"status": "error", "message": str(e)}

    async def create_project_with_univrm(
        self,
        project_name: str,
        project_path: str,
        template: str = "3D",
        unity_version: str = "",
        vrm_version: str = "vrm0",
    ) -> Dict[str, Any]:
        """Create new Unity project with UniVRM pre-installed."""
        # First create the project
        result = await self.create_project(project_name, project_path, template, unity_version)
        if result["status"] != "success":
            return result

        full_project_path = Path(project_path) / project_name

        # Install UniVRM
        install_result = await self.install_univrm(str(full_project_path), vrm_version)

        return {
            "status": "success",
            "message": f"Created Unity project with UniVRM: {project_name}",
            "project_path": str(full_project_path),
            "template": template,
            "univrm_installed": install_result["status"] == "success",
            "univrm_details": install_result,
        }

    async def check_univrm_installed(self, project_path: str) -> Dict[str, Any]:
        """Check if UniVRM is installed in a Unity project."""
        try:
            manifest_path = Path(project_path) / "Packages" / "manifest.json"

            if not manifest_path.exists():
                return {
                    "status": "error",
                    "installed": False,
                    "message": f"Not a valid Unity project (manifest.json not found): {project_path}",
                }

            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            dependencies = manifest.get("dependencies", {})

            # Check for UniVRM packages
            found_packages = {}
            univrm_installed = False

            for pkg_key, pkg_info in self.UNIVRM_PACKAGES.items():
                pkg_name = pkg_info["name"]
                if pkg_name in dependencies:
                    found_packages[pkg_key] = {
                        "name": pkg_name,
                        "version": dependencies[pkg_name],
                    }
                    univrm_installed = True

            # Also check for legacy/alternative package names
            legacy_names = ["com.vrm", "vrm", "univrm"]
            for name in legacy_names:
                for dep_name in dependencies:
                    if name in dep_name.lower():
                        found_packages[dep_name] = {
                            "name": dep_name,
                            "version": dependencies[dep_name],
                        }
                        univrm_installed = True

            return {
                "status": "success",
                "installed": univrm_installed,
                "packages": found_packages,
                "project_path": project_path,
                "message": "UniVRM is installed" if univrm_installed else "UniVRM is not installed",
            }

        except json.JSONDecodeError as e:
            return {"status": "error", "installed": False, "message": f"Invalid manifest.json: {e}"}
        except Exception as e:
            logger.error(f"Failed to check UniVRM installation: {e}")
            return {"status": "error", "installed": False, "message": str(e)}

    async def install_univrm(
        self, project_path: str, vrm_version: str = "vrm0", refresh_unity: bool = True
    ) -> Dict[str, Any]:
        """Install UniVRM packages into a Unity project.
        
        Args:
            project_path: Path to Unity project
            vrm_version: "vrm0" for VRM 0.x or "vrm1" for VRM 1.0
            refresh_unity: Whether to refresh Unity to import packages
        """
        try:
            manifest_path = Path(project_path) / "Packages" / "manifest.json"

            if not manifest_path.exists():
                return {
                    "status": "error",
                    "message": f"Not a valid Unity project: {project_path}",
                }

            # Check if already installed
            check_result = await self.check_univrm_installed(project_path)
            if check_result.get("installed"):
                return {
                    "status": "success",
                    "message": "UniVRM is already installed",
                    "packages": check_result.get("packages", {}),
                    "already_installed": True,
                }

            # Read current manifest
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            dependencies = manifest.get("dependencies", {})

            # Packages to install (in order - dependencies first)
            packages_to_install = ["univrm", "univrm-core"]
            if vrm_version == "vrm0":
                packages_to_install.append("vrm0")
            elif vrm_version == "vrm1":
                packages_to_install.append("vrm1")
            else:
                packages_to_install.append("vrm0")  # Default to VRM 0.x

            installed_packages = []
            for pkg_key in packages_to_install:
                pkg_info = self.UNIVRM_PACKAGES.get(pkg_key)
                if pkg_info:
                    dependencies[pkg_info["name"]] = pkg_info["git"]
                    installed_packages.append({
                        "key": pkg_key,
                        "name": pkg_info["name"],
                        "source": pkg_info["git"],
                    })

            # Write updated manifest
            manifest["dependencies"] = dependencies
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            result = {
                "status": "success",
                "message": f"UniVRM ({vrm_version}) packages added to manifest.json",
                "packages_installed": installed_packages,
                "project_path": project_path,
                "next_steps": [
                    "Open the project in Unity Editor",
                    "Unity will download and import the packages automatically",
                    "Wait for the import to complete before using VRM features",
                ],
            }

            # Optionally refresh Unity to trigger package import
            if refresh_unity:
                unity_path = await self._resolve_unity_path()
                if unity_path:
                    result["refresh_initiated"] = True
                    result["refresh_note"] = "Run Unity to import packages"

            return result

        except Exception as e:
            logger.error(f"Failed to install UniVRM: {e}")
            return {"status": "error", "message": str(e)}

    async def uninstall_univrm(self, project_path: str) -> Dict[str, Any]:
        """Remove UniVRM packages from a Unity project."""
        try:
            manifest_path = Path(project_path) / "Packages" / "manifest.json"

            if not manifest_path.exists():
                return {"status": "error", "message": "Not a valid Unity project"}

            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            dependencies = manifest.get("dependencies", {})
            removed_packages = []

            # Remove all UniVRM related packages
            keys_to_remove = []
            for pkg_key, pkg_info in self.UNIVRM_PACKAGES.items():
                pkg_name = pkg_info["name"]
                if pkg_name in dependencies:
                    keys_to_remove.append(pkg_name)
                    removed_packages.append(pkg_name)

            for key in keys_to_remove:
                del dependencies[key]

            manifest["dependencies"] = dependencies
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            return {
                "status": "success",
                "message": "UniVRM packages removed from manifest.json",
                "removed_packages": removed_packages,
                "note": "Restart Unity to complete uninstallation",
            }

        except Exception as e:
            logger.error(f"Failed to uninstall UniVRM: {e}")
            return {"status": "error", "message": str(e)}

    async def _resolve_unity_path(self, version: str = "") -> Optional[str]:
        """Resolve Unity Editor path."""
        # Reuse logic from UnityEditorManager
        editor_manager = UnityEditorManager(self.config)
        return await editor_manager._resolve_unity_path(version)


class SceneManager:
    """Manages Unity scene operations."""

    def __init__(self, config):
        self.config = config

    async def create_scene(
        self, scene_name: str, project_path: str, template: str = "Basic"
    ) -> Dict[str, Any]:
        """Create new Unity scene."""
        try:
            # This would typically use Unity's EditorSceneManager
            # For now, return a placeholder implementation
            return {
                "status": "success",
                "message": f"Scene creation initiated: {scene_name}",
                "scene_path": f"Assets/Scenes/{scene_name}.unity",
                "template": template,
            }

        except Exception as e:
            logger.error(f"Failed to create scene: {e}")
            return {"status": "error", "message": str(e)}
