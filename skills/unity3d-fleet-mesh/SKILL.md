# Unity3D Fleet Mesh — Skill Guide

You have access to **unity3d-mcp**, a FastMCP 3.2 server that bridges Unity 3D to the fleet mesh. This guide covers how to use the import/export pipeline across formats and connected repos.

---

## Quick reference

Unity3D-MCP sits at the center of the fleet visualization layer:

```
Gazebo (physics) ──FBX──▶  │        │──FBX──▶ Blender (modelling)
FreeCAD (CAD)    ──STEP─▶  │ Unity  │──FBX──▶ Gazebo (sim mesh)
Resonite (VR)    ──GLB──▶  │  3D    │──glTF─▶ Web/mobile
Blender (scenes) ──FBX──▶  │  MCP   │──glTF─▶ Resonite VR
World Labs (AI)  ──OBJ──▶  │        │
```

## Import pipeline

Every import endpoint accepts the same body:
```json
{"models": ["name1", "name2"], "file_path": "optional/path/{model}.fbx"}
```

If no `file_path` is given, the server searches `{source}_models/{model}` with extensions `.fbx`, `.obj`, `.gltf`, `.glb`, `.stl`, `.step`, `.vrm`.

### From Gazebo (POST /api/v1/gazebo/import)

Gazebo exports robot models and environment meshes as FBX. Typical workflow:

1. `gz_sim_state()` to list models in the simulation
2. Run the simulation — let the robot drive around
3. Export the scene from Gazebo: `gz topic -t /world/scene --msgtype gz.msgs.Scene --reptype gz.msgs.Scene --reqtype gz.msgs.Empty --req "" --timeout 2000`
4. Import into Unity via this endpoint
5. The imported model appears in the Unity scene immediately

**Use case**: Visualizing a Gazebo robot simulation in high-fidelity Unity rendering. Camera paths, lighting, materials all look better in Unity than in Gazebo's default viewport.

### From FreeCAD (POST /api/v1/freecad/import)

FreeCAD exports mechanical parts as STEP or STL. Typical workflow:

1. Design a part in FreeCAD (or via freecad-mcp)
2. Export as STEP (preferred) or STL
3. Import into Unity via this endpoint
4. The part appears as a Unity mesh with correct scale

**Use case**: Robot parts designed in CAD appear in the Unity scene alongside the simulated robot from Gazebo. Validate fit and form before 3D printing.

### From Resonite (POST /api/v1/resonite/import)

Resonite exports avatars as VRM and worlds as GLB. Typical workflow:

1. Build a world or avatar in Resonite VR
2. Export as VRM (avatar) or GLB (world)
3. Import into Unity via this endpoint
4. The VRM avatar appears with rigging; the GLB world appears as a scene

**Use case**: VR-designed content from Resonite flows into Unity for higher-fidelity rendering or combined scenes.

### From Blender (POST /api/v1/blender/import)

Blender exports scenes as FBX or GLTF. Typical workflow:

1. Model in Blender (or via blender-mcp)
2. Export as FBX (for animation/rigging) or GLTF (for web/Resonite)
3. Import into Unity via this endpoint

### From World Labs (POST /api/v1/worldlabs/import)

World Labs Marble generates OBJ/FBX/GLB worlds from text prompts. Typical workflow:

1. Generate a world via worldlabs-mcp
2. Download the export files
3. Import into Unity via this endpoint

## Export pipeline

### To FBX (POST /api/v1/export/fbx)

Best for: Blender, Gazebo, FreeCAD, any traditional 3D app.

Preserves: Hierarchy, transforms, materials, animation (Unity Animator Controller paths).

```json
{"name": "MyModel", "output_path": "exports/MyModel.fbx"}
```

### To glTF (POST /api/v1/export/gltf)

Best for: Web (Three.js, react-three-fiber), mobile apps, Resonite VR.

glTF is the "JPEG of 3D" — compact, PBR materials, no proprietary licensing. The GLB variant (single binary file) is especially convenient.

```json
{"name": "MyModel", "output_path": "exports/MyModel.glb"}
```

**When to use glTF vs FBX:**

| Factor | FBX | glTF |
|--------|-----|------|
| File size | Large | Small (often 10x smaller) |
| Animation | Full (bones, blendshapes) | Full |
| Materials | Standard Unity | PBR (metalness/roughness) |
| Open standard | No (Autodesk) | Yes (Khronos) |
| Browser/web | Requires converter | Native support |
| Resonite VR | Requires converter | Native (.glb) |
| Unity import | Native | Native (2020+) |

## Format guide

| Extension | Format | Can read | Can write | Animations | Use when |
|-----------|--------|----------|-----------|------------|----------|
| `.fbx` | Autodesk FBX | ✅ | ✅ | ✅ | Full scene exchange with Blender/Gazebo |
| `.gltf`/`.glb` | glTF / GLB | ✅ | ✅ | ✅ | Web, mobile, Resonite, delivery |
| `.obj` | Wavefront OBJ | ✅ | ❌ | ❌ | Universal fallback, no animation needed |
| `.stl` | Stereolithography | ✅ | ❌ | ❌ | 3D printing |
| `.step`/`.stp` | ISO 10303 STEP | ✅ | ❌ | ❌ | Engineering CAD, FreeCAD exchange |
| `.vrm` | VRM avatar | ✅ | ❌ | ✅ | Humanoid avatars for Resonite/VRChat |
| `.unitypackage` | Unity package | ✅ | ✅ | ✅ | Internal Unity asset sharing |

## Fleet mesh workflows

### Simulation-to-visualization (Gazebo → Unity)

```
gz_sim_state() → identify models
gz_topic_pub() → run simulation, export frames
POST /api/v1/gazebo/import → import models into Unity
```

### CAD-to-simulation (FreeCAD → Unity → Gazebo)

```
freecad-mcp export → STEP file
POST /api/v1/freecad/import → import into Unity for visualization
Validate fit and form in rendered scene
Export back to FBX → Gazebo for physics
```

### VR-to-render (Resonite → Unity → web)

```
resonite-mcp export → GLB/VRM
POST /api/v1/resonite/import → import into Unity
Add lighting, materials, post-processing in Unity
POST /api/v1/export/gltf → export for web delivery
```

### AI-worlds-to-scene (World Labs → Unity)

```
worldlabs-mcp generate → OBJ/FBX files
POST /api/v1/worldlabs/import → import into Unity scene
Composite with other elements (robots from Gazebo, parts from FreeCAD)
```

## Common issues

- **"Model file not found"** — File path is wrong or the format isn't supported. Check `file_path` ends with a known extension. Use `/import/model` for auto-detection.
- **"FBX with animation not importing"** — Unity FBX import might strip animation if the exporter settings don't include `include_animation`. Use glTF for simpler animation transfer.
- **"glTF looks different in Unity vs source"** — Unity imports glTF materials as Standard (Metallic) by default. If source uses different PBR parameters, materials may shift slightly. This is expected.
- **"VRM avatar losing rigging"** — Ensure the VRM file is standard VRM 0.x or 1.0. Non-standard or damaged VRMs may import as static meshes.
