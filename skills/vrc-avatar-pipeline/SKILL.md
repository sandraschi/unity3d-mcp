---
name: vrc-avatar-pipeline
description: Expert instructions for importing, optimizing, and uploading VRM avatars to VRChat. Optimized for FastMCP 3.2.0 agentic workflows.
---

# VRChat Avatar Pipeline (SOTA 2026)

This skill enables the automated transformation of VRM assets into VRChat-ready avatars using the `unity3d-mcp` VRM and VRChat managers.

**Rewritten 2026-07-18**: every tool name in the previous version of this
file (`import_vrm_avatar`, `check_univrm_installed`, `optimize_for_vrchat`
as a standalone tool, `configure_unity_materials`, `vrchat_validate_avatar`,
`vrchat_check_auth`, `upload_vrchat_avatar`, `optimize_textures` as a
standalone tool) was wrong — none of those are registered MCP tools. This
version uses only real, verified `tool(operation=...)` calls.

## 🚀 Step-by-Step Pipeline

### 1. Asset Preparation
-   Import the VRM file: `unity_avatar(operation="import_vrm", vrm_path=..., project_path=..., optimize_for_vrchat=True, create_prefab=True)`.
-   Verify UniVRM is installed: `unity_core(operation="check_univrm", project_path=...)`. If missing, install it with `unity_core(operation="install_univrm", project_path=...)`.

### 2. Optimization (VRChat SDK)
-   `import_vrm`'s `optimize_for_vrchat=True` flag (above) triggers a
    `vrchat_optimizations` report in the response — **be aware this report
    is currently a hardcoded placeholder** (`material_conversion`,
    `texture_compression`, etc. are fixed strings, not computed from the
    actual model). It does not really convert materials to
    VRChat-compliant shaders or add SDK components yet. There is no
    `configure_unity_materials` tool or equivalent — material/shader
    conversion is not currently automatable through this server. Treat
    this step as manual until that's implemented (tracked in `TODO.md`).
-   Validate results: `vrchat(operation="validate_avatar", avatar_prefab=..., project_path=...)` — this one is real (CLI-backed, not mocked).

### 3. Deployment
-   Ensure authentication: `vrchat(operation="check_auth")`, and if needed `vrchat(operation="authenticate", username=..., password=..., totp_code=...)`.
-   Upload: `vrchat(operation="upload_avatar", avatar_prefab=..., avatar_name=..., description=..., tags=[...], release_status="private")`.

## 🛠️ Advanced Optimization
For high-performance avatars (Mobile/Quest):
-   Texture optimization: `unity_asset(operation="optimize_textures")`.
-   Polygon/material/limits checks: `unity_validation(operation="check_polycount")`, `unity_validation(operation="check_materials")`, `unity_validation(operation="list_limits")`.
-   There is no dedicated per-LOD polygon reduction tool — not automatable through this server today.

---
**Status:** Corrected against `src/unity3d_mcp/server.py` and
`tools/portmanteau/{unity_avatar,unity_core,vrchat,unity_asset,unity_validation}.py`, 2026-07-18.
**Author:** Unity3D-MCP Intelligence
