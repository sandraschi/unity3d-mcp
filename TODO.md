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
- **11 duplicate `api_*` flat tools in `server.py`** (`api_execute_method`,
  `api_get_scene_objects`, `api_modify_object`, `api_create_prefab`,
  `api_run_simulation`, `api_batch_operations`, `api_move_along_path`,
  `api_create_path_visualization`, `api_follow_path_2d`,
  `api_follow_path_3d`, `api_stop_path_movement`) are strictly superseded
  by the `unity_api` portmanteau tool. Worse: they're *more stale* than
  `unity_api` — every flat version unconditionally returns "not
  implemented," even for `get_scene_objects`/`modify_object`, which
  `unity_api` actually performs via the live bridge now. An agent calling
  the flat names gets a false negative. Recommend: deprecate (log a
  warning + delegate to `unity_api` internally) for one release, then
  remove.
- **9 platform-helper flat tools** (`list_vr_platforms`,
  `check_platform_sdk`, `check_cck_installed`, `setup_cvr_avatar`,
  `validate_for_chilloutvr`, `prepare_for_resonite`,
  `check_resonite_compatibility`, `check_cluster_kit`,
  `prepare_for_cluster`) duplicate `multiplatform`'s operations
  one-for-one. Lower priority than the `api_*` set since these aren't
  stale/broken, just redundant — same recommendation (deprecate, then
  remove) whenever someone's touching this area anyway.
- **`unity_bridge` vs `unity3d_editor_api` vs `unity3d_bridge_status`**:
  three tools covering overlapping live-Editor-bridge ground
  (ping/get_hierarchy/create_object/delete_object/transform_object +
  status checks). `unity3d_editor_api` additionally has
  `capture_game_view`, which isn't in `unity_bridge` — that's the one
  real gap; everything else is duplicate surface. Consolidate into
  `unity_bridge` and add `capture_game_view` there, then remove the
  other two.
- **Two prompts referenced nonexistent tool names** — `unity_setup_workflow`
  and `vrc_avatar_workflow` told agents to call `create_unity_project`,
  `launch_unity_editor`, `import_vrm_avatar`, `optimize_for_vrchat`,
  `vrchat_validate_avatar` — none of which are registered tools. **Fixed**
  same session: both now reference the real portmanteau operations
  (`unity_core`, `unity_avatar`, `unity_asset`, `unity_validation`,
  `vrchat`).
- README's tool documentation (three separate, mutually-inconsistent tool
  lists) rewritten to one source of truth. **Fixed** same session.
