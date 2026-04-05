# 🎭 Guide: VRM-to-VRChat Optimization Pipeline

Converting a `.vrm` avatar (common from VRoid Studio) to a VRChat-compliant model is a multi-step process that can be fully automated using Unity3D-MCP.

---

## 🛠️ Step 1: Import & Rigging

### Commands:
```python
# Import VRM file
import_vrm_avatar(vrm_path="C:/Avatars/MyAvatar.vrm")

# Setup rigged humanoid
setup_humanoid_rig(target="MyAvatar")
```

- **Logic**: The server uses the `UniVRM` package (auto-detected or installed via `install_univrm`) to process the `.vrm` binary into Unity assets (Prefabs, Meshes, Materials).

---

## 🛠️ Step 2: VRChat Shader Migration

VRChat requires specific shaders (e.g., `VRChat/Mobile/Standard Lite` or `VRChat/Shader Inventory`) for performance ranking. VRM files typically use `MToon`.

### Automation:
```python
# Optimize for VRChat
optimize_for_vrchat(avatar_root="Assets/Avatars/MyAvatar")
```

- **Action**: The server iterates through all materials in the avatar's folder and swaps `MToon` or `Standard` shaders with VRChat-compliant equivalents based on the target platform (PC vs Quest).

---

## 🛠️ Step 3: Performance Auditing

Before uploading, VRChat validates the polycount, material slots, and bone count.

### Commands:
```python
# Validate avatar
vrchat_validate_avatar(avatar_id="MyAvatar_GameObject")
```

- **Returns**: A detailed report on **Performance Rank** (Excellent, Good, Medium, Poor, Very Poor).

---

## 🛠️ Step 4: Final Build & Upload

### Automation:
```python
# Trigger upload
vrchat_upload_avatar(target="MyAvatar_GameObject")
```

- **Action**: The server triggers the VRChat SDK's `VRC_SdkControlPanel` methods to build the asset bundle and push it to the VRChat servers.

---

## 💎 Expert Tips

- **Texture Atlasing**: For "Quest" avatars, use the server's `atlas_textures` tool to combine multiple materials into a single draw call.
- **Dynamic Bones**: The server can automatically convert legacy Dynamic Bones to the new VRChat PhysBones format during optimization.
- **Blueprint ID**: Use `vrchat_assign_blueprint_id` to link the avatar to an existing ID on your VRChat account.
