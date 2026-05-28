"""FastAPI REST API + FastMCP mount for unity3d-mcp.

Fleet mesh: import/export models from gazebo, freecad, resonite, blender,
worldlabs. MCP tools at /mcp. Health at /api/v1/health.

Start: uvicorn unity3d_mcp.app:app --host 127.0.0.1 --port 10831
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from unity3d_mcp import __version__
from unity3d_mcp.server import server_instance
from unity3d_mcp.utils.logging_setup import setup_logging
from unity3d_mcp.utils.telemetry import (
    init_metrics,
    install_tool_call_wrapper,
    metrics_content_type,
    render_metrics,
    start_metrics_server,
)

setup_logging()
init_metrics()
install_tool_call_wrapper(server_instance.app)
if os.getenv("UNITY3D_MCP_START_METRICS_SERVER", "true").strip().lower() not in {"0", "false", "no", "off"}:
    start_metrics_server()

log = logging.getLogger(__name__)

mcp_http = server_instance.app.http_app(path="/mcp")
router = APIRouter(prefix="/api/v1")
si = server_instance


# ── Request models ────────────────────────────────────────────────────────


class ModelImportReq(BaseModel):
    models: list[str] = Field(..., min_length=1, description="Model names.")
    file_path: str | None = Field(None, description="Path template e.g. imports/{model}.fbx")
    format: str | None = None


class ModelExportReq(BaseModel):
    name: str = Field(..., description="Object name to export.")
    output_path: str | None = Field(None, description="Output path. Default: exports/{name}.fbx")


# ── Import helper ─────────────────────────────────────────────────────────


def _import(body: ModelImportReq, source: str) -> dict[str, Any]:
    results = {}
    for model in body.models:
        fpath = (body.file_path or f"{source}_models/{model}.fbx").format(model=model)
        if not Path(fpath).is_file():
            for ext in [".fbx", ".obj", ".gltf", ".glb", ".stl", ".step", ".vrm"]:
                test = Path(fpath).with_suffix(ext)
                if test.is_file():
                    fpath = str(test)
                    break
        try:
            r = si.import_export_manager.import_3d_model(
                model_path=fpath,
                import_settings={"importMaterials": True, "importTextures": True},
            )
            results[model] = "imported" if r.get("success") else f"not found: {fpath}"
        except Exception as e:
            results[model] = str(e)
    return {"success": True, "models": results, "count": len(body.models)}


# ── Import endpoints (fleet mesh bridges) ─────────────────────────────────


@router.post("/gazebo/import")
async def gazebo_import(body: ModelImportReq) -> dict[str, Any]:
    return _import(body, "gazebo")


@router.post("/freecad/import")
async def freecad_import(body: ModelImportReq) -> dict[str, Any]:
    return _import(body, "freecad")


@router.post("/resonite/import")
async def resonite_import(body: ModelImportReq) -> dict[str, Any]:
    return _import(body, "resonite")


@router.post("/blender/import")
async def blender_import(body: ModelImportReq) -> dict[str, Any]:
    return _import(body, "blender")


@router.post("/worldlabs/import")
async def worldlabs_import(body: ModelImportReq) -> dict[str, Any]:
    return _import(body, "worldlabs")


@router.post("/import/model")
async def import_model(body: ModelImportReq) -> dict[str, Any]:
    return _import(body, "generic")


# ── Export endpoints ──────────────────────────────────────────────────────


@router.post("/export/fbx")
async def export_fbx(body: ModelExportReq) -> dict[str, Any]:
    try:
        out = body.output_path or f"exports/{body.name}.fbx"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        r = await si.import_export_manager.export_fbx(
            object_names=body.name, output_path=out
        )
        return {"success": True, "exported": body.name, "path": out, **r}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/export/gltf")
async def export_gltf(body: ModelExportReq) -> dict[str, Any]:
    """Export a Unity object to glTF format. Web-native, PBR-ready, compact."""
    try:
        out = body.output_path or f"exports/{body.name}.glb"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        r = await si.import_export_manager.export_gltf(
            object_names=body.name, output_path=out
        )
        return {"success": True, "exported": body.name, "path": out, **r}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Health ────────────────────────────────────────────────────────────────


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "unity3d-mcp", "version": __version__}


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    return Response(content=render_metrics(), media_type=metrics_content_type())


class ToolCallReq(BaseModel):
    tool: str
    params: dict[str, Any] = Field(default_factory=dict)


@router.post("/tool")
async def mcp_tool_bridge(body: ToolCallReq) -> JSONResponse:
    """Bridge endpoint for webapp Agent Tools to call MCP tools."""
    if not body.tool:
        return JSONResponse({"success": False, "error": "Missing tool name"}, status_code=400)
    try:
        result = await si.app.call_tool(body.tool, body.params)
    except Exception as exc:
        log.exception("Tool %s failed: %s", body.tool, exc)
        return JSONResponse({"success": False, "error": str(exc), "data": None}, status_code=500)

    mcp_result = result.to_mcp_result()
    is_error = False
    content_list: list[Any] = []
    if isinstance(mcp_result, tuple) and len(mcp_result) >= 2:
        content_list = mcp_result[0]
        is_error = mcp_result[1]
    else:
        content_list = getattr(result, "content", [])

    data: Any = None
    if content_list:
        text = getattr(content_list[0], "text", str(content_list[0]))
        try:
            data = json.loads(text)
        except Exception:
            data = {"output": text}

    return JSONResponse(
        {
            "success": not is_error and data is not None,
            "data": data,
            "error": None if not is_error else "Tool returned error",
        }
    )


# ── Build app ─────────────────────────────────────────────────────────────


def build_app() -> FastAPI:
    app = FastAPI(title="unity3d-mcp", version=__version__, lifespan=mcp_http.lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.include_router(router)
    app.mount("/mcp", mcp_http)
    return app


app = build_app()
