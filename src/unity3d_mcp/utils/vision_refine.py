"""Agent vision refinement loop for Unity Editor bridge sessions."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from unity3d_mcp.tools.portmanteau.unity_api_bridge import UnityBridgeClient
from unity3d_mcp.utils.unity_runtime import bridge_available, execute_bridge_action, get_bridge_client

logger = logging.getLogger(__name__)


async def capture_viewport(
    *,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    include_base64: bool = False,
    bridge: UnityBridgeClient | None = None,
) -> dict[str, Any]:
    """Single game view capture for vision models."""
    import base64

    client = bridge or get_bridge_client()
    result = await execute_bridge_action(
        "capture_game_view",
        bridge=client,
        output_path=output_path,
        width=width,
        height=height,
    )
    if not result.get("success"):
        return result

    path = Path(output_path)
    payload: dict[str, Any] = {
        "success": True,
        "output_path": str(path),
        "bridge_result": result.get("result"),
    }
    if include_base64 and path.is_file():
        try:
            payload["image_base64"] = base64.b64encode(path.read_bytes()).decode("ascii")
            payload["mime_type"] = "image/png"
        except OSError as exc:
            payload["base64_error"] = str(exc)
    return payload


async def capture_multi_angle(
    *,
    output_dir: str,
    angles: int = 4,
    width: int = 1280,
    height: int = 720,
    bridge: UnityBridgeClient | None = None,
) -> dict[str, Any]:
    """Capture multiple camera angles via bridge."""
    out = Path(output_dir)
    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"success": False, "error": f"Cannot create output_dir: {exc}"}

    client = bridge or get_bridge_client()
    result = await execute_bridge_action(
        "capture_multi_angle",
        bridge=client,
        output_dir=str(out),
        angles=angles,
        width=width,
        height=height,
    )
    if not result.get("success"):
        return result
    return {
        "success": True,
        "output_dir": str(out),
        "angles": angles,
        "bridge_result": result.get("result"),
    }


async def get_scene_summary(bridge: UnityBridgeClient | None = None) -> dict[str, Any]:
    """Fetch live scene summary from Unity bridge."""
    client = bridge or get_bridge_client()
    result = await execute_bridge_action("get_scene_summary", bridge=client)
    if not result.get("success"):
        return {"object_count": 0, "objects": [], "error": result.get("error")}
    summary = result.get("result") or {}
    if isinstance(summary, dict):
        return summary
    return {"raw": summary}


def build_refinement_prompt(goal: str, scene_summary: dict[str, Any]) -> str:
    """Build dialogic prompt for vision model review."""
    goal_line = goal.strip() or "Improve the Unity scene toward the user's stated goal."
    objects = scene_summary.get("objects") or []
    names = ", ".join(str(o.get("name", "?")) for o in objects[:8]) or "(none)"
    scene_name = scene_summary.get("scene_name") or scene_summary.get("scene") or "ActiveScene"
    count = scene_summary.get("object_count", len(objects))
    return (
        f"Goal: {goal_line}\n"
        f"Unity scene '{scene_name}' has {count} object(s). Sample: {names}.\n"
        "Inspect attached viewport/multi-angle images. List concrete fixes "
        "(scale, materials, lighting, colliders, prefab organization). "
        "Re-export from blender-mcp if mesh changes are needed, then call "
        "unity_import operation=import_blender. For in-editor tweaks use "
        "unity_vision_refine operation=apply_bridge_commands with JSON command list."
    )


async def build_review_bundle(
    *,
    output_dir: str,
    goal: str = "",
    include_multi_angle: bool = True,
    angles: int = 4,
    width: int = 1280,
    height: int = 720,
    bridge: UnityBridgeClient | None = None,
) -> dict[str, Any]:
    """Build agent review package: screenshot, angles, scene summary, prompt."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    screenshot = await capture_viewport(
        output_path=str(out / "review_viewport.png"),
        width=width,
        height=height,
        include_base64=True,
        bridge=bridge,
    )

    multi: dict[str, Any] | None = None
    if include_multi_angle:
        multi = await capture_multi_angle(
            output_dir=str(out / "angles"),
            angles=angles,
            width=width,
            height=height,
            bridge=bridge,
        )

    scene_summary = await get_scene_summary(bridge=bridge)
    refinement_prompt = build_refinement_prompt(goal, scene_summary)

    manifest_path = out / "review_manifest.json"
    manifest = {
        "goal": goal,
        "scene_summary": scene_summary,
        "refinement_prompt": refinement_prompt,
        "screenshot_path": str(out / "review_viewport.png"),
        "angles_dir": str(out / "angles") if include_multi_angle else None,
    }
    try:
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    except OSError as exc:
        logger.warning("Failed to write review manifest: %s", exc)

    return {
        "success": screenshot.get("success", False),
        "screenshot": screenshot,
        "multi_angle": multi,
        "scene_summary": scene_summary,
        "refinement_prompt": refinement_prompt,
        "manifest_path": str(manifest_path),
        "message": (
            "Review bundle ready. Send viewport PNG (and angles/) to your vision model, "
            "then apply fixes via unity_import or unity_vision_refine apply_bridge_commands."
        ),
    }


async def apply_bridge_commands(
    commands: list[dict[str, Any]],
    *,
    bridge: UnityBridgeClient | None = None,
) -> dict[str, Any]:
    """Apply a list of bridge actions after vision review."""
    if not commands:
        return {"success": False, "error": "commands list is empty"}

    client = bridge or get_bridge_client()
    if not await bridge_available(client):
        return {"success": False, "error": "Unity Editor bridge not connected"}

    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, cmd in enumerate(commands):
        action = cmd.get("action") or cmd.get("operation")
        if not action:
            errors.append(f"command[{index}]: missing action")
            continue
        target = cmd.get("target")
        kwargs = {k: v for k, v in cmd.items() if k not in ("action", "operation", "target")}
        result = await execute_bridge_action(action, bridge=client, target=target, **kwargs)
        results.append({"index": index, "action": action, "result": result})
        if not result.get("success"):
            errors.append(f"command[{index}] {action}: {result.get('error', 'failed')}")

    return {
        "success": not errors,
        "applied": len(results),
        "results": results,
        "errors": errors,
    }
