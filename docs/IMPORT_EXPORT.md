# Import / Export Formats & Fleet Mesh Paths

Unity3D-MCP bridges between Unity and the rest of the fleet — Gazebo simulation, FreeCAD CAD models, Resonite VR, Blender scenes, and World Labs AI worlds. Each source speaks a different 3D format.

## Available formats

| Format | Full name | Read | Write | Best for |
|--------|-----------|------|-------|----------|
| **FBX** | Autodesk Filmbox | ✅ | ✅ | Full scene exchange (animation, rigging, materials) |
| **glTF** | GL Transmission Format | ✅ | ✅ | Web, mobile, Resonite, compact delivery |
| **GLB** | glTF Binary | ✅ | ✅ | Single-file variant of glTF |
| **OBJ** | Wavefront Object | ✅ | ❌ | Universal mesh exchange, no animation |
| **STL** | Stereolithography | ✅ | ❌ | 3D printing, CAD exchange |
| **STEP** | ISO 10303 STEP | ✅ | ❌ | Engineering CAD, FreeCAD export |
| **VRM** | VRM (VRM Consortium) | ✅ | ❌ | VR avatars, Resonite humanoids |
| **UnityPackage** | .unitypackage | ✅ | ✅ | Sharing Unity assets internally |

## Fleet mesh import paths

Each fleet repo exports models in a format Unity can ingest. The REST endpoints auto-detect format from the file extension.

```
Source        ➤  Format        ➤  REST endpoint              ➤  Unity
──────────────    ────────────     ─────────────────────────      ─────
Gazebo sim       FBX, OBJ         POST /api/v1/gazebo/import     Scene rendering
FreeCAD          STEP, STL, OBJ   POST /api/v1/freecad/import    CAD visualization
Resonite VR      VRM, GLB         POST /api/v1/resonite/import   VR avatars, worlds
Blender          FBX, GLTF, OBJ   POST /api/v1/blender/import    3D models, scenes
World Labs       OBJ, FBX, GLB    POST /api/v1/worldlabs/import  AI-generated worlds
Generic          any              POST /api/v1/import/model      Any source
```

## Fleet mesh export paths

```
Unity object    ➤  Format        ➤  REST endpoint              ➤  Destination
──────────────      ────────────     ─────────────────────────      ────────────
Unity GameObject   FBX              POST /api/v1/export/fbx       Blender, Gazebo, any
Unity GameObject   glTF/GLB         POST /api/v1/export/gltf      Web, Resonite, mobile
```

## REST endpoint reference

### Import endpoints (all use the same request body)

```json
POST /api/v1/{source}/import
{
  "models": ["model1", "model2"],
  "file_path": "optional/path/{model}.fbx"
}
```

If `file_path` is omitted, Unity3D-MCP looks for the model at `{source}_models/{model}.fbx`. If the file doesn't exist, it tries common extensions: `.fbx`, `.obj`, `.gltf`, `.glb`, `.stl`, `.step`, `.vrm`.

### Export endpoints

```json
POST /api/v1/export/fbx
{
  "name": "MyModel",
  "output_path": "exports/MyModel.fbx"
}
```

```json
POST /api/v1/export/gltf
{
  "name": "MyModel",
  "output_path": "exports/MyModel.glb"
}
```

## MCP tools

Same operations available as MCP tools for AI agent use:

| MCP Tool | Purpose |
|----------|---------|
| `import_3d_model` | Import any 3D model file into Unity |
| `import_asset_package` | Import .unitypackage |
| `export_fbx` | Export Unity objects to FBX |
| `export_gltf` | Export Unity objects to glTF/GLB |

## When to use which format

| You want to... | Use | Because |
|----------------|-----|---------|
| Exchange full scenes with Blender | **FBX** | Preserves rigging, animation, cameras, lights |
| Put a model on the web | **glTF** | Tiny files, browser-native, PBR materials |
| Import into Resonite VR | **glTF/GLB** | Resonite's native 3D format |
| Send to a 3D printer | **STL** | Industry standard for printing |
| Exchange with FreeCAD | **STEP** | Engineering-grade CAD exchange |
| Upload a humanoid avatar | **VRM** | Standard VR avatar format |
| Share Unity assets internally | **UnityPackage** | Preserves all Unity metadata |
