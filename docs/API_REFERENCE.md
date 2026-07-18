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

---

## 🎭 Avatar & VRM Optimization

### `unity_avatar`
- `operation="import_vrm"` — `vrm_path`, `project_path`, `optimize_for_vrchat` (bool, default True), `create_prefab` (bool, default True). Copies the VRM into `Assets/Models/`.
  ⚠️ **Honesty note**: when `optimize_for_vrchat=True`, the returned
  `vrchat_optimizations` report (`material_conversion`, `texture_compression`,
  `polygon_reduction`, `performance_rank`, `sdk_components`) is a **hardcoded
  dict, not a computed result** — it does not actually invoke Unity to
  convert shaders, compress textures, or add SDK components. Treat it as a
  todo-list of what *should* happen, not a report of what did. Flagged in
  `TODO.md`, not fixed as part of this pass (that's new engineering work,
  not a doc correction).
- `operation="setup_animator"` — `avatar_path`, `animator_type` ("humanoid"/"generic"), `include_facial`. Same caveat: returns a templated animator-controller config, does not write a real `.controller` asset to disk.

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
