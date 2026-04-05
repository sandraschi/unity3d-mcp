"""
World Labs Integration

Import and optimize 3D environments from World Labs' Marble and Chisel tools.
Supports mesh imports (OBJ, FBX, GLB) and Gaussian Splat rendering.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class WorldLabsManager:
    """Manages World Labs asset imports and Gaussian Splatting setup."""

    # Gaussian Splatting package info
    GAUSSIAN_SPLATTING_PACKAGE = {
        "name": "com.aras-p.gaussian-splatting",
        "git": "https://github.com/aras-p/UnityGaussianSplatting.git",
        "description": "Unity Gaussian Splatting renderer by Aras Pranckevičius",
    }

    # Supported mesh formats from Marble
    SUPPORTED_MESH_FORMATS = [".obj", ".fbx", ".glb", ".gltf"]

    # Gaussian splat formats
    SPLAT_FORMATS = [".ply", ".splat"]

    def __init__(self, config):
        self.config = config

    async def import_marble_world(
        self,
        source_path: str,
        project_path: str,
        asset_name: str = "",
        include_colliders: bool = True,
        optimize_for_vrchat: bool = False,
    ) -> Dict[str, Any]:
        """Import a World Labs Marble-generated world into Unity.

        Args:
            source_path: Path to exported Marble assets (folder or file)
            project_path: Unity project path
            asset_name: Name for the imported asset (auto-detected if empty)
            include_colliders: Import collision geometry separately
            optimize_for_vrchat: Apply VRChat-specific optimizations
        """
        try:
            source = Path(source_path)
            if not source.exists():
                return {"status": "error", "message": f"Source not found: {source_path}"}

            # Determine import type
            if source.is_file():
                return await self._import_single_file(source, project_path, asset_name, optimize_for_vrchat)
            else:
                return await self._import_marble_folder(
                    source, project_path, asset_name, include_colliders, optimize_for_vrchat
                )

        except Exception as e:
            logger.error(f"Failed to import Marble world: {e}")
            return {"status": "error", "message": str(e)}

    async def _import_single_file(
        self,
        source: Path,
        project_path: str,
        asset_name: str,
        optimize_for_vrchat: bool,
    ) -> Dict[str, Any]:
        """Import a single mesh or splat file."""
        suffix = source.suffix.lower()
        name = asset_name or source.stem

        if suffix in self.SUPPORTED_MESH_FORMATS:
            return await self._import_mesh(source, project_path, name, optimize_for_vrchat)
        elif suffix in self.SPLAT_FORMATS:
            return await self._import_gaussian_splat(source, project_path, name)
        else:
            return {
                "status": "error",
                "message": (
                    f"Unsupported format: {suffix}. Supported: {self.SUPPORTED_MESH_FORMATS + self.SPLAT_FORMATS}"
                ),
            }

    async def _import_marble_folder(
        self,
        source: Path,
        project_path: str,
        asset_name: str,
        include_colliders: bool,
        optimize_for_vrchat: bool,
    ) -> Dict[str, Any]:
        """Import a folder of Marble exports."""
        name = asset_name or source.name

        # Create destination folders
        dest_base = Path(project_path) / "Assets" / "WorldLabs" / name
        dest_visuals = dest_base / "Visuals"
        dest_colliders = dest_base / "Colliders"
        dest_splats = dest_base / "Splats"

        for folder in [dest_visuals, dest_colliders, dest_splats]:
            folder.mkdir(parents=True, exist_ok=True)

        imported = {"meshes": [], "splats": [], "colliders": [], "textures": []}

        # Find and copy all assets
        for file in source.rglob("*"):
            if not file.is_file():
                continue

            suffix = file.suffix.lower()

            # Meshes
            if suffix in self.SUPPORTED_MESH_FORMATS:
                if "collider" in file.stem.lower() or "collision" in file.stem.lower():
                    if include_colliders:
                        dest = dest_colliders / file.name
                        shutil.copy2(file, dest)
                        imported["colliders"].append(str(dest))
                else:
                    dest = dest_visuals / file.name
                    shutil.copy2(file, dest)
                    imported["meshes"].append(str(dest))

            # Gaussian splats
            elif suffix in self.SPLAT_FORMATS:
                dest = dest_splats / file.name
                shutil.copy2(file, dest)
                imported["splats"].append(str(dest))

            # Textures
            elif suffix in [".png", ".jpg", ".jpeg", ".tga", ".exr"]:
                dest = dest_visuals / file.name
                shutil.copy2(file, dest)
                imported["textures"].append(str(dest))

        # Check if Gaussian Splatting is needed
        splat_setup = None
        if imported["splats"]:
            splat_setup = await self.check_gaussian_splatting_installed(project_path)
            if not splat_setup.get("installed"):
                splat_setup["recommendation"] = "Install Gaussian Splatting package to render .ply/.splat files"

        result = {
            "status": "success",
            "message": f"Imported Marble world: {name}",
            "asset_name": name,
            "destination": str(dest_base),
            "imported_files": imported,
            "file_counts": {k: len(v) for k, v in imported.items()},
        }

        if splat_setup:
            result["gaussian_splatting"] = splat_setup

        if optimize_for_vrchat:
            result["vrchat_notes"] = [
                "Consider baking lighting for better VR performance",
                "Check polygon count - VRChat recommends < 50k for Good rank",
                "Add VRC_SceneDescriptor to your scene",
                "Test with VRWorld Toolkit before upload",
            ]

        return result

    async def _import_mesh(
        self,
        source: Path,
        project_path: str,
        name: str,
        optimize_for_vrchat: bool,
    ) -> Dict[str, Any]:
        """Import a single mesh file."""
        dest_folder = Path(project_path) / "Assets" / "WorldLabs" / name
        dest_folder.mkdir(parents=True, exist_ok=True)

        dest_file = dest_folder / source.name
        shutil.copy2(source, dest_file)

        result = {
            "status": "success",
            "message": f"Imported mesh: {source.name}",
            "mesh_path": str(dest_file),
            "format": source.suffix,
            "unity_import_path": f"Assets/WorldLabs/{name}/{source.name}",
        }

        if optimize_for_vrchat:
            result["vrchat_optimization"] = {
                "recommended_actions": [
                    "Set mesh import to 'Optimize Mesh'",
                    "Enable mesh compression",
                    "Generate lightmap UVs if baking",
                    "Set texture compression to DXT1/DXT5",
                ],
            }

        return result

    async def _import_gaussian_splat(
        self,
        source: Path,
        project_path: str,
        name: str,
    ) -> Dict[str, Any]:
        """Import a Gaussian Splat file."""
        # Check if Gaussian Splatting is installed
        gs_check = await self.check_gaussian_splatting_installed(project_path)

        dest_folder = Path(project_path) / "Assets" / "WorldLabs" / name / "Splats"
        dest_folder.mkdir(parents=True, exist_ok=True)

        dest_file = dest_folder / source.name
        shutil.copy2(source, dest_file)

        result = {
            "status": "success",
            "message": f"Imported Gaussian Splat: {source.name}",
            "splat_path": str(dest_file),
            "unity_import_path": f"Assets/WorldLabs/{name}/Splats/{source.name}",
            "gaussian_splatting_installed": gs_check.get("installed", False),
        }

        if not gs_check.get("installed"):
            result["warning"] = "Gaussian Splatting package not installed"
            result["install_instructions"] = [
                "Install via: install_gaussian_splatting(project_path)",
                "Or manually add to manifest.json",
                "Package: " + self.GAUSSIAN_SPLATTING_PACKAGE["git"],
            ]

        return result

    async def check_gaussian_splatting_installed(self, project_path: str) -> Dict[str, Any]:
        """Check if Gaussian Splatting renderer is installed."""
        try:
            manifest_path = Path(project_path) / "Packages" / "manifest.json"

            if not manifest_path.exists():
                return {"status": "error", "installed": False, "message": "Not a valid Unity project"}

            with open(manifest_path) as f:
                manifest = json.load(f)

            dependencies = manifest.get("dependencies", {})

            # Check for Gaussian Splatting packages
            gs_packages = [
                "com.aras-p.gaussian-splatting",
                "gaussian-splatting",
                "com.unity.gaussian-splatting",
            ]

            for pkg in gs_packages:
                if pkg in dependencies:
                    return {
                        "status": "success",
                        "installed": True,
                        "package": pkg,
                        "version": dependencies[pkg],
                    }

            # Also check for it in any dependency
            for dep_name in dependencies:
                if "gaussian" in dep_name.lower() or "splat" in dep_name.lower():
                    return {
                        "status": "success",
                        "installed": True,
                        "package": dep_name,
                        "version": dependencies[dep_name],
                    }

            return {
                "status": "success",
                "installed": False,
                "message": "Gaussian Splatting not installed",
            }

        except Exception as e:
            return {"status": "error", "installed": False, "message": str(e)}

    async def install_gaussian_splatting(self, project_path: str) -> Dict[str, Any]:
        """Install Gaussian Splatting renderer package."""
        try:
            manifest_path = Path(project_path) / "Packages" / "manifest.json"

            if not manifest_path.exists():
                return {"status": "error", "message": "Not a valid Unity project"}

            # Check if already installed
            check = await self.check_gaussian_splatting_installed(project_path)
            if check.get("installed"):
                return {
                    "status": "success",
                    "message": "Gaussian Splatting already installed",
                    "package": check.get("package"),
                    "already_installed": True,
                }

            with open(manifest_path) as f:
                manifest = json.load(f)

            dependencies = manifest.get("dependencies", {})
            dependencies[self.GAUSSIAN_SPLATTING_PACKAGE["name"]] = self.GAUSSIAN_SPLATTING_PACKAGE["git"]

            manifest["dependencies"] = dependencies
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            return {
                "status": "success",
                "message": "Gaussian Splatting package added to manifest.json",
                "package": self.GAUSSIAN_SPLATTING_PACKAGE["name"],
                "source": self.GAUSSIAN_SPLATTING_PACKAGE["git"],
                "next_steps": [
                    "Open Unity to download and import the package",
                    "Create a GaussianSplatRenderer component in your scene",
                    "Assign your .ply files to the renderer",
                ],
            }

        except Exception as e:
            logger.error(f"Failed to install Gaussian Splatting: {e}")
            return {"status": "error", "message": str(e)}

    async def optimize_for_vrchat(
        self,
        project_path: str,
        asset_folder: str,
        target_polygon_count: int = 50000,
    ) -> Dict[str, Any]:
        """Provide optimization recommendations for VRChat.

        Note: Actual mesh decimation requires Unity Editor operations.
        This provides analysis and recommendations.
        """
        try:
            asset_path = Path(project_path) / "Assets" / asset_folder

            if not asset_path.exists():
                return {"status": "error", "message": f"Asset folder not found: {asset_folder}"}

            # Analyze assets
            meshes = list(asset_path.rglob("*.fbx")) + list(asset_path.rglob("*.obj"))
            textures = list(asset_path.rglob("*.png")) + list(asset_path.rglob("*.jpg"))
            splats = list(asset_path.rglob("*.ply")) + list(asset_path.rglob("*.splat"))

            recommendations = []

            # Mesh recommendations
            if meshes:
                recommendations.append(
                    {
                        "category": "Meshes",
                        "count": len(meshes),
                        "actions": [
                            f"Target polygon count: {target_polygon_count}",
                            "Enable 'Optimize Mesh' in import settings",
                            "Set mesh compression to 'High'",
                            "Generate lightmap UVs for baked lighting",
                        ],
                    }
                )

            # Texture recommendations
            if textures:
                total_size = sum(t.stat().st_size for t in textures)
                recommendations.append(
                    {
                        "category": "Textures",
                        "count": len(textures),
                        "total_size_mb": round(total_size / (1024 * 1024), 2),
                        "actions": [
                            "Set max texture size to 2048 or lower",
                            "Use DXT1 compression for opaque textures",
                            "Use DXT5 for textures with alpha",
                            "Consider texture atlasing",
                        ],
                    }
                )

            # Splat warnings
            if splats:
                recommendations.append(
                    {
                        "category": "Gaussian Splats",
                        "count": len(splats),
                        "warning": "Gaussian Splats may not be VRChat-compatible",
                        "actions": [
                            "Convert to mesh using Marble's mesh export option",
                            "Or bake splats to textured mesh before upload",
                            "Check VRChat allowlist for supported components",
                        ],
                    }
                )

            # General VRChat recommendations
            recommendations.append(
                {
                    "category": "VRChat Setup",
                    "actions": [
                        "Install VRChat SDK if not present",
                        "Add VRC_SceneDescriptor to scene",
                        "Set spawn point and respawn height",
                        "Use VRWorld Toolkit for validation",
                        "Test in VRChat before public upload",
                    ],
                }
            )

            return {
                "status": "success",
                "asset_folder": asset_folder,
                "recommendations": recommendations,
                "vrchat_performance_tips": {
                    "excellent": "< 7,500 polygons, < 1 material",
                    "good": "< 10,000 polygons, < 4 materials",
                    "medium": "< 15,000 polygons, < 8 materials",
                    "poor": "< 20,000 polygons, < 16 materials",
                },
            }

        except Exception as e:
            logger.error(f"Failed to analyze for VRChat: {e}")
            return {"status": "error", "message": str(e)}
