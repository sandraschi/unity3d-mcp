"""Fleet handoff import helpers (Blender GLB/VRM/FBX -> Unity Assets)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SUPPORTED_FLEET_FORMATS = ("glb", "gltf", "fbx", "obj", "vrm", "dae", "stl")
DEFAULT_BLENDER_SUBDIR = "BlenderImports"


async def import_blender_asset(
    import_manager: Any,
    *,
    file_path: str,
    project_path: str,
    assets_subdir: str = DEFAULT_BLENDER_SUBDIR,
    import_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Import a single Blender-exported asset into Unity project Assets folder."""
    source = Path(file_path)
    if not source.is_file():
        return {"success": False, "error": f"File not found: {file_path}"}

    ext = source.suffix.lower().lstrip(".")
    if ext not in SUPPORTED_FLEET_FORMATS:
        return {
            "success": False,
            "error": f"Unsupported format .{ext}",
            "supported_formats": list(SUPPORTED_FLEET_FORMATS),
        }

    project_assets = Path(project_path) / "Assets" / assets_subdir
    try:
        project_assets.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"success": False, "error": f"Cannot create Assets folder: {exc}"}

    settings = {
        "import_materials": True,
        "import_animations": ext in ("fbx", "glb", "gltf", "vrm"),
        "source": "blender-mcp",
        **(import_settings or {}),
    }

    result = await import_manager.import_3d_model(
        model_path=str(source),
        project_path=project_path,
        model_format=ext,
        import_settings=settings,
    )

    payload: dict[str, Any] = {
        "success": bool(result.get("success")),
        "source": "blender-mcp",
        "file_path": str(source),
        "project_path": project_path,
        "assets_subdir": assets_subdir,
        "format": ext,
        "import_result": result,
    }
    if result.get("destination_path"):
        payload["destination_path"] = result["destination_path"]
    if not payload["success"]:
        payload["error"] = result.get("error") or "Import failed"
    return payload


async def import_fleet_batch(
    import_manager: Any,
    *,
    input_dir: str,
    project_path: str,
    pattern: str = "*.glb",
    assets_subdir: str = DEFAULT_BLENDER_SUBDIR,
) -> dict[str, Any]:
    """Import all matching files from a Blender export directory."""
    directory = Path(input_dir)
    if not directory.is_dir():
        return {"success": False, "error": f"input_dir not found: {input_dir}"}

    imported: list[dict[str, Any]] = []
    errors: list[str] = []
    for file_path in sorted(directory.glob(pattern)):
        if not file_path.is_file():
            continue
        result = await import_blender_asset(
            import_manager,
            file_path=str(file_path),
            project_path=project_path,
            assets_subdir=assets_subdir,
        )
        imported.append(result)
        if not result.get("success"):
            errors.append(f"{file_path.name}: {result.get('error', 'failed')}")

    return {
        "success": len(imported) > 0 and not errors,
        "imported_count": len(imported),
        "imports": imported,
        "errors": errors,
        "partial_success": bool(imported) and bool(errors),
    }
