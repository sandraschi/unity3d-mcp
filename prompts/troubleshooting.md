# Troubleshooting - Unity3D-MCP

## Unity Editor Issues

### Problem: Unity Won't Launch
```
Solutions:
1. Check Unity Hub shows installation
2. Verify correct Unity version
3. Check license activation
4. Clear Unity cache (AppData)
5. Reinstall Unity if corrupted
```

### Problem: Project Won't Open
```
Causes:
- Wrong Unity version
- Corrupted project files
- Missing dependencies
- Library folder issues

Solutions:
- Open with correct Unity version
- Delete Library folder (regenerates)
- Check for error logs (Editor.log)
- Restore from backup
```

## VRM Issues

### Problem: VRM Won't Import
```
Solutions:
- Install UniVRM package
- Check VRM file valid (test in VRM viewer)
- Unity version compatible with UniVRM
- Import errors in console (read carefully)
```

### Problem: Avatar Broken After Import
```
Common issues:
- Missing textures (check paths)
- Shader not supported
- Bone mapping incorrect
- Blend shapes missing

Fixes:
- Re-import with correct settings
- Assign missing textures manually
- Convert shaders to Unity Standard
- Check VRM in original application
```

## VRChat Issues

### Problem: Avatar Won't Upload
```
Checklist:
- VRChat SDK installed correctly
- Logged into VRChat in Unity
- Avatar Descriptor configured
- Performance not "Very Poor"
- No prohibited components/scripts
- Blueprint ID set (for updates)
```

### Problem: Avatar Ranked "Poor"
```
Too many:
- Triangles: Decimate mesh
- Materials: Merge/atlas
- Texture memory: Compress, reduce size
- Mesh count: Combine meshes
- Blend shapes: Remove unused

Use profiler to identify bottlenecks
```

---

## Build Issues

### Problem: Build Fails
```
Common causes:
- Compilation errors (fix code first!)
- Missing assets
- Incompatible plugins
- Insufficient disk space

Check: Console for errors before building
```

### Problem: Build Crashes on Run
```
Debug:
- Development build (easier debugging)
- Check Player log (Player.log)
- Test in Editor first
- Platform-specific issues (test on target)
```

---

**Austrian Debugging**: Systematic, thorough, solution-focused! 🇦🇹🔧

