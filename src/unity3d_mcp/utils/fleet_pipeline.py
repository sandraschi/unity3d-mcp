"""Fleet E2E pipeline: Gazebo + blender-mcp -> unity3d-mcp import -> validate -> build."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BLENDER_URL = "http://127.0.0.1:10849"
DEFAULT_UNITY_URL = "http://127.0.0.1:10831"
DEFAULT_GAZEBO_MCP_URL = "http://127.0.0.1:10991"
DEFAULT_EXPORT_DIR = Path("D:/Temp/fleet_pipeline/exports")
DEFAULT_BUILD_DIR = Path("D:/Temp/fleet_pipeline/builds")
DEFAULT_GAZEBO_FILE_TEMPLATE = "gazebo_models/{model}.fbx"


@dataclass
class PipelineStep:
    name: str
    success: bool
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineReport:
    success: bool
    steps: list[PipelineStep] = field(default_factory=list)
    model_path: str | None = None
    project_path: str | None = None
    build_output_path: str | None = None
    execution_mode: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "model_path": self.model_path,
            "project_path": self.project_path,
            "build_output_path": self.build_output_path,
            "execution_mode": self.execution_mode,
            "steps": [
                {"name": s.name, "success": s.success, "detail": s.detail} for s in self.steps
            ],
        }


def parse_tool_payload(result: Any) -> dict[str, Any]:
    """Normalize FastMCP call_tool or HTTP /tool JSON into a dict."""
    if isinstance(result, dict):
        if "data" in result and isinstance(result["data"], dict):
            return result["data"]
        return result
    content = getattr(result, "content", None)
    if content:
        text = getattr(content[0], "text", str(content[0]))
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"output": text}
    return {"raw": str(result)}


async def call_http_tool(
    base_url: str,
    tool: str,
    params: dict[str, Any],
    *,
    timeout: float = 300.0,
) -> dict[str, Any]:
    """Call blender-mcp (or any fleet) POST /tool endpoint."""
    url = base_url.rstrip("/") + "/tool"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json={"tool": tool, "params": params})
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.exception("HTTP tool call failed tool=%s url=%s", tool, url)
        return {"success": False, "error": str(exc), "tool": tool}

    if isinstance(body, dict) and body.get("data") is not None:
        data = body["data"]
        if isinstance(data, dict):
            if body.get("success") is False and "success" not in data:
                data = {**data, "success": False}
            elif "success" not in data:
                data = {**data, "success": bool(body.get("success", True))}
            return data
    return body if isinstance(body, dict) else {"success": False, "error": "Invalid tool response"}


async def check_http_health(base_url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(base_url.rstrip("/") + "/api/v1/health")
            return response.status_code == 200
    except httpx.HTTPError:
        return False


async def import_gazebo_via_unity(
    *,
    unity_url: str,
    models: list[str],
    file_path_template: str | None = None,
) -> dict[str, Any]:
    """Import Gazebo/sim meshes into Unity via unity3d-mcp REST bridge."""
    if not models:
        return {"success": False, "error": "gazebo_models list is empty"}

    url = unity_url.rstrip("/") + "/api/v1/gazebo/import"
    payload: dict[str, Any] = {"models": models}
    if file_path_template:
        payload["file_path"] = file_path_template

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Gazebo import via Unity failed")
        return {"success": False, "error": str(exc), "unity_url": unity_url}

    if not isinstance(body, dict):
        return {"success": False, "error": "Invalid gazebo import response"}

    models_map = body.get("models", {})
    failed = [name for name, status in models_map.items() if "not found" in str(status).lower() or "error" in str(status).lower()]
    success = body.get("success", True) and not failed
    return {
        "success": success,
        "models": models_map,
        "count": body.get("count", len(models)),
        "file_path_template": file_path_template,
        "partial_errors": failed,
        "hint": "Export FBX/OBJ from Gazebo or gazebo-mcp into gazebo_models/ before import",
    }


async def export_from_gazebo_mcp(
    *,
    gazebo_url: str,
    model_name: str,
    output_path: Path,
) -> dict[str, Any]:
    """Optional pre-step: ask gazebo-mcp to export a sim model (when server exposes export tool)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not await check_http_health(gazebo_url):
        return {
            "success": False,
            "error": f"gazebo-mcp not reachable at {gazebo_url}",
            "hint": "Place exported meshes on disk and use --gazebo-models with --gazebo-file-template",
        }

    for tool_name, params in (
        ("gazebo_export", {"operation": "export_model", "model_name": model_name, "output_path": str(output_path)}),
        ("gazebo_models", {"operation": "export_fbx", "model": model_name, "output_path": str(output_path)}),
    ):
        result = await call_http_tool(gazebo_url, tool_name, params, timeout=300.0)
        if result.get("success") and output_path.is_file():
            return {"success": True, "output_path": str(output_path), "tool": tool_name, "detail": result}
    return {
        "success": False,
        "error": "gazebo-mcp export tool did not produce a file",
        "gazebo_url": gazebo_url,
    }


async def export_from_blender(
    *,
    blender_url: str,
    output_path: Path,
    operation: str = "export_glb",
    object_names: list[str] | None = None,
) -> dict[str, Any]:
    """Export via blender-mcp HTTP tool (requires Blender session + backend)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    params: dict[str, Any] = {
        "operation": operation,
        "output_path": str(output_path),
    }
    if object_names:
        params["object_names"] = object_names

    result = await call_http_tool(blender_url, "blender_export", params)
    if result.get("success") is False and not output_path.is_file():
        return result
    if output_path.is_file():
        return {
            "success": True,
            "output_path": str(output_path),
            "operation": operation,
            "blender_response": result,
        }
    return {
        "success": False,
        "error": result.get("error") or "Export did not produce output file",
        "blender_response": result,
    }


async def wait_for_job(job_id: str, *, timeout: float = 3600.0, poll_interval: float = 2.0) -> dict[str, Any]:
    from unity3d_mcp.utils.job_queue import JobStatus, get_job, job_to_dict

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = get_job(job_id)
        if job is None:
            return {"success": False, "error": f"Unknown job_id: {job_id}"}
        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            data = job_to_dict(job)
            data["success"] = job.status == JobStatus.COMPLETED
            return data
        await asyncio.sleep(poll_interval)
    return {"success": False, "error": f"Job {job_id} timed out after {timeout}s"}


async def run_fleet_pipeline(
    *,
    project_path: str,
    model_path: str | None = None,
    blender_url: str = DEFAULT_BLENDER_URL,
    unity_url: str = DEFAULT_UNITY_URL,
    gazebo_mcp_url: str = DEFAULT_GAZEBO_MCP_URL,
    gazebo_models: list[str] | None = None,
    gazebo_file_template: str = DEFAULT_GAZEBO_FILE_TEMPLATE,
    skip_gazebo: bool = True,
    try_gazebo_mcp_export: bool = False,
    export_operation: str = "export_glb",
    export_dir: Path | None = None,
    object_names: list[str] | None = None,
    skip_export: bool = False,
    skip_validate: bool = False,
    skip_build: bool = False,
    target_platform: str = "vrchat",
    build_target: str = "StandaloneWindows64",
    build_output_dir: Path | None = None,
    build_timeout: float = 3600.0,
    avatar_prefab: str | None = None,
) -> PipelineReport:
    """Run gazebo import (optional) -> blender export (optional) -> unity import -> validate -> build."""
    from unity3d_mcp.server import server_instance
    from unity3d_mcp.utils.execution_mode import describe_execution_mode
    from unity3d_mcp.utils.fleet_import import import_blender_asset
    from unity3d_mcp.utils.job_queue import submit_unity_job

    report = PipelineReport(success=False, project_path=project_path)
    project = Path(project_path)
    if not project.is_dir():
        report.steps.append(
            PipelineStep("precheck", False, {"error": f"Unity project not found: {project_path}"})
        )
        return report

    mode = await describe_execution_mode()
    report.execution_mode = str(mode.get("mode"))

    if not skip_gazebo and gazebo_models:
        export_root = export_dir or DEFAULT_EXPORT_DIR
        if try_gazebo_mcp_export:
            for model in gazebo_models:
                out = export_root / f"{model}.fbx"
                export_result = await export_from_gazebo_mcp(
                    gazebo_url=gazebo_mcp_url,
                    model_name=model,
                    output_path=out,
                )
                report.steps.append(
                    PipelineStep(
                        f"gazebo_mcp_export_{model}",
                        bool(export_result.get("success")),
                        export_result,
                    )
                )

        gazebo_result = await import_gazebo_via_unity(
            unity_url=unity_url,
            models=gazebo_models,
            file_path_template=gazebo_file_template,
        )
        gazebo_ok = bool(gazebo_result.get("success")) or bool(gazebo_result.get("models"))
        report.steps.append(PipelineStep("gazebo_import", gazebo_ok, gazebo_result))
        if not gazebo_ok and not model_path and skip_export:
            return report

    resolved_model: Path | None = Path(model_path) if model_path else None
    wants_blender_handoff = bool(resolved_model) or not skip_export

    if not wants_blender_handoff:
        if skip_validate and skip_build:
            report.success = all(s.success for s in report.steps)
            return report
    elif not skip_export and resolved_model is None:
        export_root = export_dir or DEFAULT_EXPORT_DIR
        export_root.mkdir(parents=True, exist_ok=True)
        export_file = export_root / f"fleet_handoff.{export_operation.replace('export_', '')}"
        if export_file.suffix.lower() not in {".glb", ".gltf", ".fbx", ".vrm", ".obj"}:
            export_file = export_file.with_suffix(".glb")

        if not await check_http_health(blender_url):
            report.steps.append(
                PipelineStep(
                    "blender_export",
                    False,
                    {
                        "error": f"Blender MCP not reachable at {blender_url}",
                        "hint": "Start blender-mcp HTTP backend or pass --model-path",
                    },
                )
            )
            return report

        export_result = await export_from_blender(
            blender_url=blender_url,
            output_path=export_file,
            operation=export_operation,
            object_names=object_names,
        )
        report.steps.append(PipelineStep("blender_export", bool(export_result.get("success")), export_result))
        if not export_result.get("success"):
            return report
        resolved_model = Path(str(export_result["output_path"]))

    if wants_blender_handoff:
        if resolved_model is None or not resolved_model.is_file():
            report.steps.append(
                PipelineStep(
                    "precheck",
                    False,
                    {"error": "No blender model file: provide --model-path or enable blender export"},
                )
            )
            return report

        report.model_path = str(resolved_model)

        import_result = await import_blender_asset(
            server_instance.import_export_manager,
            file_path=str(resolved_model),
            project_path=project_path,
        )
        report.steps.append(PipelineStep("unity_import", bool(import_result.get("success")), import_result))
        if not import_result.get("success"):
            return report
    elif not skip_gazebo and gazebo_models:
        report.model_path = None
    else:
        report.steps.append(
            PipelineStep(
                "precheck",
                False,
                {"error": "Enable --gazebo-models and/or blender handoff (--model-path or export)"},
            )
        )
        return report

    if not skip_validate:
        app = server_instance.app
        validate_model_path = str(resolved_model) if resolved_model else None
        if validate_model_path:
            model_val = parse_tool_payload(
                await app.call_tool(
                    "unity_validation",
                    {
                        "operation": "validate_model",
                        "model_path": validate_model_path,
                        "target_platform": target_platform,
                    },
                )
            )
            report.steps.append(
                PipelineStep("validate_model", bool(model_val.get("valid", model_val.get("success"))), model_val)
            )
            if not model_val.get("valid", model_val.get("success")):
                return report

        scene_val = parse_tool_payload(
            await app.call_tool(
                "unity_validation",
                {"operation": "validate_scene", "target_platform": target_platform},
            )
        )
        if scene_val.get("mode") == "bridge" and scene_val.get("success"):
            scene_ok = bool(scene_val.get("valid"))
        else:
            scene_ok = True
            if not scene_val.get("success"):
                scene_val["skipped"] = "Live scene validation requires Hands-In bridge"
        report.steps.append(PipelineStep("validate_scene", scene_ok, scene_val))

        audit_params: dict[str, Any] = {
            "operation": "unified_audit",
            "project_path": project_path,
            "model_path": str(resolved_model),
            "target_platform": target_platform,
        }
        if avatar_prefab:
            audit_params["avatar_prefab"] = avatar_prefab
        if validate_model_path:
            audit_params["model_path"] = validate_model_path
        audit = parse_tool_payload(await app.call_tool("unity_validation", audit_params))
        report.steps.append(
            PipelineStep("unified_audit", bool(audit.get("valid", audit.get("success"))), audit)
        )

    if skip_build:
        report.success = all(s.success for s in report.steps)
        return report

    build_dir = build_output_dir or DEFAULT_BUILD_DIR
    build_dir.mkdir(parents=True, exist_ok=True)
    job_id = await submit_unity_job(
        "build",
        name="fleet_pipeline_build",
        params={
            "project_path": project_path,
            "build_target": build_target,
            "output_path": str(build_dir),
            "development_build": True,
        },
    )
    report.steps.append(
        PipelineStep("unity_jobs_submit", True, {"job_id": job_id, "build_target": build_target})
    )

    job_result = await wait_for_job(job_id, timeout=build_timeout)
    report.steps.append(PipelineStep("unity_build", bool(job_result.get("success")), job_result))
    if job_result.get("success"):
        report.build_output_path = str(build_dir)

    report.success = all(s.success for s in report.steps)
    return report
