# 📘 API Reference: Unity3D-MCP Toolset

The Unity3D-MCP server provides a comprehensive toolset for project lifecycle management, real-time Editor control, avatar optimization, and build automation.

**Rewritten 2026-07-18** to describe the real, currently-registered tool
surface. The previous version of this file described a flat, one-tool-per-
action API (`create_unity_project`, `import_vrm_avatar`, `trigger_unity_build`,
etc.) that predates a portmanteau refactor and was never actually callable —
none of those names exist as MCP tools. See `README.md`'s "Tool surface"
table for the canonical, source-verified list; this file gives usage detail
per tool.

---

## 🏗️ Core: Project & Scene Management

### `unity_core`
Consolidates project lifecycle operations (real, CLI-backed via
`UnityEditorManager`/`ProjectManager` — not bridge-dependent).
- `operation="create_project"` — `project_name`, `project_path`, `template`, `unity_version`
- `operation="launch_editor"` — `project_path`, `unity_version`, `batch_mode`, `no_graphics`
- `operation="execute_method"` — `class_name`, `method_name`, `parameters`, `project_path` (runs Unity in `-batchmode -executeMethod`)
- `operation="check_univrm"` / `install_univrm"` — `project_path`, `vrm_version`, `refresh_unity`
- `operation="create_project_with_univrm"` — combines create_project + install_univrm

(Previously documented here as three separate tools: `create_unity_project`,
`launch_unity_editor`, `execute_unity_method`. None of those names exist —
they're `unity_core` operations.)

### `unity_scene`
- `operation="create_light"` — scene lighting setup.

---

## 🕹️ Dual-Mode: Hands-In (Live) / Hands-Off (Disk)

### `unity_bridge`
**Objective**: Live Unity Editor bridge (`MCPBridge.cs`); status check and [Hands-In] real-time session control in one tool.
- **`operation`**: `status`, `execution_mode`, `ping`, `get_hierarchy`, `transform_object`, `create_object`, `delete_object`, `capture_game_view`.
- **`target`**: Name or InstanceID for transformation/deletion.
- **`position / rotation`**: Float arrays `[x, y, z]` for object placement.
- **`output_path / width / height`**: For `capture_game_view`.
- **Return of `operation="status"`**: `{success, status: "connected/disconnected", mode: "hands_in/hands_off", port: 10835}`.

### `unity3d_disk_api`
**Objective**: [Hands-Off] Direct project file manipulation.
- **`operation`**: `inspect_file`, `list_textures`, `modify_yaml`.
- **`file_path`**: Path to `.unity`, `.prefab`, or `.asset`.
- **`new_value`**: Used for `modify_yaml` to update properties (e.g., light intensity).

### `unity_api`
**Objective**: [Hands-In] Advanced Editor automation via the same
`MCPBridge.cs` bridge as `unity_bridge`. **All operations require a live
Unity Editor session with the bridge running** — without it, every
operation returns `{"success": false, "error": "Unity Editor bridge not
connected..."}`, not a fake success.
- `operation="get_scene_objects"` — `object_filter`. Lists live scene objects via `get_hierarchy`.
- `operation="modify_object"` — `object_name`, `modifications` (`position`/`rotation`).
- `operation="create_prefab"` — `object_name`, `prefab_name`. Calls `PrefabUtility.SaveAsPrefabAsset` on the Editor side.
- `operation="run_simulation"` — `duration`, `record_data`. Enters Play mode for `duration` seconds.
- `operation="execute_method"` — `class_name`, `method_name`. **Fixed
  2026-07-18** (was a hardcoded stub). Uses C# reflection to invoke a
  public, static, **parameterless** method — the same constraint Unity's
  own `-executeMethod` CLI flag has. `parameters` is accepted but ignored,
  and the response says so explicitly rather than pretending to apply it.
- `operation="batch_operations"` — `operations` (list of dicts, each using
  the same flat command shape as a single operation). **Fixed 2026-07-18.**
  Executed sequentially on the Editor side; results and a `success_count`
  are returned per sub-operation.
- `operation="move_along_path"` / `"follow_path_2d"` / `"follow_path_3d"` —
  `object_name`, `path_points`, `speed`/`duration`, `loop`, etc. **Fixed
  2026-07-18.** All curve `path_type`s (`bezier`, `spline`, `catmull_rom`)
  are approximated as straight multi-segment linear interpolation on the
  bridge — real curve math is not implemented, and this is stated in the
  tool's own docstring, not hidden.
- `operation="create_path_visualization"` — `path_points`, `color`,
  `thickness`. **Fixed 2026-07-18.** Creates a real `GameObject` with a
  `LineRenderer` component tracing the path. `visualization_type` values
  other than `"line"` (`"dotted"`, `"waypoints"`, `"full"`) are accepted
  but not yet rendered differently.
- `operation="stop_path_movement"` — `object_name`, `decelerate`,
  `deceleration_time`. **Fixed 2026-07-18.** With `decelerate=True`, ramps
  speed to zero over `deceleration_time` seconds rather than stopping
  instantly.

⚠️ **Disclosure**: the C# side of these fixes (`MCPBridge.cs`) was written
and manually reviewed line-by-line, but **could not be compiled or tested
against a live Unity Editor** in the environment it was built in (no
`dotnet`/`mono`/`csc` available, and package-manager installs were blocked
by container permissions). Treat this bridge code as unverified until
smoke-tested against a real Editor session.

---

## 🎭 Avatar & VRM Optimization

### `unity_avatar`
- `operation="import_vrm"` — `vrm_path`, `project_path`, `optimize_for_vrchat` (bool, default True), `create_prefab` (bool, default True). Copies the VRM into `Assets/Models/`.
  **Fixed 2026-07-18.** When `optimize_for_vrchat=True`, `vrchat_optimizations`
  now parses the VRM's real binary glTF JSON chunk (stdlib `struct`/`json`,
  no Unity needed) and reports real `material_count`, `texture_count`,
  `mesh_count`, and a per-material summary, written to a JSON manifest at
  `Assets/Models/{name}_vrchat_conversion_manifest.json`. It does **not**
  perform shader conversion or texture compression — those fields are
  explicitly labeled `"NOT performed here"` rather than faked, since a
  guessed Unity shader GUID can silently produce a broken pink-shader
  material. Verified against `tests/unit/test_avatar_real.py` (15 tests,
  including against the real `tests/fixtures/Nekomimi-chan.vrm` fixture).
- `operation="setup_animator"` — `avatar_path`, `animator_type` ("humanoid"/"generic"), `include_facial`, `project_path`.
  **Fixed 2026-07-18.** Now writes a real Unity `AnimatorController` YAML
  asset (`Assets/Animators/{name}_Controller.controller`) plus its `.meta`
  file with a real GUID, using correct Unity class IDs (`!u!91`
  AnimatorController, `!u!1107` AnimatorStateMachine, `!u!1102`
  AnimatorState). Returns a `caveats` list stating this was **not validated
  against a live Unity Editor** — structurally correct by construction and
  by test, not confirmed to open cleanly in the Editor.

(Previously documented here as three separate tools: `import_vrm_avatar`,
`optimize_for_vrchat`, `setup_avatar_rigging`. None of those names exist —
`import_vrm_avatar` → `unity_avatar(operation="import_vrm")`,
`setup_avatar_rigging` → closest real equivalent is
`unity_avatar(operation="setup_animator")` (bone/animator setup, not the
same scope as "rigging"). Standalone `optimize_for_vrchat` as described —
a dedicated shader/PipelineManager/polycount pass over an already-imported
avatar — does not exist as a tool at all; the closest real workflow is
`unity_avatar(operation="import_vrm", optimize_for_vrchat=True)` at import
time, plus `unity_validation(operation="validate_avatar")` and
`vrchat(operation="validate_avatar")` for an actual (real, non-mocked)
preflight check. Do not confuse this with `worldlabs`'s own
`optimize_for_vrchat` operation, which is unrelated — it optimizes
Marble/Gaussian-splat world assets, not avatars.)

### `unity_asset`
- `operation="optimize_textures"` — texture optimization pass.

---

## 🚀 VRChat: SDK Integration

### `vrchat`
Real, CLI-backed via `VRChatSDKManager` (confirmed: `upload_avatar` shells
out to `Unity.exe -batchmode -quit -executeMethod
VRC.SDKBase.Editor.BuildPipeline.BuildAndUploadAvatar`, not a stub).
- `operation="check_auth"` / `"authenticate"` — `username`, `password`, `totp_code`
- `operation="check_sdk"` — `project_path`
- `operation="validate_avatar"` — `avatar_prefab`, `project_path`
- `operation="setup_descriptor"` — `avatar_prefab`, `viewpoint_position`
- `operation="upload_avatar"` — `avatar_prefab`, `avatar_name`, `description`, `tags`, `release_status`

**Avatars only — no world upload/publish.** For world-building, see
`vrchat-mcp/docs/Building_VRChat_Worlds_With_Unity3D_MCP.md` (uses
`unity_bridge`/`unity_import`/`unity_validation` for scene assembly; VRChat
world publish remains a manual Unity/VRChat-SDK step — no
`publish_world` operation exists anywhere in this server).

(Previously documented here as `vrchat_validate_avatar` and
`vrchat_upload_avatar`. Neither name exists — both are `vrchat` operations.)

---

## 🌍 World Labs: Marble/Chisel Integration

### `worldlabs`
- `operation="import_marble"` — import AI-generated `.marble` world snapshots.
- `operation="assemble_review"`, `"check_gaussian"`, `"install_gaussian"`, `"optimize_for_vrchat"` — see `README.md` table.

(Previously documented here as `worldlabs_import_marble`, which doesn't
exist as a standalone tool — it's a `worldlabs` operation. `worldlabs_chisel_edit`,
described here as bidirectional geometry editing against the Chisel engine,
**does not exist in any form** — no operation on `worldlabs` or any other
tool does this. There is no live, agent-driven mesh-editing round-trip to
World Labs; `worldlabs`'s real operations are import/review/optimize on
already-generated assets, not interactive editing.)

---

## 📦 Build: Multi-Platform Pipelines

### `unity_build`
- `operation="build_project"` — `project_path`, `build_target` (`StandaloneWindows64`, `Android`, `iOS`, `WebGL`, etc.), `output_path`, `development_build`.

(Previously documented here as `trigger_unity_build`. That name doesn't
exist — it's `unity_build(operation="build_project")`.)

---

## 📊 Error Handling & Troubleshooting

- **Timeout**: Most bridge operations have a 5.0s timeout.
- **Bridge Installation**: Ensure `MCPBridge.cs` is in the `Assets/Editor` folder.
- **Port Conflict**: Check for port `10835` usage if connection fails.
