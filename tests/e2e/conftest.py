"""
End-to-end test fixtures.

These fixtures detect and interact with real Unity installations.
"""

import os
from pathlib import Path
from typing import Optional

import pytest


def find_unity_executable() -> Optional[Path]:
    """Find Unity Editor executable on the system."""
    # Check environment variable first
    env_path = os.environ.get("UNITY_EDITOR_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    # Check Unity Hub installations (Windows)
    hub_path = Path(r"C:\Program Files\Unity\Hub\Editor")
    if hub_path.exists():
        # Find latest version
        versions = sorted(hub_path.iterdir(), reverse=True)
        for version in versions:
            unity_exe = version / "Editor" / "Unity.exe"
            if unity_exe.exists():
                return unity_exe

    # Check standard installation paths
    standard_paths = [
        Path(r"C:\Program Files\Unity\Editor\Unity.exe"),
        Path(r"C:\Program Files (x86)\Unity\Editor\Unity.exe"),
    ]

    for path in standard_paths:
        if path.exists():
            return path

    return None


def find_test_unity_project() -> Optional[Path]:
    """Find a Unity project for testing."""
    # Check environment variable
    env_path = os.environ.get("UNITY_TEST_PROJECT")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    # Check common locations
    common_paths = [
        Path(r"D:\Dev\repos\unity-project-1"),
        Path(r"D:\Unity\TestProject"),
        Path.home() / "Unity Projects" / "TestProject",
    ]

    for path in common_paths:
        if path.exists() and (path / "Assets").exists():
            return path

    return None


def check_univrm_installed(project_path: Path) -> bool:
    """Check if UniVRM is installed in the project."""
    manifest_path = project_path / "Packages" / "manifest.json"
    if not manifest_path.exists():
        return False

    import json

    with open(manifest_path) as f:
        manifest = json.load(f)

    deps = manifest.get("dependencies", {})
    return any("univrm" in k.lower() or "vrm" in k.lower() for k in deps.keys())


# Pytest markers
def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: mark test as end-to-end (requires Unity)")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_addoption(parser):
    parser.addoption("--run-e2e", action="store_true", default=False, help="Run end-to-end tests requiring Unity")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="Need --run-e2e to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)


# Fixtures


@pytest.fixture(scope="session")
def unity_executable() -> Optional[Path]:
    """Get Unity executable path, or None if not found."""
    return find_unity_executable()


@pytest.fixture(scope="session")
def unity_available(unity_executable) -> bool:
    """Check if Unity is available for testing."""
    return unity_executable is not None


@pytest.fixture(scope="session")
def unity_project() -> Optional[Path]:
    """Get test Unity project path, or None if not found."""
    return find_test_unity_project()


@pytest.fixture(scope="session")
def unity_project_with_vrm(unity_project) -> Optional[Path]:
    """Get Unity project with UniVRM installed."""
    if unity_project and check_univrm_installed(unity_project):
        return unity_project
    return None


@pytest.fixture
def unity_config(unity_executable, unity_project):
    """Create Unity3DConfig with real paths."""
    from unity3d_mcp.server import Unity3DConfig

    return Unity3DConfig(
        unity_editor_path=str(unity_executable) if unity_executable else "",
        project_path=str(unity_project) if unity_project else "",
        auto_detect_unity=False,
    )


# Skip decorators

requires_unity = pytest.mark.skipif(find_unity_executable() is None, reason="Unity Editor not found")

requires_unity_project = pytest.mark.skipif(find_test_unity_project() is None, reason="Unity test project not found")

requires_univrm = pytest.mark.skipif(
    find_test_unity_project() is None or not check_univrm_installed(find_test_unity_project()),
    reason="UniVRM not installed in test project",
)
