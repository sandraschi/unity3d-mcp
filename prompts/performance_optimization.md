# Performance Optimization - Unity3D-MCP

**Corrected 2026-07-18**: `profile_project()` (previously shown below) is
not a real tool — there is no FPS/CPU/GPU/draw-call profiler integration
anywhere in this server. The metrics-target guidance below is still
useful as a reference, but nothing here automates measuring them.

## Unity Performance Profiling

### Profiler Analysis
No automated profiler tool exists. Use the Unity Editor's built-in
Profiler window manually. Reference targets:
```
Key metrics:
- FPS (target: 60+ desktop, 90+ VR)
- CPU time (< 16ms per frame)
- GPU time (< 11ms for 90 FPS)
- Memory usage
- Draw calls (< 500 good, < 1000 acceptable)
- Batching effectiveness
```

The closest thing this server has to automated checks is
`unity_validation`:
```python
unity_validation(operation="check_polycount", model_path="...")
unity_validation(operation="check_materials", model_path="...")
unity_validation(operation="list_limits")
```
These check static model/material limits, not runtime FPS/CPU/GPU/draw
calls.

### Avatar Optimization
General reference guidance (manual, not automated by any tool here):
```
Triangle reduction:
- Decimate modifier
- Remove hidden geometry
- Optimize clothing layers
- Use LODs if supported

Texture optimization (unity_asset(operation="optimize_textures") does
part of this — real, but check its actual output against what you need):
- Compress (DXT5, BC7)
- Reduce resolution
- Atlas multiple textures
- Crunch compression

Material optimization (no automated tool for this):
- Merge materials
- Remove duplicate materials
- Use shader LOD
- Disable unused features
```

### Draw Call Reduction
Manual Unity Editor techniques, not automated here:
```
Batching strategies:
- Static batching (non-moving objects)
- Dynamic batching (small moving objects)
- GPU instancing (identical objects)
- Material sharing
```

## VRChat-Specific Optimization

### Quest Compatibility
Reference limits (check against them manually, or via
`unity_validation(operation="check_polycount"/"check_materials")`):
```
Quest requirements (strict):
- Max 7,500 triangles (Excellent)
- Max 10 materials
- Max 10 MB textures
- Mobile-compatible shaders
- No post-processing
- Optimized physics
```

### Shader Optimization
Reference only:
```
VRChat-approved shaders:
- Standard (basic, compatible)
- Toon (anime style)
- Poiyomi Toon (advanced, optimized)
- lilToon (feature-rich, performant)

Avoid:
- Compute shaders (not allowed)
- Tessellation (too expensive)
- Complex surface shaders (lag)
```

---

**Austrian Performance**: Every frame counts, every vertex optimized! 🇦🇹⚡
