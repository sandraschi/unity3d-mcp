"""Scene and avatar validation portmanteau tool."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

from ...platforms import PlatformManager
from ...utils.platform_audit import run_unified_audit
from ...utils.scene_validator import (
    list_platform_limits,
    validate_model_file,
    validate_prefab_on_disk,
    validate_scene_via_bridge,
)
from ...vrchat import VRChatSDKManager
from .unity_api_bridge import UnityBridgeClient

logger = logging.getLogger(__name__)


class UnityValidationToolManager:
    """Portmanteau tool for scene/mesh validation and platform audits."""

    def __init__(
        self,
        app: FastMCP,
        bridge: UnityBridgeClient,
        vrchat_sdk: VRChatSDKManager,
        platforms: PlatformManager,
    ) -> None:
        self.app = app
        self.bridge = bridge
        self.vrchat_sdk = vrchat_sdk
        self.platforms = platforms

    def register_tools(self) -> None:
        @self.app.tool
        async def unity_validation(
            operation: str,
            target_platform: str = "vrchat",
            project_path: str | None = None,
            avatar_prefab: str | None = None,
            model_path: str | None = None,
            polycount_limit: int | None = None,
            material_limit: int | None = None,
        ) -> dict[str, Any]:
            """Validate Unity scenes, avatars, and fleet models for social VR platforms.

            Operations:
            - list_limits: platform polygon/material/bone limits
            - validate_scene: live Editor scene audit via bridge (polycount, materials, missing scripts)
            - check_polycount / check_materials / check_missing_scripts: focused scene checks
            - validate_model: disk check for GLB/VRM/FBX/OBJ/prefab path
            - validate_avatar: prefab + VRChat SDK validation
            - unified_audit: VRChat + CVR + Resonite + Cluster preflight bundle
            """
            try:
                if operation == "list_limits":
                    return list_platform_limits()

                if operation == "validate_scene":
                    report = await validate_scene_via_bridge(self.bridge, target_platform=target_platform)
                    if polycount_limit and report.get("metrics"):
                        polys = report["metrics"].get("polygons", 0)
                        if polys > polycount_limit:
                            report.setdefault("errors", []).append(
                                f"Custom polycount limit exceeded: {polys} > {polycount_limit}"
                            )
                            report["valid"] = False
                    if material_limit and report.get("metrics"):
                        mats = report["metrics"].get("materials", 0)
                        if mats > material_limit:
                            report.setdefault("errors", []).append(
                                f"Custom material limit exceeded: {mats} > {material_limit}"
                            )
                            report["valid"] = False
                    return report

                if operation in ("check_polycount", "check_materials", "check_missing_scripts"):
                    report = await validate_scene_via_bridge(self.bridge, target_platform=target_platform)
                    if not report.get("success"):
                        return report
                    metrics = report.get("metrics", {})
                    if operation == "check_polycount":
                        return {
                            "success": True,
                            "operation": operation,
                            "polygons": metrics.get("polygons", 0),
                            "limit": polycount_limit or report.get("limits", {}).get("polygons"),
                            "performance_rank": report.get("performance_rank"),
                            "valid": report.get("valid", False),
                        }
                    if operation == "check_materials":
                        return {
                            "success": True,
                            "operation": operation,
                            "materials": metrics.get("materials", 0),
                            "limit": material_limit or report.get("limits", {}).get("materials"),
                            "valid": metrics.get("materials", 0)
                            <= (material_limit or report.get("limits", {}).get("materials", 32)),
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "missing_scripts": metrics.get("missing_scripts", 0),
                        "objects_with_missing_scripts": report.get("objects_with_missing_scripts", []),
                        "valid": metrics.get("missing_scripts", 0) == 0,
                    }

                if operation == "validate_model":
                    if not model_path:
                        return {"success": False, "error": "model_path required for validate_model"}
                    return validate_model_file(model_path, target_platform=target_platform)

                if operation == "validate_avatar":
                    if not project_path or not avatar_prefab:
                        return {
                            "success": False,
                            "error": "project_path and avatar_prefab required for validate_avatar",
                        }
                    disk = validate_prefab_on_disk(project_path, avatar_prefab)
                    vrchat = await self.vrchat_sdk.validate_avatar(avatar_prefab, project_path)
                    valid = disk.get("valid", True) and vrchat.get("valid", False)
                    return {
                        "success": True,
                        "valid": valid,
                        "target_platform": target_platform,
                        "prefab_disk": disk,
                        "vrchat": vrchat,
                    }

                if operation == "unified_audit":
                    scene_metrics: dict[str, Any] | None = None
                    bridge_report = await validate_scene_via_bridge(self.bridge, target_platform=target_platform)
                    if bridge_report.get("success") and bridge_report.get("metrics"):
                        scene_metrics = {
                            "triangle_count": bridge_report["metrics"].get("polygons", 0),
                            "material_count": bridge_report["metrics"].get("materials", 0),
                            "missing_script_count": bridge_report["metrics"].get("missing_scripts", 0),
                            "mesh_count": bridge_report["metrics"].get("mesh_count", 0),
                            "object_count": bridge_report["metrics"].get("object_count", 0),
                            "objects_with_missing_scripts": bridge_report.get(
                                "objects_with_missing_scripts", []
                            ),
                        }
                    return await run_unified_audit(
                        platforms=self.platforms,
                        vrchat_sdk=self.vrchat_sdk,
                        project_path=project_path,
                        avatar_prefab=avatar_prefab,
                        model_path=model_path,
                        scene_metrics=scene_metrics,
                    )

                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "list_limits",
                        "validate_scene",
                        "check_polycount",
                        "check_materials",
                        "check_missing_scripts",
                        "validate_model",
                        "validate_avatar",
                        "unified_audit",
                    ],
                }
            except Exception as exc:
                logger.exception("unity_validation failed: %s", exc)
                return {"success": False, "error": str(exc), "operation": operation}
