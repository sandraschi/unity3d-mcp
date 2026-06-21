"""
Fixture factories for creating test data.

These functions create mock objects and test data programmatically.
"""

import json
from pathlib import Path
from typing import Any

import pytest

# Path to real VRM test file
VRM_TEST_FILE = Path(__file__).parent / "Nekomimi-chan.vrm"


def has_vrm_test_file() -> bool:
    """Check if VRM test file exists."""
    return VRM_TEST_FILE.exists()


# Skip marker for tests requiring VRM file
requires_vrm_file = pytest.mark.skipif(not has_vrm_test_file(), reason=f"VRM test file not found: {VRM_TEST_FILE}")


def create_unity_manifest(
    dependencies: dict[str, str] | None = None,
    include_vrchat: bool = False,
) -> dict[str, Any]:
    """Create a Unity package manifest."""
    deps = dependencies or {
        "com.unity.modules.ai": "1.0.0",
        "com.unity.modules.animation": "1.0.0",
    }

    if include_vrchat:
        deps.update(
            {
                "com.vrchat.avatars": "3.5.0",
                "com.vrchat.base": "3.5.0",
            }
        )

    return {"dependencies": deps}


def create_unity_project_structure(base_path: Path, include_vrchat: bool = False) -> Path:
    """Create a complete Unity project structure."""
    project_path = base_path / "TestUnityProject"
    project_path.mkdir(exist_ok=True)

    # Standard Unity folders
    folders = [
        "Assets",
        "Assets/Scenes",
        "Assets/Prefabs",
        "Assets/Textures",
        "Assets/Materials",
        "Assets/Animations",
        "Library",
        "Packages",
        "ProjectSettings",
    ]

    if include_vrchat:
        folders.extend(
            [
                "Assets/VRChat",
                "Assets/VRChat/Avatars",
                "Assets/VRChat/Animations",
            ]
        )

    for folder in folders:
        (project_path / folder).mkdir(parents=True, exist_ok=True)

    # Create manifest.json
    manifest = create_unity_manifest(include_vrchat=include_vrchat)
    with open(project_path / "Packages" / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Create ProjectSettings
    (project_path / "ProjectSettings" / "ProjectSettings.asset").write_text(
        "# Unity Project Settings\nproductName: TestProject\n"
    )

    return project_path


def create_avatar_prefab(project_path: Path, name: str = "TestAvatar") -> Path:
    """Create a mock avatar prefab file."""
    prefab_path = project_path / "Assets" / "Prefabs" / f"{name}.prefab"
    prefab_path.parent.mkdir(parents=True, exist_ok=True)

    prefab_content = f"""
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &1234567890
GameObject:
  m_Name: {name}
  m_Component:
  - component: {{fileID: 1234567891}}
--- !u!114 &1234567891
MonoBehaviour:
  m_Script: {{fileID: 11500000, guid: VRCAvatarDescriptor}}
  viewPosition: {{x: 0, y: 1.6, z: 0}}
"""
    prefab_path.write_text(prefab_content)
    return prefab_path


def create_animation_controller(project_path: Path, name: str = "TestController") -> Path:
    """Create a mock animation controller file."""
    controller_path = project_path / "Assets" / "Animations" / f"{name}.controller"
    controller_path.parent.mkdir(parents=True, exist_ok=True)

    controller_content = f"""
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!91 &9100000
AnimatorController:
  m_Name: {name}
  m_AnimatorParameters: []
  m_AnimatorLayers:
  - m_Name: Base Layer
    m_StateMachine: {{fileID: 1107000011234567890}}
"""
    controller_path.write_text(controller_content)
    return controller_path


def create_vrchat_expression_params(
    project_path: Path,
    parameters: list[dict[str, Any]] | None = None,
) -> Path:
    """Create VRChat expression parameters asset."""
    params = parameters or [
        {"name": "VRCEmote", "type": "Int", "default": 0},
        {"name": "VRCFaceBlendH", "type": "Float", "default": 0},
        {"name": "VRCFaceBlendV", "type": "Float", "default": 0},
    ]

    params_path = project_path / "Assets" / "VRChat" / "ExpressionParameters.asset"
    params_path.parent.mkdir(parents=True, exist_ok=True)

    content = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!114 &11400000
MonoBehaviour:
  m_Script: {fileID: 11500000, guid: VRCExpressionParameters}
  parameters:
"""
    for param in params:
        content += f"  - name: {param['name']}\n"
        content += f"    valueType: {param['type']}\n"
        content += f"    defaultValue: {param['default']}\n"

    params_path.write_text(content)
    return params_path


def create_mock_unity_executable(base_path: Path) -> Path:
    """Create a mock Unity executable for testing."""
    unity_path = base_path / "Unity" / "Editor" / "Unity.exe"
    unity_path.parent.mkdir(parents=True, exist_ok=True)
    unity_path.write_text("mock unity executable")
    return unity_path


def create_vrchat_auth_file(base_path: Path, token: str = "test_token") -> Path:
    """Create a mock VRChat auth credentials file."""
    auth_path = base_path / "VRChat" / "auth.json"
    auth_path.parent.mkdir(parents=True, exist_ok=True)

    auth_data = {
        "authToken": token,
        "username": "test_user",
    }

    with open(auth_path, "w") as f:
        json.dump(auth_data, f)

    return auth_path


# Mock response data for API tests

MOCK_VRCHAT_USER_RESPONSE = {
    "id": "usr_12345678-1234-1234-1234-123456789abc",
    "displayName": "TestUser",
    "username": "testuser",
    "bio": "Test bio",
    "currentAvatarAssetUrl": "https://api.vrchat.cloud/avatar/test",
    "status": "active",
    "statusDescription": "Testing",
    "tags": ["system_avatar_access"],
}

MOCK_VRCHAT_2FA_RESPONSE = {
    "requiresTwoFactorAuth": ["totp", "otp"],
}

MOCK_AVATAR_VALIDATION = {
    "valid": True,
    "errors": [],
    "warnings": [],
    "performance_rank": "Good",
    "polygon_count": 15420,
    "material_count": 3,
    "texture_memory": "45 MB",
    "bone_count": 67,
    "skinned_meshes": 2,
    "physbones": 12,
}
