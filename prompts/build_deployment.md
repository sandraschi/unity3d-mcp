# Build & Deployment - Unity3D-MCP

**Corrected 2026-07-18** against `tools/portmanteau/unity_build.py` and
`tools/portmanteau/vrchat.py`. The previous version invented per-platform
tools (`build_windows`, `build_android`, `build_vrchat_avatar`) that never
existed. There is exactly one build tool, `unity_build`, parameterized by
`build_target`.

## Multi-Platform Builds

### Windows Build
```python
unity_build(
    operation="build_project",
    project_path="D:/Projects/MyGame",
    build_target="StandaloneWindows64",
    output_path="Builds/Windows/Game.exe",
    development_build=False
)
```
Build settings (scripting backend, IL2CPP/Mono, API compatibility level,
compression) are project-level Unity settings this tool does not control —
set them in the Unity Editor's Player Settings before building.

### Android Build (Quest)
```python
unity_build(
    operation="build_project",
    project_path="D:/Projects/MyGame",
    build_target="Android",
    output_path="Builds/Android/game.apk",
    development_build=False
)
```
Architecture (ARM64), min/target SDK version, texture compression (ASTC),
and graphics API are Player Settings configured in the Unity Editor, not
parameters this tool takes.

### VRChat Avatar Build
There is no separate "build a VRChat avatar" tool. VRChat avatars are
built and uploaded in one step:
```python
vrchat(
    operation="upload_avatar",
    avatar_prefab="Assets/Avatars/Character.prefab",
    avatar_name="Character",
    description="...",
    tags=["..."],
    release_status="private"
)
```
This is real — it shells out to `Unity.exe -batchmode -quit -executeMethod
VRC.SDKBase.Editor.BuildPipeline.BuildAndUploadAvatar`, confirmed against
`vrchat.py`'s `VRChatSDKManager`. **Avatars only — VRChat world builds are
not automatable this way** (no `publish_world` operation exists anywhere
in this server); see
`vrchat-mcp/docs/Building_VRChat_Worlds_With_Unity3D_MCP.md` in the
`vrchat-mcp` repo for the honest world-building pipeline.

---

## Build Optimization

### Compression Settings
```
None: Fastest build, largest size
LZ4: Fast decompression, medium size (recommended)
LZMA: Smallest size, slower loading
```
These are Unity Player Settings, not parameters of `unity_build` — set
them in the Editor.

### Asset Bundling
General guidance, not something this server automates:
- Include only used assets
- Compress textures
- Strip unused code
- Reduce shader variants

---

**Austrian Builds**: Fast, optimized, reliable! 🇦🇹📦
