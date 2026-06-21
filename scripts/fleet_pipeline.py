"""CLI for fleet E2E pipeline (blender-mcp -> unity3d-mcp)."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path

from unity3d_mcp.utils.fleet_pipeline import (
    DEFAULT_BLENDER_URL,
    DEFAULT_GAZEBO_FILE_TEMPLATE,
    DEFAULT_GAZEBO_MCP_URL,
    DEFAULT_UNITY_URL,
    run_fleet_pipeline,
)
from unity3d_mcp.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fleet pipeline: blender export -> unity import -> validate -> build",
    )
    parser.add_argument(
        "--project-path",
        required=True,
        help="Unity project path (must exist)",
    )
    parser.add_argument(
        "--model-path",
        default="",
        help="Skip blender export; use existing GLB/VRM/FBX",
    )
    parser.add_argument(
        "--unity-url",
        default=DEFAULT_UNITY_URL,
        help=f"unity3d-mcp HTTP base (default {DEFAULT_UNITY_URL})",
    )
    parser.add_argument(
        "--gazebo-models",
        nargs="*",
        default=None,
        help="Gazebo model names to import via POST /api/v1/gazebo/import",
    )
    parser.add_argument(
        "--gazebo-file-template",
        default=DEFAULT_GAZEBO_FILE_TEMPLATE,
        help="Path template for gazebo meshes, e.g. gazebo_models/{model}.fbx",
    )
    parser.add_argument(
        "--gazebo-mcp-url",
        default=DEFAULT_GAZEBO_MCP_URL,
        help=f"Optional gazebo-mcp HTTP URL (default {DEFAULT_GAZEBO_MCP_URL})",
    )
    parser.add_argument(
        "--with-gazebo",
        action="store_true",
        help="Run gazebo import step (requires --gazebo-models)",
    )
    parser.add_argument(
        "--try-gazebo-mcp-export",
        action="store_true",
        help="Attempt export via gazebo-mcp before Unity gazebo import",
    )
    parser.add_argument(
        "--blender-url",
        default=DEFAULT_BLENDER_URL,
        help=f"blender-mcp HTTP base URL (default {DEFAULT_BLENDER_URL})",
    )
    parser.add_argument(
        "--export-operation",
        default="export_glb",
        help="blender_export operation (export_glb, export_unity, export_vrm, ...)",
    )
    parser.add_argument(
        "--export-dir",
        default="",
        help="Directory for blender export output",
    )
    parser.add_argument(
        "--object-names",
        nargs="*",
        default=None,
        help="Blender object names to export",
    )
    parser.add_argument(
        "--target-platform",
        default="vrchat",
        help="Validation platform (vrchat, chilloutvr, resonite, cluster, generic)",
    )
    parser.add_argument(
        "--avatar-prefab",
        default="",
        help="Optional avatar prefab path for unified_audit",
    )
    parser.add_argument(
        "--build-target",
        default="StandaloneWindows64",
        help="Unity build target",
    )
    parser.add_argument(
        "--build-output-dir",
        default="",
        help="Unity build output directory",
    )
    parser.add_argument(
        "--build-timeout",
        type=float,
        default=3600.0,
        help="Max seconds to wait for build job",
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Require --model-path; do not call blender-mcp",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip validation and audit steps",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Stop after import/validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON report on stdout",
    )
    return parser


async def _async_main(args: argparse.Namespace) -> int:
    export_dir = Path(args.export_dir) if args.export_dir else None
    build_dir = Path(args.build_output_dir) if args.build_output_dir else None
    model_path = args.model_path.strip() or None

    if args.skip_export and not model_path:
        logger.error("--skip-export requires --model-path")
        return 2

    report = await run_fleet_pipeline(
        project_path=args.project_path,
        model_path=model_path,
        blender_url=args.blender_url,
        unity_url=args.unity_url,
        gazebo_mcp_url=args.gazebo_mcp_url,
        gazebo_models=args.gazebo_models,
        gazebo_file_template=args.gazebo_file_template,
        skip_gazebo=not args.with_gazebo,
        try_gazebo_mcp_export=args.try_gazebo_mcp_export,
        export_operation=args.export_operation,
        export_dir=export_dir,
        object_names=args.object_names,
        skip_export=args.skip_export or bool(model_path),
        skip_validate=args.skip_validate,
        skip_build=args.skip_build,
        target_platform=args.target_platform,
        build_target=args.build_target,
        build_output_dir=build_dir,
        build_timeout=args.build_timeout,
        avatar_prefab=args.avatar_prefab.strip() or None,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print("=== fleet pipeline ===")
        print(f"execution_mode: {report.execution_mode}")
        print(f"model_path: {report.model_path}")
        print(f"project_path: {report.project_path}")
        for step in report.steps:
            status = "OK" if step.success else "FAIL"
            print(f"  [{status}] {step.name}")
            if not step.success and step.detail.get("error"):
                print(f"         {step.detail['error']}")
        print(f"result: {'SUCCESS' if report.success else 'FAILED'}")
        if report.build_output_path:
            print(f"build_output: {report.build_output_path}")

    return 0 if report.success else 1


def main() -> None:
    setup_logging()
    args = _build_parser().parse_args()
    try:
        code = asyncio.run(_async_main(args))
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted")
        code = 130
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        code = 1
    raise SystemExit(code)


if __name__ == "__main__":
    main()
