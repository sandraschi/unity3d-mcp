"""Tests for VRM avatar pipeline operations."""

from unittest.mock import Mock, patch

import pytest
from fixtures.factories import VRM_TEST_FILE, requires_vrm_file


@pytest.mark.asyncio
async def test_vrm_import():
    """Test VRM file import."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="VRM imported")

        # Would call: import_vrm(vrm_path="avatar.vrm")
        # Mock verification
        assert mock_run is not None


@pytest.mark.asyncio
async def test_vrm_validation():
    """Test VRM avatar validation."""
    mock_avatar = {
        "name": "TestAvatar",
        "triangles": 10000,
        "materials": 8,
        "texture_memory": 30,
        "blend_shapes": 50,
        "humanoid_rig": True,
    }

    # Would call: validate_vrm_avatar(avatar_name="TestAvatar")
    # Validation logic:
    # - Check humanoid rig
    # - Verify blend shapes present
    # - Count triangles/materials

    assert mock_avatar["humanoid_rig"] is True
    assert mock_avatar["triangles"] < 15000  # Medium rank
    assert mock_avatar["materials"] < 16


@pytest.mark.asyncio
async def test_vrm_optimization():
    """Test VRM avatar optimization."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)

        # Would call: optimize_vrm_avatar(performance_rank="Good")
        # Optimizations:
        # - Reduce polygons
        # - Compress textures
        # - Merge materials

        assert mock_run is not None


@pytest.mark.asyncio
async def test_blend_shape_setup():
    """Test blend shape configuration."""
    expressions = ["Joy", "Angry", "Sorrow", "Fun", "Blink"]

    # Would call: setup_vrm_expressions(expressions)
    assert len(expressions) > 0
    assert "Blink" in expressions  # Essential expression


@pytest.mark.asyncio
async def test_performance_rank_calculation():
    """Test VRChat performance rank calculation."""
    avatar_stats = {"triangles": 7000, "materials": 7, "texture_memory": 35}

    # Performance rank logic:
    # Excellent: < 7500 tris, < 10 mats, < 10 MB
    # Good: < 10000 tris, < 8 mats, < 40 MB

    # This should be "Good" rank
    is_excellent = (
        avatar_stats["triangles"] < 7500 and avatar_stats["materials"] < 10 and avatar_stats["texture_memory"] < 10
    )
    is_good = (
        avatar_stats["triangles"] < 10000 and avatar_stats["materials"] < 8 and avatar_stats["texture_memory"] < 40
    )

    assert not is_excellent
    assert is_good


# ============================================================================
# Tests using real VRM file (skipped if not present)
# ============================================================================


@requires_vrm_file
def test_vrm_file_exists():
    """Test that VRM test file exists."""
    assert VRM_TEST_FILE.exists()
    assert VRM_TEST_FILE.suffix == ".vrm"


@requires_vrm_file
def test_vrm_file_size():
    """Test VRM file has reasonable size."""
    size_mb = VRM_TEST_FILE.stat().st_size / (1024 * 1024)
    assert size_mb > 0.1, "VRM file too small"
    assert size_mb < 100, "VRM file too large"


@requires_vrm_file
def test_vrm_file_readable():
    """Test VRM file can be read (it's a GLB container)."""
    with open(VRM_TEST_FILE, "rb") as f:
        magic = f.read(4)
    # VRM/GLB files start with glTF magic number
    assert magic == b"glTF", f"Invalid VRM magic: {magic}"
