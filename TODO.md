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
  **Note (2026-07-18, later same day): `create_prefab` was mischaracterized
  above as scaffolded — it was already real (`_api_create_prefab` calls
  `execute_bridge_action("create_prefab", ...)`, and `CreatePrefab(cmd)` on
  the C# side genuinely calls `PrefabUtility.SaveAsPrefabAsset`). Corrected
  in `README.md`/`docs/API_REFERENCE.md` in the pass below.**

## Fixed 2026-07-18 ("fix lying hardcodes, implement the stubs properly")

- **`unity_avatar(operation="import_vrm", optimize_for_vrchat=True)`'s
  `vrchat_optimizations` hardcode** — replaced with a real binary
  glTF/VRM parser (`avatar/parse_vrm_gltf_json`, stdlib `struct`/`json`
  only) that reports real `material_count`, `texture_count`, `mesh_count`,
  and a per-material summary, plus writes a JSON manifest to
  `Assets/Models/{name}_vrchat_conversion_manifest.json`. Deliberately
  does **not** fake shader conversion or texture compression — those
  fields are labeled `"NOT performed here"` rather than guessed, since a
  wrong Unity shader GUID silently produces a broken pink-shader material.
  Verified against `tests/unit/test_avatar_real.py` (15 tests, including
  against the real `tests/fixtures/Nekomimi-chan.vrm` fixture).
- **`unity_avatar(operation="setup_animator")`'s templated-dict hardcode**
  — replaced with a real Unity `AnimatorController` YAML asset writer
  (`avatar/build_animator_controller_yaml`), writing an actual
  `Assets/Animators/{name}_Controller.controller` + `.meta` (real GUID) to
  disk, with correct Unity class IDs (`!u!91`/`!u!1107`/`!u!1102`).
  Returns a `caveats` list stating it was **not validated against a live
  Unity Editor**. Verified structurally by 15 pytest tests, not by opening
  the asset in Unity.
- **`unity_api`'s 7 stub operations implemented**:
  `execute_method`, `batch_operations`, `move_along_path`,
  `follow_path_2d`, `follow_path_3d`, `stop_path_movement`,
  `create_path_visualization` — all now call real, working C# handlers
  added to `MCPBridge.cs`, wired through `execute_bridge_action(...)` on
  the Python side (`tools/portmanteau/unity_api.py`), the same pattern
  `get_scene_objects`/`modify_object` already used. Scoped, disclosed
  limitations (not lies — real but incomplete):
  - `execute_method` only supports public, static, **parameterless**
    methods via reflection — the same constraint Unity's own
    `-executeMethod` CLI flag has. Arbitrary parameter marshaling was
    deliberately not attempted (type-mismatched `Invoke` calls throw).
  - Path movement (`move_along_path`/`follow_path_2d`/`follow_path_3d`)
    approximates all `path_type` curve variants (`bezier`, `spline`,
    `catmull_rom`) as straight multi-segment linear interpolation — no
    true curve math.
  - `create_path_visualization`'s `visualization_type` only draws a plain
    `LineRenderer` today; `"dotted"`/`"waypoints"`/`"full"` variants are
    accepted but not yet rendered distinctly.
  - **Not compile-verified.** No C# compiler (`dotnet`/`mono`/`csc`/`mcs`)
    was available in the build environment, and `apt-get`/`sudo` package
    installs were blocked by container permissions. The C# was written and
    manually reviewed line-by-line (brace balance, control flow, type
    usage) but **not compiled or run against a live Unity Editor**. Treat
    `MCPBridge.cs` as unverified until smoke-tested in a real Editor
    session — this is a real, disclosed gap, not swept under the rug.
  - **Python-side verification also incomplete**: `uv run ruff`/`uv run
    pytest` could not run in the session that wrote the Python wiring
    changes (no network access to resolve the `uv`-managed Python
    interpreter, and no cached `ruff`/`pytest`/`fastmcp`/`httpx` wheels
    available offline). Verified instead via `python3 -m py_compile` on
    every changed file and the full `src/unity3d_mcp` tree (all pass), plus
    manual review against the existing `get_scene_objects`/`modify_object`
    pattern in the same file. Run `uv run ruff check` and `uv run pytest`
    yourself before trusting this in CI.
- Corrected the `create_prefab` mischaracterization from the previous
  entry above in `README.md` and `docs/API_REFERENCE.md` — it was already
  real (bridge-backed via `PrefabUtility.SaveAsPrefabAsset`), not
  scaffolded.
- Added a `unity_api` section to `docs/API_REFERENCE.md` (previously
  entirely absent from that file) documenting every operation's real
  behavior and the limitations above.
