# unity3d-mcp — TODO

Stretch goals:
- [ ] **Nightly CI** — scheduled runs (optional, CI already runs on push/PR)
- [ ] **Fix remaining text-[10px] instances** — 18 across avatar, hierarchy, script-console, plugin-manager pages

## Found 2026-07-18, during a README accuracy audit (not fixed, flagged only — removing registered tools is a breaking change and deserves its own pass)

- **`app.py` is dead code.** Not imported by `__main__.py`, not referenced
  in `pyproject.toml`. The real entry point is `server.py`
  (`server_instance.app`). `app.py` and `app.py.20260712_153809.bak`
  contain an entire second implementation of motor control, path
  movement, import/export, and VRM-Unity-rigging tools that were never
  wired up and aren't running. Either delete `app.py` or actually
  register its tools — right now it's just confusing dead weight that an
  earlier README revision was silently describing as if it were live.
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

## Still open, not started (lower priority, found in passing)

- `docs/API_REFERENCE.md` and `prompts/*` still document several tool
  names that were never real to begin with (not something this pass
  broke) — `import_vrm_avatar`, `optimize_for_vrchat`, `setup_avatar_rigging`,
  `motor_control`, `import_3d_model`, `execute_unity_method`,
  `create_unity_project`, `switch_platform`, `install_univrm`,
  `install_asset_package` and similar do not exist as MCP tools. Same
  phantom-op bug class as everything above, pre-dates this session,
  out of scope for this pass — flagged here so it isn't mistaken for
  "already covered."
- `app.py` (dead code, contains an unregistered second implementation of
  motor/import-export/VRM-rigging tools) still not deleted or wired up.
