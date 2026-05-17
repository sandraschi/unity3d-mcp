"""FastAPI REST API + FastMCP mount for unity3d-mcp.

Provides REST endpoints for fleet mesh integration (gazebo-mcp bridge,
health checks) alongside the full MCP tool surface at /mcp.

Start with: uvicorn unity3d_mcp.app:app --host 127.0.0.1 --port 10831
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, Field

from unity3d_mcp.config import Unity3DConfig

log = logging.getLogger(__name__)

# Import the server instance (FastMCP ASGI app)
from unity3d_mcp.server import server_instance

mcp_http = server_instance.app.http_app(path="/mcp")
router = APIRouter(prefix="/api/v1")


# ── Fleet mesh bridge: gazebo-mcp → unity3d-mcp ──────────────────────────


class GazeboImportRequest(BaseModel):
    models: list[str] = Field(..., min_length=1, description="Gazebo model names to import into Unity.")


@router.post("/gazebo/import")
async def gazebo_import(body: GazeboImportRequest) -> dict[str, Any]:
    """Receive Gazebo simulation models for Unity 3D visualization.

    Called by gazebo-mcp's sync_to_unity() tool.
    Imports the listed models into the Unity scene for rendering.
    """
    from unity3d_mcp.server import server_instance as si

    results = {}
    for model in body.models:
        try:
            # Use the existing 3D model import tool
            si.import_export_manager.import_3d_model(
                model_name=model,
                file_path=f"gazebo_models/{model}.fbx",
                import_settings={"importMaterials": True, "importTextures": True},
            )
            results[model] = "imported"
        except Exception as e:
            results[model] = f"failed: {e}"
            log.warning("Gazebo import failed for %s: %s", model, e)

    return {"success": True, "models": results, "count": len(body.models)}


@router.get("/gazebo/import")
async def gazebo_import_get(q: str | None = None) -> dict[str, Any]:
    """GET version — list recently imported Gazebo models."""
    # Unity doesn't persist an import log yet, so return empty
    return {"success": True, "models": [], "count": 0}


# ── Health ────────────────────────────────────────────────────────────────


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "unity3d-mcp", "version": "1.0.0"}


# ── Build the FastAPI app ─────────────────────────────────────────────────


def build_app() -> FastAPI:
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="unity3d-mcp", version="1.0.0", lifespan=mcp_http.lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.include_router(router)
    app.mount("/mcp", mcp_http)

    @app.get("/health")
    async def root_health() -> dict[str, str]:
        return {"status": "ok", "service": "unity3d-mcp"}

    return app


app = build_app()
