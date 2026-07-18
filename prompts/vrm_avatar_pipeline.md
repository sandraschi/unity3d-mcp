# VRM Avatar Pipeline - Unity3D-MCP

**Corrected 2026-07-18** against `tools/portmanteau/unity_avatar.py` and
`tools/portmanteau/unity_validation.py`. The previous version invented
`import_vrm` (as a bare function with an `import_settings` dict),
`validate_vrm_avatar`, `optimize_vrm_avatar`, and `setup_vrm_expressions`
— none matched anything real.

## VRM Format Overview

**VRM** (Virtual Reality Model) - Japanese standard for 3D avatars in VR/AR.

### VRM Features
- Humanoid rig (standardized bones)
- Blend shapes (facial expressions)
- Spring bones (hair/cloth physics)
- Metadata (author, license, usage rights)
- First Person view settings
- Texture/material definitions

## VRM Import Workflow

### Step 1: Import VRM
```python
unity_avatar(
    operation="import_vrm",
    vrm_path="D:/Avatars/character.vrm",
    project_path="D:/Projects/MyGame",
    optimize_for_vrchat=True,
    create_prefab=True
)
```
Real — copies the VRM into `Assets/Models/` and creates a prefab
reference. There is no `import_settings` dict with granular
`extract_textures`/`extract_materials` flags; the two real knobs are
`optimize_for_vrchat` and `create_prefab`.

⚠️ When `optimize_for_vrchat=True`, the response includes a
`vrchat_optimizations` report — **this is currently a hardcoded
placeholder dict** (fixed strings like "Standard to VRChat compatible"),
not a computed result from the actual model. It does not really convert
shaders or add SDK components yet. Flagged in `TODO.md`.

### Step 2: Validation
```python
unity_validation(
    operation="validate_model",
    model_path="D:/Avatars/character.vrm",
    target_platform="vrchat"
)
```
Real, works directly on the model file (doesn't require an imported
Unity project). For a project-context avatar check instead, use
`vrchat(operation="validate_avatar", avatar_prefab="...", project_path="...")`.

### Step 3: Optimization
**No dedicated `optimize_vrm_avatar` tool exists.** The closest real
pieces:
```python
unity_asset(operation="optimize_textures")
unity_validation(operation="check_polycount", model_path="...")
unity_validation(operation="check_materials", model_path="...")
```
There is no automated polygon decimation, blend-shape cleanup, or bone
reduction tool — those remain manual Unity/Blender tasks.

## VRChat Avatar Optimization

### Performance Targets
Reference only (check against them with `unity_validation`'s operations
above, or manually):
```
VRChat Ranks (Quest-compatible):
Excellent: < 7,500 tris, < 10 mats, < 10 MB tex
Good: < 10,000 tris, < 8 mats, < 40 MB tex
Medium: < 15,000 tris, < 16 mats, < 40 MB tex

PC-Only (higher limits):
Good: < 32,000 tris, < 16 mats, < 80 MB tex
Medium: < 70,000 tris, < 24 mats, < 150 MB tex
```

### Optimization Techniques
Manual guidance, not automated by any tool here beyond
`unity_asset(operation="optimize_textures")`:
```
Polygon reduction:
- Decimate modifier (reduce tris)
- Remove hidden geometry
- Optimize body (hidden by clothes)
- LOD system (if supported)

Texture optimization:
- Compress textures (DXT5, BC7)
- Reduce resolution (4K to 2K to 1K)
- Atlas textures (combine multiple)
- Remove alpha channel if unused

Material merging:
- Combine similar materials
- Texture atlasing
- Share textures between materials
- Remove unused materials
```

### Expression Setup
**No `setup_vrm_expressions` tool, or any equivalent, exists.** VRM blend
shape clip setup (facial expressions, eye blinks, mouth shapes, custom
expressions) is not automatable through this server — manual in Unity or
the original VRM authoring tool.

---

**Austrian VRM**: Optimized, compatible, expressive! 🇦🇹👤
