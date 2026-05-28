"""Scene and asset validation helpers for Unity Agent Lab."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PLATFORM_LIMITS: Dict[str, Dict[str, int]] = {
    "vrchat": {"polygons": 70000, "materials": 32, "bones": 256, "texture_mb": 200},
    "chilloutvr": {"polygons": 70000, "materials": 16, "bones": 400, "texture_mb": 256},
    "resonite": {"polygons": 100000, "materials": 20, "bones": 512, "texture_mb": 512},
    "cluster": {"polygons": 50000, "materials": 16, "bones": 256, "texture_mb": 128},
    "generic": {"polygons": 150000, "materials": 32, "bones": 512, "texture_mb": 512},
}


def list_platform_limits() -> Dict[str, Any]:
    return {
        "success": True,
        "platforms": PLATFORM_LIMITS,
        "notes": [
            "Bridge validate_scene provides live Editor counts when MCPBridge.cs is active.",
            "Disk checks use file heuristics; full SDK validation requires Unity Editor.",
        ],
    }


def _performance_rank(polygons: int, materials: int, limits: Dict[str, int]) -> str:
    poly_limit = limits.get("polygons", 70000)
    mat_limit = limits.get("materials", 32)
    if polygons <= poly_limit * 0.45 and materials <= max(4, mat_limit // 4):
        return "Excellent"
    if polygons <= poly_limit * 0.7 and materials <= max(8, mat_limit // 2):
        return "Good"
    if polygons <= poly_limit and materials <= mat_limit:
        return "Medium"
    return "Poor"


def evaluate_scene_metrics(
    metrics: Dict[str, Any],
    target_platform: str = "vrchat",
) -> Dict[str, Any]:
    limits = PLATFORM_LIMITS.get(target_platform.lower(), PLATFORM_LIMITS["generic"])
    polygons = int(metrics.get("triangle_count", metrics.get("polygons", 0)) or 0)
    materials = int(metrics.get("material_count", metrics.get("materials", 0)) or 0)
    missing_scripts = int(metrics.get("missing_script_count", metrics.get("missing_scripts", 0)) or 0)
    mesh_count = int(metrics.get("mesh_count", 0) or 0)

    errors: List[str] = []
    warnings: List[str] = []

    if polygons > limits["polygons"]:
        errors.append(f"Polygon count {polygons} exceeds {target_platform} limit {limits['polygons']}")
    elif polygons > limits["polygons"] * 0.85:
        warnings.append(f"Polygon count {polygons} is near {target_platform} limit {limits['polygons']}")

    if materials > limits["materials"]:
        errors.append(f"Material count {materials} exceeds {target_platform} limit {limits['materials']}")
    elif materials > limits["materials"] * 0.75:
        warnings.append(f"Material count {materials} is high for {target_platform}")

    if missing_scripts > 0:
        errors.append(f"{missing_scripts} missing script component(s) detected")

    rank = _performance_rank(polygons, materials, limits)
    valid = len(errors) == 0

    return {
        "success": True,
        "valid": valid,
        "target_platform": target_platform,
        "performance_rank": rank,
        "metrics": {
            "polygons": polygons,
            "materials": materials,
            "mesh_count": mesh_count,
            "missing_scripts": missing_scripts,
            "object_count": int(metrics.get("object_count", 0) or 0),
        },
        "limits": limits,
        "errors": errors,
        "warnings": warnings,
        "objects_with_missing_scripts": metrics.get("objects_with_missing_scripts", []),
    }


async def validate_scene_via_bridge(bridge: Any, target_platform: str = "vrchat") -> Dict[str, Any]:
    try:
        raw = await bridge.validate_scene()
    except Exception as exc:
        logger.exception("Bridge validate_scene failed: %s", exc)
        return {"success": False, "error": str(exc), "mode": "bridge"}

    if raw.get("error"):
        return {"success": False, "error": raw["error"], "mode": "bridge", "raw": raw}

    report = evaluate_scene_metrics(raw, target_platform=target_platform)
    report["mode"] = "bridge"
    report["scene_name"] = raw.get("scene_name", "")
    return report


def validate_model_file(model_path: str, target_platform: str = "generic") -> Dict[str, Any]:
    path = Path(model_path)
    if not path.is_file():
        return {"success": False, "error": f"File not found: {model_path}"}

    suffix = path.suffix.lower()
    supported = {".glb", ".gltf", ".fbx", ".obj", ".vrm", ".prefab"}
    if suffix not in supported:
        return {
            "success": False,
            "error": f"Unsupported format: {suffix}",
            "supported": sorted(supported),
        }

    size_mb = round(path.stat().st_size / (1024 * 1024), 2)
    limits = PLATFORM_LIMITS.get(target_platform.lower(), PLATFORM_LIMITS["generic"])
    warnings: List[str] = []
    errors: List[str] = []

    if size_mb > limits.get("texture_mb", 512):
        warnings.append(f"File size {size_mb} MB may be heavy for {target_platform}")

    if suffix == ".fbx" and target_platform == "resonite":
        warnings.append("GLB/VRM preferred for Resonite direct import")

    return {
        "success": True,
        "valid": len(errors) == 0,
        "target_platform": target_platform,
        "model_path": str(path),
        "format": suffix.lstrip("."),
        "file_size_mb": size_mb,
        "errors": errors,
        "warnings": warnings,
        "hint": "Use validate_scene with live bridge for accurate poly/material counts.",
    }


def validate_prefab_on_disk(project_path: str, prefab_path: str) -> Dict[str, Any]:
    project = Path(project_path)
    prefab = Path(prefab_path)
    if not prefab.is_absolute():
        candidate = project / prefab_path
        if candidate.is_file():
            prefab = candidate
        else:
            candidate = project / "Assets" / prefab_path
            if candidate.is_file():
                prefab = candidate

    if not prefab.is_file():
        return {"success": False, "error": f"Prefab not found: {prefab_path}"}

    result: Dict[str, Any] = {
        "success": True,
        "prefab_path": str(prefab),
        "valid": True,
        "errors": [],
        "warnings": [],
    }

    try:
        import UnityPy  # type: ignore

        env = UnityPy.load(str(prefab))
        mesh_count = 0
        for obj in env.objects:
            if obj.type.name in {"Mesh", "SkinnedMeshRenderer"}:
                mesh_count += 1
        result["mesh_assets"] = mesh_count
        if mesh_count == 0:
            result["warnings"].append("No mesh objects detected in prefab via UnityPy scan")
    except Exception as exc:
        logger.warning("UnityPy prefab scan failed: %s", exc)
        result["warnings"].append(f"UnityPy scan skipped: {exc}")

    return result
