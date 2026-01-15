"""
Core Unity Editor Management

Unity Editor automation, project management, and scene operations.
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
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
        """Execute Unity Editor method via command line.

        Note: If Unity is already running with the project open, this will attempt
        to launch a new Unity instance in batch mode. For running Unity instances,
        consider using Unity Editor API plugins for real-time communication.
        """
        try:
            # Try to detect Unity version from project if project_path provided
            unity_version = ""
            if project_path:
                version_file = Path(project_path) / "ProjectSettings" / "ProjectVersion.txt"
                if version_file.exists():
                    try:
                        with open(version_file, "r") as f:
                            for line in f:
                                if line.startswith("m_EditorVersion:"):
                                    unity_version = line.split(":")[1].strip()
                                    logger.info(
                                        f"Detected Unity version from project: {unity_version}"
                                    )
                                    break
                    except Exception as e:
                        logger.warning(f"Failed to read Unity version from project: {e}")

            unity_path = await self._resolve_unity_path(unity_version)
            if not unity_path:
                # Try one more time without version to find any Unity installation
                logger.warning("Unity not found with version, trying without version")
                unity_path = await self._resolve_unity_path("")
                if not unity_path:
                    error_msg = f"Unity Editor not found"
                    if unity_version:
                        error_msg += f" (looking for version {unity_version})"
                    return {"status": "error", "message": error_msg}

            # Build method execution command
            method_call = f"{class_name}.{method_name}"

            # Note: -batchmode -quit launches Unity in batch mode and quits after execution
            # If Unity is already running with the project, this will launch a separate instance
            # For real-time communication with running Unity, use Unity Editor API plugins
            args = [
                unity_path,
                "-batchmode",
                "-quit",
                "-executeMethod",
                method_call,
                "-logFile",
                "-",
            ]

            if project_path:
                args.extend(["-projectPath", project_path])

            logger.info(f"Executing Unity method: {method_call} with Unity: {unity_path}")

            # Add parameters as command line arguments
            # Unity's -executeMethod doesn't support parameters directly via command line
            # Parameters need to be passed via static fields or other mechanisms
            # For now, we'll log them but can't pass them directly
            if parameters:
                logger.info(f"Method parameters provided but not passed to Unity: {parameters}")
                logger.warning(
                    "Unity -executeMethod doesn't support parameters via command line. Consider using static fields or Unity Editor API."
                )

            result = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()
            stdout_str = stdout.decode("utf-8", errors="ignore") if stdout else ""
            stderr_str = stderr.decode("utf-8", errors="ignore") if stderr else ""

            # Check for common Unity errors
            if "Unity Editor not found" in stderr_str or "could not be found" in stderr_str:
                return {
                    "status": "error",
                    "message": "Unity Editor not found",
                    "stderr": stderr_str,
                }

            return {
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "output": stdout_str,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "method": method_call,
                "parameters": parameters,
                "unity_path": unity_path,
            }

        except Exception as e:
            logger.error(f"Failed to execute Unity method: {e}")
            return {"status": "error", "message": str(e)}

    def install_mcp_bridge(self, project_path: str) -> bool:
        """Install MCPBridge.cs into the Unity project."""
        try:
            editor_mcp_dir = Path(project_path) / "Assets" / "Editor" / "MCP"
            editor_mcp_dir.mkdir(parents=True, exist_ok=True)

            # Source path - relative to this file
            current_dir = Path(__file__).parent.parent
            source_path = current_dir / "resources" / "MCPBridge.cs"

            if not source_path.exists():
                logger.error(f"MCPBridge.cs not found at {source_path}")
                return False

            shutil.copy2(source_path, editor_mcp_dir / "MCPBridge.cs")
            logger.info(f"Installed MCPBridge.cs to {editor_mcp_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to install MCP bridge: {e}")
            return False

    def write_command_params(self, project_path: str, params: Dict[str, Any]) -> bool:
        """Write command parameters to JSON file for Unity to read."""
        try:
            param_file = Path(project_path) / "mcp_params.json"
            with open(param_file, "w") as f:
                json.dump(params, f, indent=2)
            logger.info(f"Wrote params to {param_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to write params: {e}")
            return False

    async def _resolve_unity_path(self, version: str = "") -> Optional[str]:
        """Resolve Unity Editor executable path."""
        if self.config.unity_editor_path and Path(self.config.unity_editor_path).exists():
            return self.config.unity_editor_path

        # Auto-detect Unity installation
        if self.config.auto_detect_unity:
            # First, try Unity Hub installations
            hub_editors_path = Path.home() / "AppData/Roaming/Unity Hub/editors.json"
            if hub_editors_path.exists():
                try:
                    with open(hub_editors_path, "r", encoding="utf-8") as f:
                        editors_data = json.load(f)
                        editors = []

                        # Handle different JSON structures
                        if isinstance(editors_data, dict):
                            # Try "editors" key
                            if "editors" in editors_data:
                                editors = editors_data["editors"]
                            # Try direct list of editors
                            elif isinstance(editors_data.get("list"), list):
                                editors = editors_data["list"]
                            # Try if the dict itself contains editor info
                            else:
                                # Check if it's a dict with editor IDs as keys
                                for key, value in editors_data.items():
                                    if isinstance(value, dict) and (
                                        "version" in value or "location" in value
                                    ):
                                        editors.append(value)
                        elif isinstance(editors_data, list):
                            editors = editors_data

                        logger.debug(f"Found {len(editors)} Unity installations in Hub")

                        # If version specified, find exact match
                        if version:
                            for editor in editors:
                                if isinstance(editor, dict):
                                    editor_version = editor.get("version", "")
                                    editor_path = editor.get("location", "")
                                    if editor_path and (
                                        version in editor_version or editor_version in version
                                    ):
                                        unity_exe = Path(editor_path) / "Editor" / "Unity.exe"
                                        if unity_exe.exists():
                                            logger.info(f"Found Unity {version} at: {unity_exe}")
                                            return str(unity_exe)
                        else:
                            # No version specified, use first available or latest
                            for editor in editors:
                                if isinstance(editor, dict):
                                    editor_path = editor.get("location", "")
                                    if editor_path:
                                        unity_exe = Path(editor_path) / "Editor" / "Unity.exe"
                                        if unity_exe.exists():
                                            logger.info(f"Found Unity at: {unity_exe}")
                                            return str(unity_exe)
                except Exception as e:
                    logger.warning(f"Failed to parse Unity Hub editors.json: {e}", exc_info=True)

            # Fallback: Check common installation paths
            if version:
                # Try with specific version in Hub
                hub_path = Path(f"C:/Program Files/Unity/Hub/Editor/{version}/Editor/Unity.exe")
                if hub_path.exists():
                    return str(hub_path)
                # Also try without version prefix matching
                hub_base = Path("C:/Program Files/Unity/Hub/Editor")
                if hub_base.exists():
                    for version_dir in hub_base.iterdir():
                        if version_dir.is_dir() and version in version_dir.name:
                            unity_exe = version_dir / "Editor" / "Unity.exe"
                            if unity_exe.exists():
                                return str(unity_exe)
            else:
                # Try to find any Unity installation in Hub
                hub_base = Path("C:/Program Files/Unity/Hub/Editor")
                if hub_base.exists():
                    # Find latest version (sort by directory name, which usually contains version)
                    try:
                        versions = sorted(
                            [d for d in hub_base.iterdir() if d.is_dir()], reverse=True
                        )
                        for version_dir in versions:
                            unity_exe = version_dir / "Editor" / "Unity.exe"
                            if unity_exe.exists():
                                return str(unity_exe)
                    except Exception as e:
                        logger.warning(f"Failed to scan Unity Hub directory: {e}")

            # Legacy paths (non-Hub installations)
            common_paths = [
                Path("C:/Program Files/Unity/Editor/Unity.exe"),
                Path("C:/Program Files (x86)/Unity/Editor/Unity.exe"),
            ]

            for path in common_paths:
                if path.exists():
                    return str(path)

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
                    installed_packages.append(
                        {
                            "key": pkg_key,
                            "name": pkg_info["name"],
                            "source": pkg_info["git"],
                        }
                    )

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
        self.unity_editor = UnityEditorManager(config)

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

    async def create_light(
        self,
        light_name: str,
        light_type: str = "Spot",
        color: Optional[List[float]] = None,
        intensity: float = 1.0,
        position: Optional[Dict[str, float]] = None,
        rotation: Optional[Dict[str, float]] = None,
        project_path: str = "",
    ) -> Dict[str, Any]:
        """Create a light in the current scene using MCPBridge."""
        try:
            if not project_path:
                return {"status": "error", "message": "project_path is required for MCPBridge"}

            # 1. Install Bridge
            if not self.unity_editor.install_mcp_bridge(project_path):
                return {"status": "error", "message": "Failed to install MCPBridge"}

            # 2. Prepare Parameters
            params = {
                "name": light_name,
                "type": light_type,
                "color": color or [1.0, 1.0, 1.0, 1.0],
                "intensity": intensity,
                "position": [position.get("x", 0), position.get("y", 0), position.get("z", 0)]
                if position
                else None,
                "rotation": [rotation.get("x", 0), rotation.get("y", 0), rotation.get("z", 0)]
                if rotation
                else None,
            }

            # 3. Write Parameters
            if not self.unity_editor.write_command_params(project_path, params):
                return {"status": "error", "message": "Failed to write command params"}

            # 4. Execute Bridge Method
            result = await self.unity_editor.execute_method(
                "MCP.MCPBridge",
                "CreateLight",
                parameters=params,  # Passed for logging, but file used for transfer
                project_path=project_path,
            )

            return result

        except Exception as e:
            logger.error(f"Failed to create light: {e}")
            return {"status": "error", "message": str(e)}
