# Performance Optimization - Unity3D-MCP

## Unity Performance Profiling

### Profiler Analysis
```python
profile_project()

Key metrics:
- FPS (target: 60+ desktop, 90+ VR)
- CPU time (< 16ms per frame)
- GPU time (< 11ms for 90 FPS)
- Memory usage
- Draw calls (< 500 good, < 1000 acceptable)
- Batching effectiveness
```

### Avatar Optimization
```
Triangle reduction:
- Decimate modifier
- Remove hidden geometry
- Optimize clothing layers
- Use LODs if supported

Texture optimization:
- Compress (DXT5, BC7)
- Reduce resolution
- Atlas multiple textures
- Crunch compression

Material optimization:
- Merge materials
- Remove duplicate materials
- Use shader LOD
- Disable unused features
```

### Draw Call Reduction
```
Batching strategies:
- Static batching (non-moving objects)
- Dynamic batching (small moving objects)
- GPU instancing (identical objects)
- Material sharing
```

## VRChat-Specific Optimization

### Quest Compatibility
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

