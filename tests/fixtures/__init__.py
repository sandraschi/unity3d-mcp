"""
Test fixtures package for unity3d-mcp.

This package contains reusable test data and fixture factories.
"""

from pathlib import Path

# Fixture paths
FIXTURES_DIR = Path(__file__).parent
UNITY_PROJECT_DIR = FIXTURES_DIR / "unity_project"
VRCHAT_DIR = FIXTURES_DIR / "vrchat"

# Test data files
VRM_AVATAR_PATH = FIXTURES_DIR / "Nekomimi-chan.vrm"


def get_fixture_path(name: str) -> Path:
    """Get path to a fixture file."""
    return FIXTURES_DIR / name
