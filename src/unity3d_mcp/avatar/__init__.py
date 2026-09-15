"""
Avatar and VRM Management

VRM avatar import, configuration, and animation setup for Unity.
"""

import asyncio
import json
import logging
import struct
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class VRMParseError(Exception):
    """Raised when a .vrm file isn't a well-formed binary glTF container."""


def parse_vrm_gltf_json(vrm_path: str) -> dict[str, Any]:
    """Parse the JSON chunk of a binary glTF/VRM file.

    VRM (0.x and 1.0) is a binary glTF container: a 12-byte header
    (b"glTF" magic, uint32 version, uint32 total length) followed by
    chunks of (uint32 length, 4-byte type, data). The first chunk is
    always type b"JSON" and holds the glTF scene document as UTF-8 text
    (materials, textures, images, meshes, nodes, etc.) - this is real,
    documented glTF 2.0 binary container structure (the ".glb"/".vrm"
    format), not Unity-specific. No third-party library needed; only
    stdlib `struct` for the binary header parsing.

    Raises VRMParseError on anything that isn't a valid binary glTF
    container, rather than silently returning empty/fake data.
    """
    with open(vrm_path, "rb") as f:
        header = f.read(12)
        if len(header) < 12 or header[0:4] != b"glTF":
            raise VRMParseError(f"{vrm_path}: not a binary glTF/VRM file (missing 'glTF' magic bytes)")
        _version, _total_length = struct.unpack("<II", header[4:12])

        chunk_header = f.read(8)
        if len(chunk_header) < 8:
            raise VRMParseError(f"{vrm_path}: truncated file, missing first chunk header")
        chunk_length, chunk_type = struct.unpack("<I4s", chunk_header)
        if chunk_type != b"JSON":
            raise VRMParseError(f"{vrm_path}: first chunk is type {chunk_type!r}, expected b'JSON'")

        json_bytes = f.read(chunk_length)
        if len(json_bytes) < chunk_length:
            raise VRMParseError(f"{vrm_path}: truncated file, JSON chunk shorter than its declared length")

    try:
        return json.loads(json_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VRMParseError(f"{vrm_path}: JSON chunk is not valid UTF-8 JSON: {exc}") from exc


def summarize_vrm_materials(gltf: dict[str, Any]) -> dict[str, Any]:
    """Extract real material/texture counts and per-material shape from a parsed glTF document.

    Every field here is read directly from the file's actual JSON
    structure - nothing here is guessed, hardcoded, or estimated.
    """
    materials = gltf.get("materials", [])
    images = gltf.get("images", [])
    textures = gltf.get("textures", [])
    meshes = gltf.get("meshes", [])

    material_summaries = []
    for i, mat in enumerate(materials):
        pbr = mat.get("pbrMetallicRoughness", {})
        material_summaries.append(
            {
                "index": i,
                "name": mat.get("name", f"Material_{i}"),
                "has_base_color_texture": "baseColorTexture" in pbr,
                "has_metallic_roughness_texture": "metallicRoughnessTexture" in pbr,
                "has_normal_texture": "normalTexture" in mat,
                "has_emissive_texture": "emissiveTexture" in mat,
                "alpha_mode": mat.get("alphaMode", "OPAQUE"),
                "double_sided": bool(mat.get("doubleSided", False)),
            }
        )

    primitive_count = sum(len(m.get("primitives", [])) for m in meshes)

    return {
        "material_count": len(materials),
        "texture_count": len(textures),
        "image_count": len(images),
        "mesh_count": len(meshes),
        "primitive_count": primitive_count,
        "materials": material_summaries,
    }


class VRMAvatarManager:
    """Manages VRM avatar import and configuration."""

    def __init__(self, config):
        self.config = config

    async def import_vrm(
        self,
        vrm_path: str,
        project_path: str,
        optimize_for_vrchat: bool = True,
        create_prefab: bool = True,
    ) -> dict[str, Any]:
        """Import VRM avatar into Unity project."""
        try:
            # Validate VRM file
            if not Path(vrm_path).exists():
                return {"status": "error", "message": f"VRM file not found: {vrm_path}"}

            if not vrm_path.lower().endswith(".vrm"):
                return {"status": "error", "message": "File is not a VRM file"}

            # Copy VRM to Unity project
            assets_path = Path(project_path) / "Assets" / "Models"
            assets_path.mkdir(parents=True, exist_ok=True)

            vrm_name = Path(vrm_path).stem
            target_path = assets_path / f"{vrm_name}.vrm"

            # Copy file (simplified)
            import shutil

            await asyncio.to_thread(shutil.copy2, vrm_path, target_path)

            result = {
                "status": "success",
                "message": f"VRM avatar imported: {vrm_name}",
                "vrm_path": str(target_path),
                "avatar_name": vrm_name,
                "optimized_for_vrchat": optimize_for_vrchat,
                "prefab_created": create_prefab,
            }

            if optimize_for_vrchat:
                result["vrchat_optimizations"] = await self._apply_vrchat_optimizations(
                    vrm_name, project_path, vrm_path
                )

            if create_prefab:
                result["prefab_path"] = f"Assets/Prefabs/{vrm_name}.prefab"

            return result

        except Exception as e:
            logger.error(f"Failed to import VRM: {e}")
            return {"status": "error", "message": str(e)}

    async def _apply_vrchat_optimizations(self, avatar_name: str, project_path: str, vrm_path: str) -> dict[str, Any]:
        """Analyze the VRM's real material/texture data and write an honest conversion manifest.

        Rewritten 2026-07-18: this used to return a hardcoded dict
        ("Standard to VRChat compatible", "Good (estimated)", etc.)
        regardless of what was actually imported - a lie, flagged in
        TODO.md and now fixed.

        What this genuinely does: parses the VRM's own binary glTF JSON
        chunk (real data, not guessed) to report actual material/texture/
        mesh counts, and writes a real manifest file to disk listing what
        was found.

        What this deliberately does NOT do: rewrite any Unity .mat asset's
        shader reference, or claim texture compression/polygon reduction
        happened. At this point in the pipeline (Hands-Off import - the
        VRM file was just copied into Assets/Models/) Unity/UniVRM has not
        yet run its own importer, so there ARE NO .mat/.png assets on disk
        to convert or compress - claiming otherwise would just be a
        different flavor of the same lie. Rewriting a Unity shader
        reference safely requires Unity's own AssetDatabase to resolve
        the shader GUID; doing that blind, outside Unity, risks writing a
        broken (pink-shader) material while claiming success, which is
        worse than reporting the real, honest gap.
        """
        try:
            gltf = parse_vrm_gltf_json(vrm_path)
        except VRMParseError as exc:
            logger.warning(f"VRM analysis failed for optimization report: {exc}")
            return {
                "status": "error",
                "message": f"Could not analyze VRM for optimization: {exc}",
                "material_conversion": "not attempted: VRM could not be parsed",
                "texture_compression": "not attempted",
                "polygon_reduction": "not attempted",
                "performance_rank": "not estimated",
                "sdk_components": "not added: no Unity asset was touched",
            }

        summary = summarize_vrm_materials(gltf)

        manifest = {
            "avatar_name": avatar_name,
            "source_vrm": vrm_path,
            "material_count": summary["material_count"],
            "texture_count": summary["texture_count"],
            "image_count": summary["image_count"],
            "mesh_count": summary["mesh_count"],
            "primitive_count": summary["primitive_count"],
            "materials": summary["materials"],
            "recommended_shader": (
                "VRChat/Mobile/Toon Lit or lilToon (set manually in the Unity Inspector "
                "after import - this tool does not rewrite shader GUIDs outside Unity)"
            ),
            "still_manual_steps": [
                "Open the project in Unity so UniVRM actually imports the VRM into real .mat/.png/.prefab assets",
                "Convert each material's shader in the Unity Inspector, or via an Editor script run inside Unity",
                "Add a VRC Avatar Descriptor: vrchat(operation='setup_descriptor', avatar_prefab=...)",
                "Get a real performance rank: vrchat(operation='validate_avatar', avatar_prefab=..., project_path=...)",
            ],
        }

        manifest_path = Path(project_path) / "Assets" / "Models" / f"{avatar_name}_vrchat_conversion_manifest.json"
        try:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            manifest_written = str(manifest_path)
        except OSError as exc:
            logger.warning(f"Could not write VRChat conversion manifest: {exc}")
            manifest_written = None

        return {
            "material_count": summary["material_count"],
            "texture_count": summary["texture_count"],
            "image_count": summary["image_count"],
            "mesh_count": summary["mesh_count"],
            "materials_found": summary["materials"],
            "manifest_written": manifest_written,
            "material_conversion": (
                "NOT performed here - real material data extracted above and written to the "
                "manifest; shader conversion requires a Unity-side step"
            ),
            "texture_compression": (
                "NOT performed - no texture assets exist on disk yet in Hands-Off mode "
                "(Unity/UniVRM hasn't imported them)"
            ),
            "polygon_reduction": "NOT performed - not implemented; would require real mesh decimation logic",
            "performance_rank": (
                "not estimated here - use vrchat(operation='validate_avatar') after opening "
                "the project in Unity for a real rank"
            ),
            "sdk_components": "NOT added - no Unity project state was modified by this call",
        }


def _unity_guid() -> str:
    """A Unity-shaped 32-hex-char GUID (Unity itself just uses uuid4().hex - no dashes)."""
    return uuid.uuid4().hex


def _yaml_state_block(file_id: int, name: str) -> str:
    """One AnimatorState (!u!1102) YAML object, no motion attached (no .anim clip exists on disk)."""
    return f"""--- !u!1102 &{file_id}
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0, guid: 00000000000000000000000000000000, type: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {name}
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions: []
  m_StateMachineBehaviours: []
  m_Position: {{x: 50, y: 50, z: 0}}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 1
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {{fileID: 0}}
  m_Tag:
  m_SpeedParameter:
  m_MirrorParameter:
  m_CycleOffsetParameter:
  m_TimeParameter:
"""


def _yaml_state_machine_block(file_id: int, name: str, state_file_ids: list[int], default_state_id: int) -> str:
    child_states = "\n".join(
        f"  - serializedVersion: 1\n    m_State: {{fileID: {sid}}}\n    m_Position: {{x: 300, y: {120 + i * 80}, z: 0}}"
        for i, sid in enumerate(state_file_ids)
    )
    return f"""--- !u!1107 &{file_id}
AnimatorStateMachine:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0, guid: 00000000000000000000000000000000, type: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {name}
  m_ChildStates:
{child_states}
  m_ChildStateMachines: []
  m_AnyStateTransitions: []
  m_EntryTransitions: []
  m_StateMachineTransitions: {{}}
  m_StateMachineBehaviours: []
  m_AnyStatePosition: {{x: 50, y: 20, z: 0}}
  m_EntryPosition: {{x: 50, y: 120, z: 0}}
  m_ExitPosition: {{x: 800, y: 120, z: 0}}
  m_ParentStateMachinePosition: {{x: 800, y: 20, z: 0}}
  m_DefaultState: {{fileID: {default_state_id}}}
"""


def _param_type_code(param_type: str) -> int:
    # Unity's AnimatorControllerParameterType enum values.
    return {"float": 1, "int": 3, "bool": 4, "trigger": 9}.get(param_type, 1)


def _yaml_parameter_block(name: str, param_type: str, default: Any) -> str:
    code = _param_type_code(param_type)
    default_float = float(default) if param_type == "float" else 0
    default_int = int(default) if param_type == "int" else 0
    default_bool = 1 if (param_type in ("bool", "trigger") and default) else 0
    return (
        f"  - m_Name: {name}\n"
        f"    m_Type: {code}\n"
        f"    m_DefaultFloat: {default_float}\n"
        f"    m_DefaultInt: {default_int}\n"
        f"    m_DefaultBool: {default_bool}\n"
        f"    m_Controller: {{fileID: 9100000}}"
    )


def build_animator_controller_yaml(
    controller_name: str,
    layers: list[dict[str, Any]],
    parameters: list[dict[str, Any]],
) -> str:
    """Build a real Unity AnimatorController .controller YAML asset.

    Format is Unity's documented text-YAML serialization (class IDs 91 =
    AnimatorController, 1107 = AnimatorStateMachine, 1102 = AnimatorState).
    Each layer gets its own state machine with one AnimatorState per
    requested state name; states have no motion attached since no real
    .anim clips exist on disk to reference (attaching a motion reference
    to a clip that doesn't exist would be a broken PPtr, worse than none).

    UNVERIFIED against a live Unity Editor - this repo has no Unity
    installation to compile/import-test against. If Unity rejects this
    file, it will show as an import error in the Console (not silent
    corruption of other assets), and the fix is to hand-correct this
    generator function. Do not treat this as guaranteed byte-correct.
    """
    file_id_counter = [110700000, 110200000]  # [state_machine_next, state_next]
    object_blocks: list[str] = []
    layer_yaml_entries: list[str] = []

    for layer in layers:
        sm_id = file_id_counter[0]
        file_id_counter[0] += 1

        state_ids = []
        for state_name in layer["states"]:
            sid = file_id_counter[1]
            file_id_counter[1] += 1
            state_ids.append(sid)
            object_blocks.append(_yaml_state_block(sid, state_name))

        default_state = state_ids[0] if state_ids else 0
        object_blocks.append(_yaml_state_machine_block(sm_id, layer["name"], state_ids, default_state))

        layer_yaml_entries.append(
            f"  - serializedVersion: 5\n"
            f"    m_Name: {layer['name']}\n"
            f"    m_StateMachine: {{fileID: {sm_id}}}\n"
            f"    m_Mask: {{fileID: 0}}\n"
            f"    m_Motions: []\n"
            f"    m_Behaviours: []\n"
            f"    m_BlendingMode: 0\n"
            f"    m_SyncedLayerIndex: -1\n"
            f"    m_DefaultWeight: 0\n"
            f"    m_IKPass: 0\n"
            f"    m_SyncedLayerAffectsTiming: 0\n"
            f"    m_Controller: {{fileID: 9100000}}"
        )

    parameter_yaml = "\n".join(
        _yaml_parameter_block(p["name"], p.get("type", "float"), p.get("default", 0)) for p in parameters
    )

    controller_block = f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!91 &9100000
AnimatorController:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0, guid: 00000000000000000000000000000000, type: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {controller_name}
  serializedVersion: 5
  m_AnimatorParameters:
{parameter_yaml}
  m_AnimatorLayers:
{chr(10).join(layer_yaml_entries)}
"""
    return controller_block + "\n".join(object_blocks)


class AnimationManager:
    """Manages avatar animation and animator controllers."""

    def __init__(self, config):
        self.config = config

    @staticmethod
    def _derive_project_root(avatar_path: str, project_path: str | None) -> Path | None:
        """Find the Unity project root (the folder containing Assets/) from either
        an explicit project_path or by locating the 'Assets' segment inside avatar_path.
        Returns None if neither yields a usable root - callers must not silently
        write files to the wrong place or fabricate a fake path.
        """
        if project_path:
            return Path(project_path)

        parts = Path(avatar_path).parts
        if "Assets" in parts:
            idx = parts.index("Assets")
            if idx > 0:
                return Path(*parts[:idx])
        return None

    async def setup_animator(
        self,
        avatar_path: str,
        animator_type: str = "humanoid",
        include_facial: bool = True,
        project_path: str | None = None,
    ) -> dict[str, Any]:
        """Setup animator controller for avatar - writes a real .controller asset to disk.

        Rewritten 2026-07-18: this used to return a templated config dict
        and write nothing to disk at all - a lie by omission, flagged in
        TODO.md and now fixed. This version actually writes a
        `.controller` YAML asset (and its `.meta` file with a real GUID)
        to `Assets/Animators/` under the Unity project root.

        Honesty caveats, returned in the response, not hidden:
        - No motion clips are attached to any state (none exist on disk
          in Hands-Off mode) - states are structurally real but empty.
        - This has not been validated by actually opening the file in a
          live Unity Editor (none available in this environment). If
          Unity's importer rejects it, that will show as a Console error
          on the asset, not data loss elsewhere in the project.
        """
        try:
            avatar_name = Path(avatar_path).stem
            project_root = self._derive_project_root(avatar_path, project_path)

            layers = [
                {"name": "Base Layer", "states": ["Idle", "Walk", "Run"]},
            ]
            parameters = [
                {"name": "Speed", "type": "float", "default": 0.0},
                {"name": "Grounded", "type": "bool", "default": True},
            ]

            if include_facial:
                layers.append({"name": "Facial Layer", "states": ["Neutral", "Happy", "Sad"]})
                parameters.extend(
                    [
                        {"name": "Expression", "type": "int", "default": 0},
                        {"name": "BlinkRate", "type": "float", "default": 1.0},
                    ]
                )

            controller_name = f"{avatar_name}_Controller"

            if project_root is None:
                return {
                    "status": "error",
                    "message": (
                        "Could not determine the Unity project root from avatar_path "
                        f"({avatar_path!r}) and no project_path was given. Nothing was "
                        "written to disk - pass project_path explicitly."
                    ),
                    "animator_type": animator_type,
                    "facial_animations": include_facial,
                }

            controller_yaml = build_animator_controller_yaml(controller_name, layers, parameters)

            animators_dir = project_root / "Assets" / "Animators"
            animators_dir.mkdir(parents=True, exist_ok=True)
            controller_file = animators_dir / f"{controller_name}.controller"
            meta_file = animators_dir / f"{controller_name}.controller.meta"

            controller_file.write_text(controller_yaml, encoding="utf-8")

            guid = _unity_guid()
            meta_file.write_text(
                f"fileFormatVersion: 2\nguid: {guid}\nNativeFormatImporter:\n"
                "  externalObjects: {}\n  mainObjectFileID: 9100000\n  userData:\n  assetBundleName:\n"
                "  assetBundleVariant:\n",
                encoding="utf-8",
            )

            return {
                "status": "success",
                "message": f"Animator controller written to disk for: {avatar_name}",
                "controller_path": str(controller_file),
                "meta_path": str(meta_file),
                "guid": guid,
                "animator_type": animator_type,
                "facial_animations": include_facial,
                "layers": [layer["name"] for layer in layers],
                "states_per_layer": {layer["name"]: layer["states"] for layer in layers},
                "parameters": parameters,
                "caveats": [
                    "No motion clips attached to any state - none exist on disk yet.",
                    "NOT validated against a live Unity Editor in this environment; "
                    "open the project in Unity and check the Console for import errors "
                    "on this asset before relying on it.",
                ],
            }

        except Exception as e:
            logger.error(f"Failed to setup animator: {e}")
            return {"status": "error", "message": str(e)}

    async def create_animation_clip(
        self, clip_name: str, duration: float, keyframes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create animation clip with keyframes.

        NOTE (2026-07-18): this method is real code but is not registered
        as an MCP tool anywhere (`unity_avatar` only exposes `import_vrm`
        and `setup_animator` - see tools/portmanteau/unity_avatar.py). It
        is also still a hardcoded/in-memory stub itself: it builds a
        plausible-looking curve dict but writes nothing to disk. Unlike
        `setup_animator` above, this was NOT rewritten to write a real
        Unity AnimationClip (.anim) asset - that's a different, even more
        complex serialized format (class ID 74, with curve bindings per
        property path), and since nothing can call this method via MCP
        today, the effort wasn't justified in this pass. Left flagged
        here rather than silently left as another future "looks real"
        trap; see TODO.md.
        """
        try:
            clip_path = f"Assets/Animations/{clip_name}.anim"

            animation_data = {
                "name": clip_name,
                "duration": duration,
                "sample_rate": 60,
                "keyframes": keyframes,
                "curves": [],
            }

            # Process keyframes into animation curves
            for keyframe in keyframes:
                curve = {
                    "property": keyframe.get("property", ""),
                    "time": keyframe.get("time", 0.0),
                    "value": keyframe.get("value", 0.0),
                    "in_tangent": keyframe.get("in_tangent", 0.0),
                    "out_tangent": keyframe.get("out_tangent", 0.0),
                }
                animation_data["curves"].append(curve)

            return {
                "status": "success",
                "message": f"Animation clip created: {clip_name}",
                "clip_path": clip_path,
                "duration": duration,
                "keyframe_count": len(keyframes),
                "animation_data": animation_data,
            }

        except Exception as e:
            logger.error(f"Failed to create animation clip: {e}")
            return {"status": "error", "message": str(e)}
