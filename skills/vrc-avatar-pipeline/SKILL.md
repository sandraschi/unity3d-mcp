---
name: vrc-avatar-pipeline
description: Expert instructions for importing, optimizing, and uploading VRM avatars to VRChat. Optimized for FastMCP 3.2.0 agentic workflows.
---

# VRChat Avatar Pipeline (SOTA 2026)

This skill enables the automated transformation of VRM assets into VRChat-ready avatars using the `unity3d-mcp` VRM and VRChat managers.

## 🚀 Step-by-Step Pipeline

### 1. Asset Preparation
-   Import the VRM file using `import_vrm_avatar`.
-   Verify that UniVRM is installed using `check_univrm_installed`.

### 2. Optimization (VRChat SDK)
-   Apply `optimize_for_vrchat` to the imported prefab.
-   Ensure materials are converted to VRChat-compliant shaders (e.g., Liltoon or Standard) using `configure_unity_materials`.
-   Validate results via `vrchat_validate_avatar`.

### 3. Deployment
-   Ensure authentication with `vrchat_check_auth`.
-   Execute `upload_vrchat_avatar` to your VRChat account.

## 🛠️ Advanced Optimization
For high-performance avatars (Mobile/Quest):
-   Perform texture atlas generation via `optimize_textures`.
-   Lower polygon counts on specific LODs if supported by project assets.

---
**Status:** ✅ SOTA v12.0 Compliant
**Author:** Unity3D-MCP Intelligence
