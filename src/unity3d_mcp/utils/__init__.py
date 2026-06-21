"""
Unity3D MCP Utilities

Shared utilities for path resolution, configuration, and logging.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class UnityPathResolver:
    """Resolves Unity Editor and project paths."""

    def __init__(self, config):
        self.config = config

    def find_unity_installations(self) -> list[dict[str, str]]:
        """Find all Unity Editor installations."""
        installations = []

        # Unity Hub installations
        hub_path = Path.home() / "AppData/Roaming/UnityHub/editors.json"
        if hub_path.exists():
            try:
                with open(hub_path) as f:
                    editors_data = json.load(f)
                    for _editor_id, editor_info in editors_data.items():
                        installations.append(
                            {
                                "version": editor_info.get("version", "unknown"),
                                "path": editor_info.get("location", ""),
                                "source": "Unity Hub",
                            }
                        )
            except Exception as e:
                logger.warning(f"Failed to parse Unity Hub editors: {e}")

        # Manual installations
        common_paths = [
            r"C:\Program Files\Unity\Editor\Unity.exe",
            r"C:\Program Files (x86)\Unity\Editor\Unity.exe",
        ]

        for path_str in common_paths:
            path = Path(path_str)
            if path.exists():
                installations.append({"version": "unknown", "path": str(path), "source": "Manual Installation"})

        return installations

    def resolve_project_path(self, project_identifier: str) -> str | None:
        """Resolve project path from name or path."""
        path = Path(project_identifier)

        # If it's already a valid path, return it
        if path.exists() and (path / "Assets").exists():
            return str(path)

        # Search common Unity project locations
        search_paths = [
            Path.home() / "Unity Projects",
            Path("D:/Unity Projects"),
            Path("C:/Unity Projects"),
        ]

        for search_path in search_paths:
            if search_path.exists():
                project_path = search_path / project_identifier
                if project_path.exists() and (project_path / "Assets").exists():
                    return str(project_path)

        return None


class ConfigManager:
    """Manages Unity3D MCP configuration."""

    def __init__(self, config):
        self.config = config
        self.config_file = Path.home() / ".unity3d_mcp_config.json"

    def load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        return {}

    def save_config(self, config_data: dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get_recent_projects(self) -> list[str]:
        """Get list of recently used Unity projects."""
        config = self.load_config()
        return config.get("recent_projects", [])

    def add_recent_project(self, project_path: str) -> None:
        """Add project to recent projects list."""
        config = self.load_config()
        recent = config.get("recent_projects", [])

        # Remove if already exists
        if project_path in recent:
            recent.remove(project_path)

        # Add to front
        recent.insert(0, project_path)

        # Keep only last 10
        recent = recent[:10]

        config["recent_projects"] = recent
        self.save_config(config)


class LogManager:
    """Manages logging configuration."""

    def __init__(self, config):
        self.config = config
        self.setup_logging()

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)

        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(Path.home() / "unity3d_mcp.log"),
            ],
        )

        # Set specific logger levels
        logging.getLogger("unity3d_mcp").setLevel(log_level)
        logging.getLogger("asyncio").setLevel(logging.WARNING)

    def get_log_file_path(self) -> str:
        """Get path to log file."""
        return str(Path.home() / "unity3d_mcp.log")


class UnityVersionResolver:
    """Resolves Unity version requirements."""

    def __init__(self):
        self.version_compatibility = {
            "VRM": ["2019.4", "2020.3", "2021.3", "2022.3"],
            "VRChat SDK": ["2019.4", "2022.3"],
            "URP": ["2019.4", "2020.3", "2021.3", "2022.3"],
            "HDRP": ["2019.4", "2020.3", "2021.3", "2022.3"],
        }

    def get_recommended_version(self, requirements: list[str]) -> str | None:
        """Get recommended Unity version for requirements."""
        if not requirements:
            return "2022.3"  # Latest LTS

        compatible_versions = None

        for requirement in requirements:
            req_versions = set(self.version_compatibility.get(requirement, []))
            if compatible_versions is None:
                compatible_versions = req_versions
            else:
                compatible_versions = compatible_versions.intersection(req_versions)

        if compatible_versions:
            # Return newest compatible version
            return max(compatible_versions)

        return "2022.3"  # Fallback to latest LTS

    def check_compatibility(self, unity_version: str, requirements: list[str]) -> dict[str, bool]:
        """Check compatibility of Unity version with requirements."""
        compatibility = {}

        for requirement in requirements:
            compatible_versions = self.version_compatibility.get(requirement, [])
            compatibility[requirement] = unity_version in compatible_versions

        return compatibility


class PerformanceProfiler:
    """Performance profiling utilities."""

    def __init__(self):
        self.profiles = {}

    def profile_avatar(self, avatar_data: dict[str, Any]) -> dict[str, Any]:
        """Profile avatar performance metrics."""
        polygon_count = avatar_data.get("polygon_count", 0)
        material_count = avatar_data.get("material_count", 0)
        texture_memory = avatar_data.get("texture_memory_mb", 0)

        # VRChat performance ranking
        rank = "Excellent"
        if polygon_count > 7500 or material_count > 1 or texture_memory > 10:
            rank = "Good"
        if polygon_count > 20000 or material_count > 4 or texture_memory > 40:
            rank = "Medium"
        if polygon_count > 70000 or material_count > 8 or texture_memory > 128:
            rank = "Poor"

        recommendations = []
        if polygon_count > 20000:
            recommendations.append("Reduce polygon count for better performance")
        if material_count > 4:
            recommendations.append("Combine materials to reduce draw calls")
        if texture_memory > 40:
            recommendations.append("Optimize texture sizes and compression")

        return {
            "performance_rank": rank,
            "polygon_count": polygon_count,
            "material_count": material_count,
            "texture_memory_mb": texture_memory,
            "recommendations": recommendations,
            "vrchat_compatible": rank != "Very Poor",
        }
