#!/usr/bin/env python3
"""HTTP server for Unity3D MCP - FastAPI interface for web-based control."""

import logging
import os
import subprocess
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Unity3D MCP Server",
    description="HTTP API for Unity 3D Editor automation and VRChat integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests
class FleetLaunchRequest(BaseModel):
    """Request model for launching a fleet application."""

    repo_path: str = Field(..., description="Absolute path to the repository root")


class FleetLaunchResponse(BaseModel):
    """Response model for fleet launch operation."""

    success: bool
    message: str


# API Routes
@app.get("/api/v1/health")
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "server": "unity3d-mcp-sota",
        "version": "2026.2.17",
        "capabilities": [
            "unity_editor_automation",
            "vrm_avatar_pipeline",
            "vrchat_sdk_integration",
            "worldlabs_import",
            "fleet_orchestration",
        ],
    }


@app.post("/api/v1/fleet/launch", response_model=FleetLaunchResponse)
async def launch_app(request: FleetLaunchRequest) -> FleetLaunchResponse:
    """Launch another MCP app via its start.ps1 script."""
    path = Path(request.repo_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Path {request.repo_path} does not exist")

    # Security check: Ensure path is within D:/Dev/repos
    try:
        allowed_base = Path("D:/Dev/repos").resolve()
        target_path = path.resolve()
        target_path.relative_to(allowed_base)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Access denied: Path outside allowed directory") from exc

    start_script = path / "web_sota" / "start.ps1"
    if not start_script.exists():
        start_script = path / "web" / "start.ps1"
        if not start_script.exists():
            start_script = path / "start.ps1"
            if not start_script.exists():
                raise HTTPException(status_code=400, detail="No valid SOTA entry point found")

    try:
        powershell = str(
            Path(os.environ.get("SystemRoot", "C:\\Windows"))
            / "System32"
            / "WindowsPowerShell"
            / "v1.0"
            / "powershell.exe"
        )
        subprocess.Popen(
            [powershell, "-ExecutionPolicy", "Bypass", "-File", str(start_script)],
            cwd=str(path),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            shell=False,
        )
        return FleetLaunchResponse(success=True, message=f"Launched {path.name} successfully")
    except Exception as e:
        logger.error(f"Failed to launch {path.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/workflows")
async def list_workflows():
    """List all available Arazzo mission descriptors."""
    workflows_dir = Path(__file__).parent / "workflows"
    if not workflows_dir.exists():
        return {"status": "success", "workflows": []}

    found_workflows = []
    for yaml_file in workflows_dir.glob("*.yaml"):
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                found_workflows.append(
                    {
                        "id": yaml_file.stem,
                        "title": data.get("info", {}).get("title"),
                        "description": data.get("info", {}).get("description"),
                        "spec": data,
                    }
                )
        except Exception as e:
            logger.error(f"Error parsing workflow {yaml_file}: {e}")

    return {"status": "success", "count": len(found_workflows), "workflows": found_workflows}


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Unity3D MCP Server",
        "version": "1.0.0",
        "description": "HTTP API for Unity 3D Editor automation",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "fleet": "/api/v1/fleet/*",
        },
    }
