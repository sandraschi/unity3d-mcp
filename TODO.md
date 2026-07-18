# unity3d-mcp — TODO

Stretch goals:
- [ ] **Nightly CI** — scheduled runs (optional, CI already runs on push/PR)
- [ ] **Fix remaining text-[10px] instances** — 18 across avatar, hierarchy, script-console, plugin-manager pages

## Found 2026-07-18, during a README accuracy audit (not fixed, flagged only — removing registered tools is a breaking change and deserves its own pass)

- **`app.py` is dead code.** — **Fixed 2026-07-18 (second follow-up
  pass).** Deleted `app.py` and `app.py.20260712_153809.bak`. Confirmed
  safe first: not imported by `__main__.py`, not referenced in
  `pyproject.toml`, and the server (`unity3d_mcp.server`) imports and
  initializes cleanly with both files gone (verified live, not just via
  grep). The motor/import-export/VRM-rigging code it contained was a
  second, never-wired implementation — nothing was lost by deleting it
  since it was never reachable; the *real* copies of that logic
  (`motor_manager.py`, `import_export_manager.py`, `vrm_avatar_manager.py`)
  are untouched and still exist, still unregistered as tools.
- **11 duplicate `api_*` flat tools in `server.py`** — **Fixed 2026-07-18
  (same day, follow-up pass).** Removed entirely (`api_execute_method`,
  `api_get_scene_objects`, `api_modify_object`, `api_create_prefab`,
  `api_run_simulation`, `api_batch_operations`, `api_move_along_path`,
  `api_create_path_visualization`, `api_follow_path_2d`,
  `api_follow_path_3d`, `api_stop_path_movement`), along with their
  backing `_api_*` stub methods on the `Unity3DMCP` class (same names,
  also all unconditional "not implemented" stubs, confirmed unused by
  anything except the tools just removed — checked via grep across
  `tests/` first, no coverage touches them). Verified against
  `tests/test_phase1_tools.py`/`test_phase2_tools.py`, which test
  `UnityAPIToolManager._api_*` directly (a different class, in
  `unity_api.py`) — untouched, still the real implementation. Use
  `unity_api(operation=...)`.
- **9 platform-helper flat tools** — **Fixed 2026-07-18 (same day,
  follow-up pass).** Removed entirely (`list_vr_platforms`,
  `check_platform_sdk`, `check_cck_installed`, `setup_cvr_avatar`,
  `validate_for_chilloutvr`, `prepare_for_resonite`,
  `check_resonite_compatibility`, `check_cluster_kit`,
  `prepare_for_cluster`). Verified one-for-one against `multiplatform`'s
  operations in `tools/portmanteau/platform.py` before removing, and
  checked `tests/unit/test_platforms.py` — it tests the underlying
  `PlatformManager`/`ChilloutVRManager`/`ResoniteManager`/`ClusterManager`
  classes directly, not these flat tools, so no test coverage was lost.
  Use `multiplatform(operation=...)`.
- **`unity_bridge` vs `unity3d_editor_api` vs `unity3d_bridge_status`** —
  **Fixed 2026-07-18 (same day, follow-up pass).** `capture_game_view`
  (the one real gap) ported into `unity_bridge` as a new operation
  (`tools/portmanteau/unity_bridge.py`), then `unity3d_bridge_status` and
  `unity3d_editor_api` removed from `server.py`. The `unity3d_agentic_workflow`
  prompt text (which referenced `unity3d_editor_api` by name in its
  mission instructions) was updated to say `unity_bridge`. Also updated:
  `skills/unity-editor-automation/SKILL.md` (this one is functionally
  loaded via `SkillsDirectoryProvider`, not just a doc — treated with the
  same rigor as the prompt fix below), `docs/GUIDE_EDITOR_AUTO.md`,
  `docs/API_REFERENCE.md`, `docs/ARCHITECTURE_DUAL_MODE.md`,
  `prompts/system.md`, `prompts/user.md`, `prompts/examples.json` (these
  three `prompts/*` files are confirmed **not** wired into `src/` at
  runtime — static reference docs, not live prompts, lower risk than the
  skill file, fixed anyway so no stale examples are left lying around).
  `unity3d_disk_api` and `unity3d_agentic_workflow` were not touched —
  neither duplicates anything.
- **Two prompts referenced nonexistent tool names** — `unity_setup_workflow`
  and `vrc_avatar_workflow` told agents to call `create_unity_project`,
  `launch_unity_editor`, `import_vrm_avatar`, `optimize_for_vrchat`,
  `vrchat_validate_avatar` — none of which are registered tools. **Fixed**
  same session: both now reference the real portmanteau operations
  (`unity_core`, `unity_avatar`, `unity_asset`, `unity_validation`,
  `vrchat`).
- README's tool documentation (three separate, mutually-inconsistent tool
  lists) rewritten to one source of truth. **Fixed** same session.

## Fixed 2026-07-18 (second follow-up pass, "fix it all, even if it predates this session")

- **All pre-existing phantom tool names across docs/prompts/skills** —
  every flat tool name that was never real (`import_vrm_avatar`,
  `optimize_for_vrchat` as a standalone tool, `setup_avatar_rigging`,
  `motor_control`, `import_3d_model`, `execute_unity_method`,
  `create_unity_project`, `switch_platform`, `install_univrm` as a
  standalone tool, `install_asset_package`, `check_vrchat_authentication`,
  `authenticate_vrchat`, `vrchat_validate_avatar`, `vrchat_upload_avatar`,
  `create_material`, `convert_materials_vrchat`, `import_package`,
  `get_build_settings`/`switch_platform`/`optimize_for_platform` as
  standalone tools, `import_marble_world`,
  `check_gaussian_splatting_installed`, `install_gaussian_splatting`,
  `export_gltf`, `export_unity_package`, `create_animation_clip`,
  `setup_animator_controller`, `worldlabs_chisel_edit`,
  `create_expression_menu`, `configure_unity_materials`, and more) has
  been corrected across every file that had it: `docs/API_REFERENCE.md`
  (rewritten in full), `docs/ARCHITECTURE_DUAL_MODE.md`,
  `docs/GUIDE_EDITOR_AUTO.md`, `skills/unity-editor-automation/SKILL.md`,
  `skills/vrc-avatar-pipeline/SKILL.md` (both skill files are functionally
  loaded via `SkillsDirectoryProvider` — fixed with the same rigor as a
  runtime bug, not just docs), and every file in `prompts/`
  (`system.md`, `user.md`, `examples.json`, `game_development.md`,
  `build_deployment.md`, `performance_optimization.md`,
  `vrchat_integration.md`, `vrm_avatar_pipeline.md` — confirmed these
  `prompts/*` files are not wired into `src/` at runtime, so lower stakes
  than the skills, fixed anyway).
- Each corrected reference points to the real `tool(operation=...)` call
  where one exists, or is explicitly marked "no equivalent exists" where
  none does (motor control, generic asset import/export, material
  creation, animation clip authoring, expression menu construction —
  none of these are automatable through this server in any form, real or
  stub).
- Also flagged inline, not fixed (new engineering, not a doc correction):
  `unity_avatar(operation="import_vrm", optimize_for_vrchat=True)` and
  `operation="setup_animator"` both return hardcoded/templated reports,
  not results computed from the actual model — found while verifying
  `avatar/__init__.py` against the docs being corrected. `unity_api`'s
  `execute_method`/`create_prefab`/`batch_operations`/path-movement
  operations are confirmed scaffolded (always "not implemented"); its
  `get_scene_objects`/`modify_object`/`run_simulation` are confirmed real.
  `unity_build` has a real `get_build_settings` method on `BuildManager`
  that is never exposed as a `unity_build` operation — reachable only by
  importing the server module directly, not via MCP.
