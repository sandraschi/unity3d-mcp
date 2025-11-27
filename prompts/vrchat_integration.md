# VRChat Integration - Unity3D-MCP

## VRChat SDK Setup

### SDK Installation
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

### VRC Avatar Descriptor
```python
setup_vrchat_avatar(
    avatar_root="Character",
    view_position=(0, 1.6, 0),  # Eye height
    avatar_name="My Avatar",
    description="Custom VRChat avatar"
)

Descriptor configures:
- View position (first-person camera)
- Animation layers (base, additive, gesture, action, FX)
- Expression parameters
- Expression menu
- Playable layers
- Lip sync mode
```

### Expression Parameters
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
```python
create_expression_menu(
    name="Main Menu",
    controls=[
        {"name": "Smile", "type": "Toggle", "parameter": "Smile"},
        {"name": "Hat", "type": "Toggle", "parameter": "HatEnabled"},
        {"name": "Ear Rotation", "type": "RadialPuppet", "parameter": "EarRotate"}
    ]
)

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
validate_vrchat_avatar(avatar_name="Character")

Checks:
- VRC Avatar Descriptor present
- View position set
- Performance rank (Poor blocks Quest upload)
- Missing scripts (not allowed in VRChat)
- Shader compatibility (VRChat-approved shaders)
- Animation override controllers valid
- Expression parameters within limits (16 bools, 16 ints, 16 floats)
```

### Upload to VRChat
```python
upload_vrchat_avatar(
    avatar_name="Character",
    thumbnail_camera="Front",
    visibility="private"  # or "public"
)

Process:
1. Build avatar asset bundle
2. Generate thumbnail
3. Upload to VRChat servers
4. Set visibility and tags
5. Verify upload successful
6. Test in VRChat client
```

---

**Austrian VRChat**: Optimized, expressive, community-ready! 🇦🇹🌐

