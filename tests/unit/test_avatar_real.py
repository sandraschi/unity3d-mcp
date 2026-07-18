"""Unit tests for the real (non-mocked) avatar pipeline logic added 2026-07-18.

These replace two hardcoded/fake operations that used to lie about what
they did:
  - VRMAvatarManager._apply_vrchat_optimizations used to return a fixed
    dict regardless of input. It now parses the VRM's real binary glTF
    JSON chunk and reports real material/texture/mesh counts.
  - AnimationManager.setup_animator used to return an in-memory config
    dict and write nothing to disk. It now writes a real Unity
    AnimatorController YAML asset + .meta file.

Both are tested here against the real Nekomimi-chan.vrm fixture where
possible (skipped if that fixture is missing), plus synthetic-data tests
that don't depend on the fixture being present.
"""

from __future__ import annotations

import json
import struct

import pytest
from fixtures.factories import requires_vrm_file


def _make_minimal_glb(gltf_json: dict) -> bytes:
    """Build a minimal valid binary glTF (.glb/.vrm) container in memory,
    JSON chunk only, for tests that don't need the real fixture file.
    """
    json_bytes = json.dumps(gltf_json).encode("utf-8")
    # glTF binary chunks must be 4-byte aligned; pad with spaces.
    pad = (4 - len(json_bytes) % 4) % 4
    json_bytes += b" " * pad

    chunk_header = struct.pack("<I4s", len(json_bytes), b"JSON")
    total_length = 12 + 8 + len(json_bytes)
    header = struct.pack("<4sII", b"glTF", 2, total_length)
    return header + chunk_header + json_bytes


class TestParseVrmGltfJson:
    """Test the binary glTF/VRM parser against synthetic and real data."""

    def test_parses_minimal_synthetic_glb(self, tmp_path):
        from unity3d_mcp.avatar import parse_vrm_gltf_json

        gltf = {
            "asset": {"version": "2.0"},
            "materials": [{"name": "Face"}, {"name": "Body"}],
            "textures": [{"source": 0}],
            "images": [{"uri": "tex0.png"}],
            "meshes": [{"primitives": [{}]}],
        }
        vrm_path = tmp_path / "synthetic.vrm"
        vrm_path.write_bytes(_make_minimal_glb(gltf))

        parsed = parse_vrm_gltf_json(str(vrm_path))
        assert parsed["materials"] == gltf["materials"]
        assert len(parsed["textures"]) == 1

    def test_rejects_non_gltf_file(self, tmp_path):
        from unity3d_mcp.avatar import VRMParseError, parse_vrm_gltf_json

        bad_path = tmp_path / "not_a_vrm.vrm"
        bad_path.write_bytes(b"this is not a glTF file at all")

        with pytest.raises(VRMParseError):
            parse_vrm_gltf_json(str(bad_path))

    def test_rejects_truncated_file(self, tmp_path):
        from unity3d_mcp.avatar import VRMParseError, parse_vrm_gltf_json

        truncated = tmp_path / "truncated.vrm"
        truncated.write_bytes(b"glTF" + b"\x00" * 4)  # magic present, header incomplete

        with pytest.raises(VRMParseError):
            parse_vrm_gltf_json(str(truncated))

    @requires_vrm_file
    def test_parses_real_nekomimi_vrm(self, vrm_test_file):
        from unity3d_mcp.avatar import parse_vrm_gltf_json, summarize_vrm_materials

        gltf = parse_vrm_gltf_json(str(vrm_test_file))
        summary = summarize_vrm_materials(gltf)

        # Real, non-hardcoded numbers pulled from the actual file — this
        # is exactly the class of claim the old code faked.
        assert summary["material_count"] > 0
        assert summary["texture_count"] > 0
        assert summary["mesh_count"] > 0
        assert len(summary["materials"]) == summary["material_count"]
        assert all("name" in m for m in summary["materials"])


class TestSummarizeVrmMaterials:
    def test_counts_match_input_exactly(self):
        from unity3d_mcp.avatar import summarize_vrm_materials

        gltf = {
            "materials": [
                {"name": "M1", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}},
                {"name": "M2"},
            ],
            "textures": [{"source": 0}, {"source": 1}, {"source": 2}],
            "images": [{}, {}, {}],
            "meshes": [{"primitives": [{}, {}]}, {"primitives": [{}]}],
        }
        summary = summarize_vrm_materials(gltf)

        assert summary["material_count"] == 2
        assert summary["texture_count"] == 3
        assert summary["image_count"] == 3
        assert summary["mesh_count"] == 2
        assert summary["primitive_count"] == 3
        assert summary["materials"][0]["has_base_color_texture"] is True
        assert summary["materials"][1]["has_base_color_texture"] is False

    def test_handles_empty_gltf(self):
        from unity3d_mcp.avatar import summarize_vrm_materials

        summary = summarize_vrm_materials({})
        assert summary["material_count"] == 0
        assert summary["materials"] == []


class TestApplyVrchatOptimizationsReal:
    """VRMAvatarManager.import_vrm's optimize_for_vrchat path — no more hardcoded lies."""

    @pytest.mark.asyncio
    @requires_vrm_file
    async def test_import_reports_real_material_count_not_hardcoded(self, tmp_path, mock_config, vrm_test_file):
        from unity3d_mcp.avatar import VRMAvatarManager

        manager = VRMAvatarManager(mock_config)
        result = await manager.import_vrm(str(vrm_test_file), str(tmp_path), optimize_for_vrchat=True)

        assert result["status"] == "success"
        opt = result["vrchat_optimizations"]

        # The old code always said "Standard to VRChat compatible" no
        # matter what. Assert the new fields are real computed data.
        assert isinstance(opt["material_count"], int)
        assert opt["material_count"] > 0
        assert opt["manifest_written"] is not None

        # The manifest must actually exist on disk with the same numbers.
        with open(opt["manifest_written"], encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["material_count"] == opt["material_count"]

        # It must NOT claim to have performed work it didn't do.
        assert "NOT performed" in opt["material_conversion"]
        assert "NOT performed" in opt["texture_compression"]

    @pytest.mark.asyncio
    async def test_optimization_handles_unparseable_vrm_honestly(self, tmp_path, mock_config):
        from unity3d_mcp.avatar import VRMAvatarManager

        bad_vrm = tmp_path / "bad.vrm"
        bad_vrm.write_bytes(b"not a real vrm file")

        manager = VRMAvatarManager(mock_config)
        result = await manager.import_vrm(str(bad_vrm), str(tmp_path), optimize_for_vrchat=True)

        assert result["status"] == "success"  # the copy itself succeeds
        opt = result["vrchat_optimizations"]
        assert opt["status"] == "error"
        assert "not attempted" in opt["material_conversion"]


class TestSetupAnimatorReal:
    """AnimationManager.setup_animator — now writes a real .controller asset."""

    @pytest.mark.asyncio
    async def test_writes_real_controller_and_meta_files(self, tmp_path):
        from unity3d_mcp.avatar import AnimationManager

        manager = AnimationManager(config=None)
        avatar_path = str(tmp_path / "Assets" / "Models" / "TestAvatar.vrm")
        result = await manager.setup_animator(avatar_path, animator_type="humanoid", include_facial=True)

        assert result["status"] == "success"

        controller_path = result["controller_path"]
        meta_path = result["meta_path"]

        import os

        assert os.path.exists(controller_path)
        assert os.path.exists(meta_path)

        with open(controller_path, encoding="utf-8") as f:
            content = f.read()

        # Structural sanity checks against real Unity YAML class IDs.
        assert "AnimatorController" in content
        assert "!u!91" in content  # AnimatorController class ID
        assert "!u!1107" in content  # AnimatorStateMachine class ID
        assert "!u!1102" in content  # AnimatorState class ID
        assert "Idle" in content
        assert "Walk" in content
        assert "Run" in content
        # Facial layer requested, must be present.
        assert "Facial Layer" in content
        assert "Neutral" in content

        # GUID in the .meta file must be a real 32-hex-char Unity-shaped GUID.
        with open(meta_path, encoding="utf-8") as f:
            meta_content = f.read()
        assert result["guid"] in meta_content
        assert len(result["guid"]) == 32
        int(result["guid"], 16)  # must be valid hex

    @pytest.mark.asyncio
    async def test_without_facial_omits_facial_layer(self, tmp_path):
        from unity3d_mcp.avatar import AnimationManager

        manager = AnimationManager(config=None)
        avatar_path = str(tmp_path / "Assets" / "Models" / "TestAvatar.vrm")
        result = await manager.setup_animator(avatar_path, include_facial=False)

        assert result["status"] == "success"
        with open(result["controller_path"], encoding="utf-8") as f:
            content = f.read()
        assert "Facial Layer" not in content

    @pytest.mark.asyncio
    async def test_honest_error_when_project_root_undeterminable(self):
        from unity3d_mcp.avatar import AnimationManager

        manager = AnimationManager(config=None)
        # No "Assets" segment anywhere, and no project_path given.
        result = await manager.setup_animator("/some/random/path/avatar.vrm")

        assert result["status"] == "error"
        assert "project" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_explicit_project_path_overrides_derivation(self, tmp_path):
        from unity3d_mcp.avatar import AnimationManager

        manager = AnimationManager(config=None)
        result = await manager.setup_animator(
            "avatar.vrm", project_path=str(tmp_path)
        )

        assert result["status"] == "success"
        assert str(tmp_path) in result["controller_path"]


class TestBuildAnimatorControllerYaml:
    """Direct tests of the YAML-generation helper — no filesystem needed."""

    def test_produces_matching_number_of_state_blocks(self):
        from unity3d_mcp.avatar import build_animator_controller_yaml

        layers = [{"name": "Base Layer", "states": ["Idle", "Walk"]}]
        params = [{"name": "Speed", "type": "float", "default": 0.0}]

        yaml_text = build_animator_controller_yaml("TestController", layers, params)

        assert yaml_text.count("!u!1102") == 2  # two states
        assert yaml_text.count("!u!1107") == 1  # one state machine
        assert yaml_text.count("!u!91") == 1  # one controller

    def test_multiple_layers_produce_multiple_state_machines(self):
        from unity3d_mcp.avatar import build_animator_controller_yaml

        layers = [
            {"name": "Base Layer", "states": ["Idle"]},
            {"name": "Facial Layer", "states": ["Neutral", "Happy"]},
        ]
        yaml_text = build_animator_controller_yaml("TestController", layers, [])

        assert yaml_text.count("!u!1107") == 2
        assert yaml_text.count("!u!1102") == 3

    def test_file_ids_are_unique(self):
        import re

        from unity3d_mcp.avatar import build_animator_controller_yaml

        layers = [
            {"name": "Base Layer", "states": ["Idle", "Walk", "Run"]},
            {"name": "Facial Layer", "states": ["Neutral", "Happy", "Sad"]},
        ]
        yaml_text = build_animator_controller_yaml("TestController", layers, [])

        file_ids = re.findall(r"&(\d+)", yaml_text)
        assert len(file_ids) == len(set(file_ids)), "duplicate fileID anchors would corrupt the asset"
