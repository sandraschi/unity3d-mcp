# Build & Deployment - Unity3D-MCP

## Multi-Platform Builds

### Windows Build
```python
build_windows(
    output_path="Builds/Windows/Game.exe",
    architecture="x86_64",  # or x86
    development=False,
    compression="LZ4"  # or None, LZMA
)

Build settings:
- Target: Windows (64-bit recommended)
- Scripting backend: IL2CPP or Mono
- API compatibility: .NET Standard 2.1
```

### Android Build (Quest)
```python
build_android(
    output_path="Builds/Android/game.apk",
    architecture="ARM64",
    min_sdk_version=26,  # Android 8.0
    target_sdk_version=32
)

Quest-specific:
- Architecture: ARM64 only
- Texture compression: ASTC
- Graphics API: OpenGLES3 or Vulkan
- Build for Android, install to Quest via SideQuest
```

### VRChat Avatar Build
```python
build_vrchat_avatar(
    avatar_name="Character",
    build_target="Windows",  # or Android for Quest
    output_folder="Builds/VRChat/"
)

Builds asset bundle, not standalone application
Automatically uploads if configured
```

---

## Build Optimization

### Compression Settings
```
None: Fastest build, largest size
LZ4: Fast decompression, medium size (recommended)
LZMA: Smallest size, slower loading
```

### Asset Bundling
```
Optimize:
- Include only used assets
- Compress textures
- Strip unused code
- Reduce shader variants
```

---

**Austrian Builds**: Fast, optimized, reliable! 🇦🇹📦

