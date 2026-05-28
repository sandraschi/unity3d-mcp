"""In-process async job queue for long-running Unity operations."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class UnityJob:
    id: str
    job_type: str
    name: str
    status: JobStatus = JobStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    params: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    mode: str | None = None
    _task: asyncio.Task | None = field(default=None, repr=False)


_jobs: dict[str, UnityJob] = {}
_build_runner: Callable[..., Awaitable[dict[str, Any]]] | None = None
_import_runner: Callable[..., Awaitable[dict[str, Any]]] | None = None
_simulation_runner: Callable[..., Awaitable[dict[str, Any]]] | None = None


def configure_job_runners(
    *,
    build_runner: Callable[..., Awaitable[dict[str, Any]]] | None = None,
    import_runner: Callable[..., Awaitable[dict[str, Any]]] | None = None,
    simulation_runner: Callable[..., Awaitable[dict[str, Any]]] | None = None,
) -> None:
    """Inject managers for job execution (called from server init)."""
    global _build_runner, _import_runner, _simulation_runner
    if build_runner is not None:
        _build_runner = build_runner
    if import_runner is not None:
        _import_runner = import_runner
    if simulation_runner is not None:
        _simulation_runner = simulation_runner


def _prune_old_jobs(max_jobs: int = 100) -> None:
    if len(_jobs) <= max_jobs:
        return
    finished = sorted(
        (
            (jid, job)
            for jid, job in _jobs.items()
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
        ),
        key=lambda item: item[1].finished_at or 0,
    )
    for jid, _ in finished[: len(_jobs) - max_jobs]:
        _jobs.pop(jid, None)


def _update_jobs_gauge() -> None:
    try:
        from unity3d_mcp.utils.telemetry import set_jobs_active

        active = sum(1 for job in _jobs.values() if job.status in (JobStatus.PENDING, JobStatus.RUNNING))
        set_jobs_active(active)
    except Exception:
        pass


async def _run_build_job(job: UnityJob) -> None:
    if _build_runner is None:
        raise RuntimeError("Build job runner not configured")
    params = job.params
    result = await _build_runner(
        project_path=params.get("project_path", ""),
        build_target=params.get("build_target", "StandaloneWindows64"),
        output_path=params.get("output_path", ""),
        development_build=bool(params.get("development_build", False)),
    )
    job.output = result if isinstance(result, dict) else {"result": result}
    if not job.output.get("success", job.output.get("status") == "success"):
        job.error = job.output.get("error") or job.output.get("message") or "Build failed"


async def _run_batch_import_job(job: UnityJob) -> None:
    if _import_runner is None:
        raise RuntimeError("Import job runner not configured")
    params = job.params
    input_dir = Path(str(params.get("input_dir", "")))
    pattern = str(params.get("pattern", "*.glb"))
    project_path = params.get("project_path")
    if not input_dir.is_dir():
        raise ValueError(f"input_dir not found: {input_dir}")

    imported: list[dict[str, Any]] = []
    errors: list[str] = []
    for file_path in sorted(input_dir.glob(pattern)):
        if not file_path.is_file():
            continue
        try:
            result = await _import_runner(
                model_path=str(file_path),
                project_path=project_path,
            )
            imported.append({"file": str(file_path), "result": result})
            if not result.get("success"):
                errors.append(f"{file_path.name}: {result.get('error', 'import failed')}")
        except Exception as exc:
            errors.append(f"{file_path.name}: {exc}")

    job.output = {
        "imported_count": len(imported),
        "imports": imported,
        "errors": errors,
    }
    if not imported:
        job.error = "No files matched batch import pattern"
    elif errors:
        job.error = "; ".join(errors[:5])


async def _run_simulation_job(job: UnityJob) -> None:
    if _simulation_runner is None:
        raise RuntimeError("Simulation job runner not configured")
    params = job.params
    duration = float(params.get("duration", 1.0))
    record_data = bool(params.get("record_data", False))
    timeout = float(params.get("timeout", max(duration * 3, 30.0)))
    result = await _simulation_runner(duration=duration, record_data=record_data, timeout=timeout)
    job.output = result if isinstance(result, dict) else {"result": result}
    job.mode = result.get("mode") if isinstance(result, dict) else None
    if not result.get("success"):
        job.error = result.get("error") or "Simulation failed"


async def submit_unity_job(
    job_type: str,
    *,
    name: str = "unity_job",
    params: dict[str, Any] | None = None,
) -> str:
    """Queue a Unity job and return job_id immediately."""
    job_id = str(uuid.uuid4())[:12]
    job = UnityJob(id=job_id, job_type=job_type, name=name, params=params or {})
    _jobs[job_id] = job
    _prune_old_jobs()

    runners = {
        "build": _run_build_job,
        "batch_import": _run_batch_import_job,
        "simulation": _run_simulation_job,
    }
    runner = runners.get(job_type)
    if runner is None:
        job.status = JobStatus.FAILED
        job.error = f"Unknown job_type: {job_type}"
        job.finished_at = time.time()
        return job_id

    async def _runner() -> None:
        job.status = JobStatus.RUNNING
        job.started_at = time.time()
        try:
            await runner(job)
            if job.status == JobStatus.RUNNING:
                job.status = JobStatus.FAILED if job.error else JobStatus.COMPLETED
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.error = "Job cancelled"
            raise
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
            logger.exception("Unity job %s failed: %s", job_id, exc)
        finally:
            job.finished_at = time.time()
            _update_jobs_gauge()

    job._task = asyncio.create_task(_runner())
    _update_jobs_gauge()
    return job_id


def get_job(job_id: str) -> UnityJob | None:
    return _jobs.get(job_id)


def job_to_dict(job: UnityJob) -> dict[str, Any]:
    return {
        "id": job.id,
        "job_type": job.job_type,
        "name": job.name,
        "status": job.status.value,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "params": job.params,
        "output": job.output,
        "error": job.error,
        "mode": job.mode,
    }


def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    jobs = sorted(_jobs.values(), key=lambda j: j.created_at, reverse=True)
    return [job_to_dict(j) for j in jobs[:limit]]


async def cancel_job(job_id: str) -> bool:
    job = _jobs.get(job_id)
    if not job or not job._task:
        return False
    if job.status not in (JobStatus.PENDING, JobStatus.RUNNING):
        return False
    job._task.cancel()
    try:
        await job._task
    except asyncio.CancelledError:
        pass
    job.status = JobStatus.CANCELLED
    job.finished_at = time.time()
    _update_jobs_gauge()
    return True
