"""Unified social VR platform audit (VRChat, CVR, Resonite, Cluster)."""

from __future__ import annotations

import logging
from typing import Any

from .scene_validator import evaluate_scene_metrics, validate_model_file, validate_prefab_on_disk

logger = logging.getLogger(__name__)


async def run_unified_audit(
    *,
    platforms: Any,
    vrchat_sdk: Any,
    project_path: str | None = None,
    avatar_prefab: str | None = None,
    model_path: str | None = None,
    scene_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run cross-platform validation summary for agent preflight."""
    audits: dict[str, Any] = {}
    blocking: list[str] = []
    warnings: list[str] = []

    if project_path:
        try:
            sdk = await vrchat_sdk.check_sdk_installed(project_path)
            audits["vrchat_sdk"] = sdk
            if not sdk.get("installed"):
                warnings.append("VRChat SDK not installed in project")
        except Exception as exc:
            audits["vrchat_sdk"] = {"success": False, "error": str(exc)}

        try:
            cck = await platforms.chillout.check_cck_installed(project_path)
            audits["chilloutvr_cck"] = cck
        except Exception as exc:
            audits["chilloutvr_cck"] = {"success": False, "error": str(exc)}

        try:
            cluster = await platforms.cluster.check_cluster_kit_installed(project_path)
            audits["cluster_kit"] = cluster
        except Exception as exc:
            audits["cluster_kit"] = {"success": False, "error": str(exc)}

    if avatar_prefab and project_path:
        try:
            prefab_disk = validate_prefab_on_disk(project_path, avatar_prefab)
            audits["prefab_disk"] = prefab_disk
            if prefab_disk.get("errors"):
                blocking.extend(prefab_disk["errors"])
            if prefab_disk.get("warnings"):
                warnings.extend(prefab_disk["warnings"])
        except Exception as exc:
            audits["prefab_disk"] = {"success": False, "error": str(exc)}

        try:
            vrchat_val = await vrchat_sdk.validate_avatar(avatar_prefab, project_path)
            audits["vrchat_avatar"] = vrchat_val
            if not vrchat_val.get("valid", True):
                blocking.extend(vrchat_val.get("errors", []))
            warnings.extend(vrchat_val.get("warnings", []))
        except Exception as exc:
            audits["vrchat_avatar"] = {"valid": False, "errors": [str(exc)]}

        try:
            cvr_val = await platforms.chillout.validate_for_chillout(avatar_prefab, project_path)
            audits["chilloutvr"] = cvr_val
        except Exception as exc:
            audits["chilloutvr"] = {"success": False, "error": str(exc)}

    if model_path:
        try:
            resonite = await platforms.resonite.check_resonite_compatibility(model_path)
            audits["resonite"] = resonite
            if not resonite.get("compatible", True):
                blocking.append(f"Resonite incompatible model: {model_path}")
            warnings.extend(resonite.get("recommendations", []))
        except Exception as exc:
            audits["resonite"] = {"success": False, "error": str(exc)}

        audits["model_file"] = validate_model_file(model_path, target_platform="resonite")

    platform_scores: dict[str, Any] = {}
    if scene_metrics:
        for platform in ("vrchat", "chilloutvr", "resonite", "cluster"):
            platform_scores[platform] = evaluate_scene_metrics(scene_metrics, target_platform=platform)

    valid = len(blocking) == 0
    return {
        "success": True,
        "valid": valid,
        "blocking_errors": blocking,
        "warnings": warnings,
        "audits": audits,
        "platform_scores": platform_scores,
        "hint": "Install SDKs and run bridge validate_scene for live Editor metrics.",
    }
