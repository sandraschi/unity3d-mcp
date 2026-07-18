# VRChat Integration - Unity3D-MCP

**Corrected 2026-07-18** against `tools/portmanteau/vrchat.py`. The
previous version invented `setup_vrchat_avatar`, `create_expression_menu`,
`validate_vrchat_avatar`, `upload_vrchat_avatar` with parameter shapes
that never matched the real tool. There is one tool, `vrchat`, with six
real operations.

## VRChat SDK Setup

### SDK Installation
Manual, not automated by this server:
```
Requirements:
- Unity 2019.4.31f1 (VRChat recommended)
- VRChat Creator Companion (VCC)
- VRChat SDK3 - Avatars

Installation via VCC:
1. Open VRChat Creator Companion
2. Create new avatar project (auto-installs SDK)
3. Or migrate existing project
```
Check whether the SDK is already installed with
`vrchat(operation="check_sdk", project_path="...")`.

### VRC Avatar Descriptor
```python
vrchat(
    operation="setup_descriptor",
    avatar_prefab="Assets/Avatars/Character.prefab",
    viewpoint_position=[0, 1.6, 0]
)
```
Real, delegates to `VRChatSDKManager.setup_avatar_descriptor`. Note the
real parameter is `avatar_prefab` (a path), not `avatar_root`, and there
is no `avatar_name`/`description` at this step — those belong to the
upload step below.

### Expression Parameters
Reference only — no tool sets these directly:
```
VRChat Parameters:
- VRCFaceBlendH (horizontal mouth)
- VRCFaceBlendV (vertical mouth)
- VRCEmote (gesture number)
- Custom parameters (toggles, floats, ints, bools)

Parameter types:
- Bool: On/off toggles (clothes, accessories)
- Int: Multiple states (hat selection)
- Float: Continuous (ear rotation)
```

### Expression Menus
**No `create_expression_menu` tool, or any equivalent, exists.** Building
VRChat expression menus (buttons, toggles, sub-menus, puppets) is not
automatable through this server — do this manually in the Unity Editor's
VRChat SDK panel. The menu-type reference below is accurate as
background, just not something you can call a tool for:
```
Menu types:
- Button: Trigger action
- Toggle: On/off state
- Sub-menu: Navigate to other menus
- Two Axis Puppet: 2D control
- Four Axis Puppet: 4D control
- Radial Puppet: Circular control
```

## Avatar Upload Process

### Pre-Upload Validation
```python
vrchat(
    operation="validate_avatar",
    avatar_prefab="Assets/Avatars/Character.prefab",
    project_path="D:/Projects/MyAvatar"
)
```
Real. Checks performance rank, missing scripts, shader compatibility, and
similar, via `VRChatSDKManager.validate_avatar`.

### Authentication
```python
vrchat(operation="check_auth")
vrchat(operation="authenticate", username="...", password="...", totp_code="...")
```

### Upload to VRChat
```python
vrchat(
    operation="upload_avatar",
    avatar_prefab="Assets/Avatars/Character.prefab",
    avatar_name="Character",
    description="Custom VRChat avatar",
    tags=["original"],
    release_status="private"  # or "public"
)
```
Real — this is the one confirmed to shell out to actual Unity CLI
(`-batchmode -quit -executeMethod
VRC.SDKBase.Editor.BuildPipeline.BuildAndUploadAvatar`), not a mock. Note
the real parameter is `release_status` ("private"/"public"), not
`visibility`, and there's no `thumbnail_camera` parameter — thumbnail
generation is handled by the VRChat SDK itself during upload, not
configurable through this tool.

---

**Austrian VRChat**: Optimized, expressive, community-ready! 🇦🇹🌐
