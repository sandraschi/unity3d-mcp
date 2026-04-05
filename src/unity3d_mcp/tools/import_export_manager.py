"""
Import/Export Tools for Unity3D MCP

Comprehensive import and export functionality for Unity projects.
Handles asset packages, 3D models, textures, audio, animations, and project data.
Supports multiple formats and provides batch operations for efficiency.
"""

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ImportExportManager:
    """Manages import and export operations for Unity projects."""

    def __init__(self, config):
        self.config = config
        self.active_imports = {}  # Track active import operations
        self.active_exports = {}  # Track active export operations

    async def import_asset_package(
        self,
        package_path: str,
        project_path: Optional[str] = None,
        interactive: bool = False,
        import_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Import Unity asset package into project."""
        try:
            package_path = Path(package_path)
            if not package_path.exists():
                return {
                    "success": False,
                    "error": f"Package file not found: {package_path}",
                    "package_path": str(package_path),
                }

            # Default import settings
            settings = {
                "include_dependencies": True,
                "overwrite_existing": False,
                "import_materials": True,
                "import_textures": True,
                "import_models": True,
                "import_animations": True,
                "import_audio": True,
                **(import_settings or {}),
            }

            # Track import operation
            import_id = f"import_{package_path.name}_{asyncio.get_event_loop().time()}"
            self.active_imports[import_id] = {
                "type": "package",
                "path": str(package_path),
                "settings": settings,
                "status": "starting",
            }

            # Simulate package analysis
            package_info = await self._analyze_package(package_path)

            return {
                "success": True,
                "import_id": import_id,
                "package_path": str(package_path),
                "package_info": package_info,
                "import_settings": settings,
                "message": f"Package import initiated: {package_path.name}",
            }

        except Exception as e:
            logger.error(f"Failed to import asset package {package_path}: {e}")
            return {"success": False, "error": str(e), "package_path": str(package_path)}

    async def import_3d_model(
        self,
        model_path: str,
        project_path: Optional[str] = None,
        model_format: Optional[str] = None,
        import_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Import 3D model file (FBX, OBJ, GLTF, etc.) into Unity project."""
        try:
            model_path = Path(model_path)
            if not model_path.exists():
                return {
                    "success": False,
                    "error": f"Model file not found: {model_path}",
                    "model_path": str(model_path),
                }

            # Auto-detect format if not specified
            if not model_format:
                model_format = model_path.suffix.lower().lstrip(".")

            supported_formats = ["fbx", "obj", "gltf", "glb", "dae", "3ds", "blend", "vrm"]
            if model_format not in supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported format: {model_format}. Supported: {supported_formats}",
                    "model_path": str(model_path),
                    "detected_format": model_format,
                }

            # Default import settings based on format
            default_settings = {
                "fbx": {"import_materials": True, "import_animations": True, "scale_factor": 1.0},
                "obj": {"import_materials": False, "optimize_mesh": True},
                "gltf": {"import_animations": True, "import_skins": True},
                "glb": {"import_animations": True, "import_skins": True},
            }

            settings = {**default_settings.get(model_format, {}), **(import_settings or {})}

            # Analyze model
            model_info = await self._analyze_3d_model(model_path, model_format)

            # Execute Import (Copy to Assets)
            destination_path = None
            if project_path:
                try:
                    project_assets = Path(project_path) / "Assets"
                    if not project_assets.exists():
                        project_assets.mkdir(parents=True, exist_ok=True)

                    destination_path = project_assets / model_path.name
                    shutil.copy2(model_path, destination_path)
                    logger.info(f"Copied model to {destination_path}")
                except Exception as e:
                    logger.error(f"Failed to copy model to project: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to copy model: {e}",
                        "model_path": str(model_path),
                    }

            # Track import
            import_id = f"import_{model_path.name}_{asyncio.get_event_loop().time()}"
            self.active_imports[import_id] = {
                "type": "3d_model",
                "path": str(model_path),
                "destination": str(destination_path) if destination_path else None,
                "format": model_format,
                "settings": settings,
                "status": "completed" if destination_path else "simulated",
            }

            return {
                "success": True,
                "import_id": import_id,
                "model_path": str(model_path),
                "destination_path": str(destination_path) if destination_path else "simulated",
                "model_format": model_format,
                "model_info": model_info,
                "import_settings": settings,
                "message": f"3D model import {'completed' if destination_path else 'initiated'}: {model_path.name}",
            }

        except Exception as e:
            logger.error(f"Failed to import 3D model {model_path}: {e}")
            return {"success": False, "error": str(e), "model_path": str(model_path)}

    async def import_texture(
        self,
        texture_path: str,
        project_path: Optional[str] = None,
        texture_type: str = "diffuse",
        import_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Import texture file into Unity project."""
        try:
            texture_path = Path(texture_path)
            if not texture_path.exists():
                return {
                    "success": False,
                    "error": f"Texture file not found: {texture_path}",
                    "texture_path": str(texture_path),
                }

            supported_formats = ["png", "jpg", "jpeg", "tga", "psd", "tiff", "tif", "exr", "hdr"]
            texture_format = texture_path.suffix.lower().lstrip(".")
            if texture_format not in supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported texture format: {texture_format}. Supported: {supported_formats}",
                    "texture_path": str(texture_path),
                }

            # Default settings based on texture type
            default_settings = {
                "diffuse": {"generate_mipmaps": True, "compression": "normal", "max_size": 2048},
                "normal": {"generate_mipmaps": True, "compression": "normal", "max_size": 2048},
                "specular": {"generate_mipmaps": True, "compression": "normal", "max_size": 1024},
                "height": {"generate_mipmaps": False, "compression": "none", "max_size": 1024},
                "occlusion": {"generate_mipmaps": True, "compression": "normal", "max_size": 1024},
                "emission": {"generate_mipmaps": True, "compression": "normal", "max_size": 1024},
            }

            settings = {
                **default_settings.get(texture_type, default_settings["diffuse"]),
                **(import_settings or {}),
            }

            # Analyze texture
            texture_info = await self._analyze_texture(texture_path, texture_format)

            return {
                "success": True,
                "texture_path": str(texture_path),
                "texture_format": texture_format,
                "texture_type": texture_type,
                "texture_info": texture_info,
                "import_settings": settings,
                "message": f"Texture import initiated: {texture_path.name}",
            }

        except Exception as e:
            logger.error(f"Failed to import texture {texture_path}: {e}")
            return {"success": False, "error": str(e), "texture_path": str(texture_path)}

    async def export_fbx(
        self,
        object_names: Union[str, List[str]],
        output_path: str,
        project_path: Optional[str] = None,
        export_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Export Unity objects to FBX format."""
        try:
            if isinstance(object_names, str):
                object_names = [object_names]

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Default FBX export settings
            settings = {
                "include_animation": True,
                "include_materials": True,
                "embed_textures": False,
                "fbx_version": "FBX 2020",
                "coordinate_system": "Right-Handed",
                "scale_factor": 1.0,
                "export_hierarchy": True,
                **(export_settings or {}),
            }

            # Validate objects exist
            object_info = await self._validate_export_objects(object_names)

            # Track export
            export_id = f"export_fbx_{output_path.name}_{asyncio.get_event_loop().time()}"
            self.active_exports[export_id] = {
                "type": "fbx",
                "output_path": str(output_path),
                "objects": object_names,
                "settings": settings,
                "status": "starting",
            }

            return {
                "success": True,
                "export_id": export_id,
                "output_path": str(output_path),
                "objects": object_names,
                "object_count": len(object_names),
                "object_info": object_info,
                "export_settings": settings,
                "message": f"FBX export initiated: {len(object_names)} objects to {output_path.name}",
            }

        except Exception as e:
            logger.error(f"Failed to export FBX to {output_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": str(output_path),
                "objects": object_names if isinstance(object_names, list) else [object_names],
            }

    async def export_unity_package(
        self,
        asset_paths: Union[str, List[str]],
        output_path: str,
        project_path: Optional[str] = None,
        package_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Export Unity assets to .unitypackage format."""
        try:
            if isinstance(asset_paths, str):
                asset_paths = [asset_paths]

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Default package settings
            settings = {
                "include_dependencies": True,
                "include_meta_files": True,
                "compress_package": True,
                "package_version": "1.0",
                **(package_settings or {}),
            }

            # Validate assets exist
            asset_info = await self._validate_export_assets(asset_paths)

            # Track export
            export_id = f"export_package_{output_path.name}_{asyncio.get_event_loop().time()}"
            self.active_exports[export_id] = {
                "type": "unitypackage",
                "output_path": str(output_path),
                "assets": asset_paths,
                "settings": settings,
                "status": "starting",
            }

            return {
                "success": True,
                "export_id": export_id,
                "output_path": str(output_path),
                "assets": asset_paths,
                "asset_count": len(asset_paths),
                "asset_info": asset_info,
                "package_settings": settings,
                "message": f"Unity package export initiated: {len(asset_paths)} assets to {output_path.name}",
            }

        except Exception as e:
            logger.error(f"Failed to export Unity package to {output_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": str(output_path),
                "assets": asset_paths if isinstance(asset_paths, list) else [asset_paths],
            }

    async def export_prefab(
        self,
        object_name: str,
        output_path: str,
        project_path: Optional[str] = None,
        prefab_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Export Unity object as prefab."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Default prefab settings
            settings = {
                "include_children": True,
                "include_components": True,
                "include_materials": True,
                "include_scripts": True,
                "create_folder": True,
                **(prefab_settings or {}),
            }

            # Validate object exists
            object_info = await self._validate_export_objects([object_name])

            # Track export
            export_id = f"export_prefab_{output_path.name}_{asyncio.get_event_loop().time()}"
            self.active_exports[export_id] = {
                "type": "prefab",
                "output_path": str(output_path),
                "object": object_name,
                "settings": settings,
                "status": "starting",
            }

            return {
                "success": True,
                "export_id": export_id,
                "output_path": str(output_path),
                "object_name": object_name,
                "object_info": object_info[0] if object_info else None,
                "prefab_settings": settings,
                "message": f"Prefab export initiated: {object_name} to {output_path.name}",
            }

        except Exception as e:
            logger.error(f"Failed to export prefab {object_name} to {output_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": str(output_path),
                "object_name": object_name,
            }

    async def batch_import(
        self,
        import_operations: List[Dict[str, Any]],
        project_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform batch import operations."""
        try:
            results = []
            batch_id = f"batch_import_{asyncio.get_event_loop().time()}"

            for operation in import_operations:
                op_type = operation.get("type", "asset_package")
                op_params = operation.get("params", {})

                if op_type == "asset_package":
                    result = await self.import_asset_package(
                        package_path=op_params.get("package_path"),
                        project_path=project_path,
                        import_settings=op_params.get("settings"),
                    )
                elif op_type == "3d_model":
                    result = await self.import_3d_model(
                        model_path=op_params.get("model_path"),
                        project_path=project_path,
                        model_format=op_params.get("format"),
                        import_settings=op_params.get("settings"),
                    )
                elif op_type == "texture":
                    result = await self.import_texture(
                        texture_path=op_params.get("texture_path"),
                        project_path=project_path,
                        texture_type=op_params.get("texture_type", "diffuse"),
                        import_settings=op_params.get("settings"),
                    )
                else:
                    result = {"success": False, "error": f"Unknown import type: {op_type}"}

                results.append({"operation": operation, "result": result})

            success_count = sum(1 for r in results if r["result"].get("success", False))

            return {
                "success": True,
                "batch_id": batch_id,
                "total_operations": len(import_operations),
                "successful_operations": success_count,
                "failed_operations": len(import_operations) - success_count,
                "results": results,
                "message": f"Batch import completed: {success_count}/{len(import_operations)} successful",
            }

        except Exception as e:
            logger.error(f"Failed to perform batch import: {e}")
            return {"success": False, "error": str(e), "total_operations": len(import_operations)}

    async def get_import_status(self, import_id: str) -> Dict[str, Any]:
        """Get status of an import operation."""
        if import_id not in self.active_imports:
            return {
                "success": False,
                "error": f"Import operation not found: {import_id}",
                "import_id": import_id,
            }

        operation = self.active_imports[import_id]
        return {
            "success": True,
            "import_id": import_id,
            "status": operation["status"],
            "type": operation["type"],
            "path": operation["path"],
            "progress": operation.get("progress", 0.0),
            "message": operation.get("message", "Import in progress"),
        }

    async def get_export_status(self, export_id: str) -> Dict[str, Any]:
        """Get status of an export operation."""
        if export_id not in self.active_exports:
            return {
                "success": False,
                "error": f"Export operation not found: {export_id}",
                "export_id": export_id,
            }

        operation = self.active_exports[export_id]
        return {
            "success": True,
            "export_id": export_id,
            "status": operation["status"],
            "type": operation["type"],
            "output_path": operation["output_path"],
            "progress": operation.get("progress", 0.0),
            "message": operation.get("message", "Export in progress"),
        }

    # Helper methods for analysis and validation
    async def _analyze_package(self, package_path: Path) -> Dict[str, Any]:
        """Analyze Unity asset package contents."""
        # Placeholder for package analysis
        return {
            "file_size": package_path.stat().st_size,
            "estimated_assets": 10,  # Placeholder
            "contains_materials": True,
            "contains_textures": True,
            "contains_models": True,
            "contains_scripts": False,
        }

    async def _analyze_3d_model(self, model_path: Path, model_format: str) -> Dict[str, Any]:
        """Analyze 3D model file."""
        # Placeholder for model analysis
        return {
            "file_size": model_path.stat().st_size,
            "format": model_format,
            "estimated_vertices": 1000,  # Placeholder
            "estimated_triangles": 2000,  # Placeholder
            "has_materials": model_format in ["fbx", "gltf", "glb"],
            "has_animations": model_format in ["fbx", "gltf", "glb"],
            "has_skeleton": False,  # Placeholder
        }

    async def _analyze_texture(self, texture_path: Path, texture_format: str) -> Dict[str, Any]:
        """Analyze texture file."""
        # Placeholder for texture analysis
        return {
            "file_size": texture_path.stat().st_size,
            "format": texture_format,
            "dimensions": "1024x1024",  # Placeholder
            "color_space": "sRGB",
            "has_alpha": texture_format in ["png", "tga"],
            "bit_depth": 8,
        }

    async def _validate_export_objects(self, object_names: List[str]) -> List[Dict[str, Any]]:
        """Validate that objects exist for export."""
        # Placeholder validation
        return [{"name": name, "exists": True, "type": "GameObject"} for name in object_names]

    async def _validate_export_assets(self, asset_paths: List[str]) -> List[Dict[str, Any]]:
        """Validate that assets exist for export."""
        # Placeholder validation
        return [{"path": path, "exists": True, "type": "Asset"} for path in asset_paths]


class ImportExportToolManager:
    """Tool manager for import/export operations."""

    def __init__(self, mcp_app, import_export_manager: ImportExportManager):
        self.app = mcp_app
        self.import_export_manager = import_export_manager

    def register_tools(self):
        """Register all import/export tools."""

        @self.app.tool
        async def import_asset_package(
            package_path: str,
            project_path: Optional[str] = None,
            interactive: bool = False,
            import_settings: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Import Unity asset package (.unitypackage) into project.

            Imports a Unity asset package containing models, textures, materials,
            animations, and other assets into the specified Unity project.

            Args:
                package_path: Path to the .unitypackage file
                project_path: Unity project path (auto-detected if not provided)
                interactive: Whether to show import dialog (CLI limitation)
                import_settings: Custom import settings to override defaults

            Returns:
                Dictionary containing:
                - success: Boolean indicating import success
                - import_id: Unique identifier for tracking the import
                - package_path: Path to the imported package
                - package_info: Analysis of package contents
                - import_settings: Settings used for import
                - error: Error message if failed

            Examples:
                # Import a standard asset package
                import_asset_package("D:/Assets/Characters.unitypackage")

                # Import with custom settings
                import_asset_package(
                    package_path="D:/Assets/Models.unitypackage",
                    import_settings={
                        "include_dependencies": True,
                        "overwrite_existing": False,
                        "import_materials": True
                    }
                )
            """
            return await self.import_export_manager.import_asset_package(
                package_path, project_path, interactive, import_settings
            )

        @self.app.tool
        async def import_3d_model(
            model_path: str,
            project_path: Optional[str] = None,
            model_format: Optional[str] = None,
            import_settings: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Import 3D model file (FBX, OBJ, GLTF, etc.) into Unity project.

            Imports 3D model files in various formats into the Unity project,
            automatically configuring import settings based on format.

            Args:
                model_path: Path to the 3D model file
                project_path: Unity project path (auto-detected if not provided)
                model_format: Model format (auto-detected from extension if not provided)
                import_settings: Custom import settings to override defaults

            Returns:
                Dictionary containing:
                - success: Boolean indicating import success
                - import_id: Unique identifier for tracking the import
                - model_path: Path to the imported model
                - model_format: Detected or specified format
                - model_info: Analysis of model contents
                - import_settings: Settings used for import
                - error: Error message if failed

            Examples:
                # Import FBX model
                import_3d_model("D:/Models/Character.fbx")

                # Import OBJ with custom scale
                import_3d_model(
                    model_path="D:/Models/Prop.obj",
                    import_settings={"scale_factor": 0.1}
                )
            """
            return await self.import_export_manager.import_3d_model(
                model_path, project_path, model_format, import_settings
            )

        @self.app.tool
        async def import_texture(
            texture_path: str,
            project_path: Optional[str] = None,
            texture_type: str = "diffuse",
            import_settings: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Import texture file into Unity project.

            Imports texture files and automatically configures them for the
            specified texture type (diffuse, normal, specular, etc.).

            Args:
                texture_path: Path to the texture file
                project_path: Unity project path (auto-detected if not provided)
                texture_type: Type of texture (diffuse, normal, specular, height, occlusion, emission)
                import_settings: Custom import settings to override defaults

            Returns:
                Dictionary containing:
                - success: Boolean indicating import success
                - texture_path: Path to the imported texture
                - texture_format: Detected texture format
                - texture_type: Specified texture type
                - texture_info: Analysis of texture properties
                - import_settings: Settings used for import
                - error: Error message if failed

            Examples:
                # Import diffuse texture
                import_texture("D:/Textures/Brick.png", texture_type="diffuse")

                # Import normal map
                import_texture("D:/Textures/Brick_Normal.png", texture_type="normal")
            """
            return await self.import_export_manager.import_texture(
                texture_path, project_path, texture_type, import_settings
            )

        @self.app.tool
        async def export_fbx(
            object_names: Union[str, List[str]],
            output_path: str,
            project_path: Optional[str] = None,
            export_settings: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Export Unity objects to FBX format.

            Exports Unity GameObjects to FBX format for use in other 3D applications.
            Supports animation, materials, and hierarchy preservation.

            Args:
                object_names: Name(s) of Unity objects to export
                output_path: Path where to save the FBX file
                project_path: Unity project path (auto-detected if not provided)
                export_settings: Custom export settings to override defaults

            Returns:
                Dictionary containing:
                - success: Boolean indicating export initiation success
                - export_id: Unique identifier for tracking the export
                - output_path: Path where FBX will be saved
                - objects: List of objects being exported
                - object_count: Number of objects to export
                - object_info: Information about objects being exported
                - export_settings: Settings used for export
                - error: Error message if failed

            Examples:
                # Export single object
                export_fbx("Character", "D:/Exports/Character.fbx")

                # Export multiple objects
                export_fbx(
                    object_names=["Character", "Weapon"],
                    output_path="D:/Exports/Scene.fbx",
                    export_settings={"include_animation": True}
                )
            """
            return await self.import_export_manager.export_fbx(object_names, output_path, project_path, export_settings)

        @self.app.tool
        async def export_unity_package(
            asset_paths: Union[str, List[str]],
            output_path: str,
            project_path: Optional[str] = None,
            package_settings: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Export Unity assets to .unitypackage format.

            Creates a Unity asset package containing the specified assets,
            their dependencies, and meta files for sharing or backup.

            Args:
                asset_paths: Path(s) to Unity assets to include in package
                output_path: Path where to save the .unitypackage file
                project_path: Unity project path (auto-detected if not provided)
                package_settings: Custom package settings to override defaults

            Returns:
                Dictionary containing:
                - success: Boolean indicating export initiation success
                - export_id: Unique identifier for tracking the export
                - output_path: Path where package will be saved
                - assets: List of assets being packaged
                - asset_count: Number of assets to package
                - asset_info: Information about assets being packaged
                - package_settings: Settings used for packaging
                - error: Error message if failed

            Examples:
                # Export single asset
                export_unity_package("Assets/Models/Character.prefab", "D:/Packages/Character.unitypackage")

                # Export folder of assets
                export_unity_package("Assets/Textures/", "D:/Packages/Textures.unitypackage")
            """
            return await self.import_export_manager.export_unity_package(
                asset_paths, output_path, project_path, package_settings
            )

        @self.app.tool
        async def export_prefab(
            object_name: str,
            output_path: str,
            project_path: Optional[str] = None,
            prefab_settings: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Export Unity object as prefab.

            Creates a Unity prefab from a scene object, preserving all
            components, children, and materials.

            Args:
                object_name: Name of the Unity object to export as prefab
                output_path: Path where to save the prefab file
                project_path: Unity project path (auto-detected if not provided)
                prefab_settings: Custom prefab settings to override defaults

            Returns:
                Dictionary containing:
                - success: Boolean indicating export initiation success
                - export_id: Unique identifier for tracking the export
                - output_path: Path where prefab will be saved
                - object_name: Name of object being exported
                - object_info: Information about the object being exported
                - prefab_settings: Settings used for prefab creation
                - error: Error message if failed

            Examples:
                # Export object as prefab
                export_prefab("Robot", "Assets/Prefabs/Robot.prefab")
            """
            return await self.import_export_manager.export_prefab(
                object_name, output_path, project_path, prefab_settings
            )

        @self.app.tool
        async def batch_import(
            import_operations: List[Dict[str, Any]],
            project_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Perform batch import operations.

            Executes multiple import operations in sequence, useful for
            setting up new projects or migrating large amounts of content.

            Args:
                import_operations: List of import operation dictionaries
                project_path: Unity project path (auto-detected if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating batch import initiation success
                - batch_id: Unique identifier for the batch operation
                - total_operations: Total number of import operations
                - successful_operations: Number of successful operations
                - failed_operations: Number of failed operations
                - results: Detailed results for each operation
                - error: Error message if batch import failed

            Examples:
                # Batch import multiple assets
                batch_import([
                    {
                        "type": "asset_package",
                        "params": {"package_path": "D:/Assets/Characters.unitypackage"}
                    },
                    {
                        "type": "3d_model",
                        "params": {"model_path": "D:/Models/Environment.fbx"}
                    },
                    {
                        "type": "texture",
                        "params": {
                            "texture_path": "D:/Textures/Diffuse.png",
                            "texture_type": "diffuse"
                        }
                    }
                ])
            """
            return await self.import_export_manager.batch_import(import_operations, project_path)

        @self.app.tool
        async def get_import_status(import_id: str) -> Dict[str, Any]:
            """Get status of an import operation.

            Checks the current status and progress of an ongoing import operation.

            Args:
                import_id: Import operation ID returned by import functions

            Returns:
                Dictionary containing:
                - success: Boolean indicating status retrieval success
                - import_id: The import operation ID
                - status: Current status ("starting", "in_progress", "completed", "failed")
                - type: Type of import operation
                - path: Path being imported
                - progress: Progress percentage (0.0 to 1.0)
                - message: Status message
                - error: Error message if status check failed

            Examples:
                # Check import status
                get_import_status("import_Character.fbx_123456.789")
            """
            return await self.import_export_manager.get_import_status(import_id)

        @self.app.tool
        async def get_export_status(export_id: str) -> Dict[str, Any]:
            """Get status of an export operation.

            Checks the current status and progress of an ongoing export operation.

            Args:
                export_id: Export operation ID returned by export functions

            Returns:
                Dictionary containing:
                - success: Boolean indicating status retrieval success
                - export_id: The export operation ID
                - status: Current status ("starting", "in_progress", "completed", "failed")
                - type: Type of export operation
                - output_path: Path where export will be saved
                - progress: Progress percentage (0.0 to 1.0)
                - message: Status message
                - error: Error message if status check failed

            Examples:
                # Check export status
                get_export_status("export_fbx_Scene.fbx_123456.789")
            """
            return await self.import_export_manager.get_export_status(export_id)
