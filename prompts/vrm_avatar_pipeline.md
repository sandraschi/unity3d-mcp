# VRM Avatar Pipeline - Unity3D-MCP

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
import_vrm(
    vrm_path="D:/Avatars/character.vrm",
    import_settings={
        "extract_textures": True,
        "extract_materials": True,
        "generate_prefab": True
    }
)

Creates:
- Model in scene
- Textures in folder
- Materials
- Prefab for reuse
```

### Step 2: Validation
```python
validate_vrm_avatar(avatar_name="Character")

Checks:
- Humanoid rig correct
- Blend shapes present
- Bone structure valid
- Materials assigned
- Textures loaded
```

### Step 3: Optimization
```python
optimize_vrm_avatar(
    avatar_name="Character",
    target_platform="VRChat",
    performance_rank="Good"
)

Optimizations:
- Polygon reduction (decimation)
- Texture compression
- Material merging (atlasing)
- Blend shape cleanup (remove unused)
- Bone reduction (if possible)
```

## VRChat Avatar Optimization

### Performance Targets
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
```
Polygon reduction:
- Decimate modifier (reduce tris)
- Remove hidden geometry
- Optimize body (hidden by clothes)
- LOD system (if supported)

Texture optimization:
- Compress textures (DXT5, BC7)
- Reduce resolution (4K → 2K → 1K)
- Atlas textures (combine multiple)
- Remove alpha channel if unused

Material merging:
- Combine similar materials
- Texture atlasing
- Share textures between materials
- Remove unused materials
```

### Expression Setup
```python
# Setup facial expressions
setup_vrm_expressions(
    avatar_name="Character",
    expressions=[
        "Neutral", "Joy", "Angry", "Sorrow",
        "Fun", "Blink_L", "Blink_R", "Blink"
    ]
)

VRM blend shape clips:
- Facial expressions (joy, angry, etc.)
- Eye blinks
- Mouth shapes (A, I, U, E, O)
- Custom expressions
```

---

**Austrian VRM**: Optimized, compatible, expressive! 🇦🇹👤

