"""Unity async job queue portmanteau tool."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...utils.job_queue import cancel_job, get_job, job_to_dict, list_jobs, submit_unity_job

logger = logging.getLogger(__name__)


class UnityJobsToolManager:
    """Portmanteau tool for async Unity build, import, and simulation jobs."""

    def __init__(self, app: FastMCP) -> None:
        self.app = app

    def register_tools(self) -> None:
        @self.app.tool
        async def unity_jobs(
            operation: str = "status",
            job_id: str = "",
            job_type: str = "build",
            name: str = "unity_job",
            project_path: Optional[str] = None,
            build_target: str = "StandaloneWindows64",
            output_path: Optional[str] = None,
            development_build: bool = False,
            input_dir: Optional[str] = None,
            pattern: str = "*.glb",
            duration: float = 1.0,
            record_data: bool = False,
            timeout: float = 120.0,
            limit: int = 20,
        ) -> Dict[str, Any]:
            """Async job queue for builds, batch imports, and play-mode simulation.

            Operations:
            - submit: queue job (job_type: build | batch_import | simulation)
            - status: poll job by job_id
            - list: recent jobs
            - cancel: cancel pending/running job
            """
            try:
                if operation == "submit":
                    params: dict[str, Any] = {}
                    if job_type == "build":
                        if not project_path or not output_path:
                            return {
                                "success": False,
                                "error": "project_path and output_path required for build jobs",
                            }
                        params = {
                            "project_path": project_path,
                            "build_target": build_target,
                            "output_path": output_path,
                            "development_build": development_build,
                        }
                    elif job_type == "batch_import":
                        if not input_dir:
                            return {"success": False, "error": "input_dir required for batch_import jobs"}
                        params = {
                            "input_dir": input_dir,
                            "pattern": pattern,
                            "project_path": project_path,
                        }
                    elif job_type == "simulation":
                        params = {
                            "duration": duration,
                            "record_data": record_data,
                            "timeout": timeout,
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Unknown job_type: {job_type}",
                            "available_job_types": ["build", "batch_import", "simulation"],
                        }

                    new_id = await submit_unity_job(job_type, name=name, params=params)
                    return {"success": True, "job_id": new_id, "job_type": job_type, "status": "pending"}

                if operation == "status":
                    if not job_id:
                        return {"success": False, "error": "job_id required for status"}
                    job = get_job(job_id)
                    if not job:
                        return {"success": False, "error": f"Unknown job_id: {job_id}"}
                    data = job_to_dict(job)
                    data["success"] = job.status.value in ("completed", "running", "pending")
                    return data

                if operation == "list":
                    return {"success": True, "jobs": list_jobs(limit=limit)}

                if operation == "cancel":
                    if not job_id:
                        return {"success": False, "error": "job_id required for cancel"}
                    ok = await cancel_job(job_id)
                    return {"success": ok, "job_id": job_id, "cancelled": ok}

                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["submit", "status", "list", "cancel"],
                }
            except Exception as exc:
                logger.exception("unity_jobs failed: %s", exc)
                return {"success": False, "error": str(exc), "operation": operation}
