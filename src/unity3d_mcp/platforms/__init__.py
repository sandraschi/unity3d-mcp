"""
Social VR Platform Integrations

Support for multiple social VR platforms beyond VRChat:
- ChilloutVR (CCK - Content Creation Kit)
- Resonite (direct VRM/GLB import)
- Cluster (Cluster Creator Kit)
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ChilloutVRManager:
    """ChilloutVR integration via CCK (Content Creation Kit).

    ChilloutVR is Unity-based like VRChat, uses similar workflow.
    CCK package: https://docs.abinteractive.net/cck/
    """

    def __init__(self, config):
        self.config = config
        self.cck_package = {
            "name": "com.abi.cck",
            "git": "https://github.com/ABI-Software/CCK.git",
            "docs": "https://docs.abinteractive.net/cck/",
        }
        self.performance_limits = {
            "excellent": {"polygons": 32000, "materials": 4, "bones": 150},
            "good": {"polygons": 70000, "materials": 8, "bones": 256},
            "medium": {"polygons": 70000, "materials": 16, "bones": 400},
            "poor": {"polygons": 150000, "materials": 32, "bones": 750},
        }

    async def check_cck_installed(self, project_path: str) -> dict[str, Any]:
        """Check if ChilloutVR CCK is installed."""
        try:
            manifest_path = Path(project_path) / "Packages" / "manifest.json"

            if not manifest_path.exists():
                return {"status": "error", "installed": False, "message": "Not a Unity project"}

            with open(manifest_path) as f:
                manifest = json.load(f)

            deps = manifest.get("dependencies", {})

            # Check for CCK package
            cck_names = ["com.abi.cck", "abi.cck", "cck"]
            for name in cck_names:
                if name in deps:
                    return {
                        "status": "success",
                        "installed": True,
                        "package": name,
                        "version": deps[name],
                    }

            # Check for any ABI package
            for dep in deps:
                if "abi" in dep.lower() or "chillout" in dep.lower():
                    return {
                        "status": "success",
                        "installed": True,
                        "package": dep,
                        "version": deps[dep],
                    }

            return {
                "status": "success",
                "installed": False,
                "message": "CCK not installed",
                "install_url": self.cck_package["docs"],
            }

        except Exception as e:
            return {"status": "error", "installed": False, "message": str(e)}

    async def install_cck(self, project_path: str) -> dict[str, Any]:
        """Install ChilloutVR CCK package.

        Note: CCK requires manual download from ABI website due to licensing.
        This provides instructions rather than auto-install.
        """
        return {
            "status": "info",
            "message": "CCK requires manual installation",
            "instructions": [
                "1. Visit https://docs.abinteractive.net/cck/",
                "2. Download the CCK Unity package",
                "3. Import into Unity via Assets > Import Package",
                "4. Configure CCK settings in the editor",
            ],
            "documentation": self.cck_package["docs"],
            "note": "CCK is free but requires ABI account",
        }

    async def setup_cvr_avatar(
        self,
        avatar_object: str,
        project_path: str,
        eye_height: float = 1.6,
        voice_position: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Setup CVRAvatar component on avatar.

        This generates the configuration - actual component addition
        requires Unity Editor execution.
        """
        config = {
            "avatar_object": avatar_object,
            "eye_height": eye_height,
            "voice_position": voice_position or {"x": 0, "y": 1.6, "z": 0.1},
            "components_to_add": [
                "CVRAvatar",
                "CVRAvatarBiped",  # For humanoid rigs
            ],
            "recommended_setup": [
                "Add CVRAvatar to root object",
                "Configure eye/view position",
                "Setup voice position",
                "Add CVR components for special features",
                "Test in CCK before upload",
            ],
        }

        return {
            "status": "success",
            "message": f"CVRAvatar config generated for: {avatar_object}",
            "configuration": config,
            "unity_method": "ChilloutVRSetup.ConfigureAvatar",
        }

    async def validate_for_chillout(self, avatar_name: str, project_path: str) -> dict[str, Any]:
        """Validate avatar for ChilloutVR upload."""
        # ChilloutVR is more permissive than VRChat
        return {
            "status": "success",
            "message": "ChilloutVR validation (simulated)",
            "platform": "ChilloutVR",
            "notes": [
                "ChilloutVR has more generous limits than VRChat",
                "Supports more Unity components",
                "PhysBones equivalent: Dynamic Bones or CVR equivalent",
                "Less strict on polygon counts",
            ],
            "performance_limits": self.performance_limits,
        }


class ResoniteManager:
    """Resonite (formerly NeosVR) integration.

    Resonite supports direct VRM/GLB import - no Unity required!
    Content is created/edited directly in-world.
    """

    def __init__(self, config):
        self.config = config
        self.supported_formats = [".vrm", ".glb", ".gltf", ".fbx", ".obj"]
        self.performance_recommendations = {
            "avatar_polygons": 100000,
            "avatar_materials": 20,
            "texture_resolution": 4096,
        }

    async def prepare_for_resonite(
        self,
        model_path: str,
        optimize: bool = True,
    ) -> dict[str, Any]:
        """Prepare a model for Resonite import.

        Resonite imports VRM/GLB directly - no SDK needed!
        """
        path = Path(model_path)

        if not path.exists():
            return {"status": "error", "message": f"File not found: {model_path}"}

        suffix = path.suffix.lower()
        if suffix not in self.supported_formats:
            return {
                "status": "error",
                "message": f"Unsupported format: {suffix}",
                "supported": self.supported_formats,
            }

        return {
            "status": "success",
            "message": "Model ready for Resonite import",
            "model_path": str(path),
            "format": suffix,
            "import_instructions": [
                "1. Open Resonite",
                "2. Open your inventory or spawn a new object",
                "3. Drag and drop the file into Resonite",
                "4. Or use File > Import in desktop mode",
                "5. The model will be imported and can be saved to inventory",
            ],
            "vrm_notes": [
                "VRM files import with expressions/blend shapes",
                "Humanoid rig is auto-detected",
                "Can be equipped directly as avatar",
            ]
            if suffix == ".vrm"
            else [],
            "optimization_tips": [
                "Use GLB for smaller file sizes",
                "VRM 1.0 is well supported",
                "Resonite handles high poly counts well",
                "In-world tools can optimize further",
            ],
        }

    async def check_resonite_compatibility(self, model_path: str) -> dict[str, Any]:
        """Check if model is compatible with Resonite."""
        path = Path(model_path)

        if not path.exists():
            return {"status": "error", "message": "File not found"}

        suffix = path.suffix.lower()
        file_size = path.stat().st_size / (1024 * 1024)  # MB

        compatibility = {
            "format_supported": suffix in self.supported_formats,
            "file_size_mb": round(file_size, 2),
            "size_ok": file_size < 100,  # 100MB soft limit
        }

        recommendations = []
        if file_size > 50:
            recommendations.append("Consider optimizing - large files may load slowly")
        if suffix == ".fbx":
            recommendations.append("GLB format recommended for better compatibility")

        return {
            "status": "success",
            "compatible": compatibility["format_supported"],
            "details": compatibility,
            "recommendations": recommendations,
            "resonite_features": [
                "Real-time in-world editing",
                "No external tools needed for adjustments",
                "Collaborative creation supported",
                "ProtoFlux for scripting/logic",
            ],
        }


class ClusterManager:
    """Cluster (Japanese social VR) integration.

    Cluster uses Unity + Cluster Creator Kit.
    Popular in Japan, supports VRM avatars.
    """

    CREATOR_KIT_URL = "https://creator.cluster.mu/"

    def __init__(self, config):
        self.config = config

    async def check_cluster_kit_installed(self, project_path: str) -> dict[str, Any]:
        """Check if Cluster Creator Kit is installed."""
        try:
            manifest_path = Path(project_path) / "Packages" / "manifest.json"

            if not manifest_path.exists():
                return {"status": "error", "installed": False, "message": "Not a Unity project"}

            with open(manifest_path) as f:
                manifest = json.load(f)

            deps = manifest.get("dependencies", {})

            # Check for Cluster packages
            cluster_packages = ["mu.cluster.cluster-creator-kit", "cluster"]
            for pkg in cluster_packages:
                if pkg in deps:
                    return {
                        "status": "success",
                        "installed": True,
                        "package": pkg,
                        "version": deps[pkg],
                    }

            for dep in deps:
                if "cluster" in dep.lower():
                    return {
                        "status": "success",
                        "installed": True,
                        "package": dep,
                        "version": deps[dep],
                    }

            return {
                "status": "success",
                "installed": False,
                "message": "Cluster Creator Kit not installed",
                "install_url": self.CREATOR_KIT_URL,
            }

        except Exception as e:
            return {"status": "error", "installed": False, "message": str(e)}

    async def prepare_for_cluster(
        self,
        avatar_path: str,
        project_path: str,
    ) -> dict[str, Any]:
        """Prepare avatar for Cluster upload."""
        return {
            "status": "success",
            "message": "Cluster preparation info",
            "platform": "Cluster",
            "avatar_path": avatar_path,
            "requirements": [
                "VRM format strongly recommended",
                "Humanoid rig required",
                "Japanese UI (some English)",
                "Cluster account required",
            ],
            "upload_steps": [
                "1. Install Cluster Creator Kit in Unity",
                "2. Import VRM avatar",
                "3. Add ClusterAvatar component",
                "4. Configure in Creator Kit window",
                "5. Upload via Creator Kit",
            ],
            "creator_kit_url": self.CREATOR_KIT_URL,
            "notes": [
                "Cluster is popular in Japan",
                "Hosts many virtual events",
                "VRM is the primary avatar format",
                "Good mobile VR support",
            ],
        }


class PlatformManager:
    """Unified manager for all social VR platforms."""

    def __init__(self, config):
        self.config = config
        self.chillout = ChilloutVRManager(config)
        self.resonite = ResoniteManager(config)
        self.cluster = ClusterManager(config)

    async def list_supported_platforms(self) -> dict[str, Any]:
        """List all supported social VR platforms."""
        return {
            "status": "success",
            "platforms": {
                "vrchat": {
                    "name": "VRChat",
                    "engine": "Unity",
                    "sdk": "VRChat SDK",
                    "avatar_format": "Unity prefab + VRC components",
                    "status": "Full support",
                },
                "chilloutvr": {
                    "name": "ChilloutVR",
                    "engine": "Unity",
                    "sdk": "CCK (Content Creation Kit)",
                    "avatar_format": "Unity prefab + CVR components",
                    "status": "Supported",
                    "notes": "More permissive than VRChat",
                },
                "resonite": {
                    "name": "Resonite",
                    "engine": "FrooxEngine (custom)",
                    "sdk": "None needed - direct import",
                    "avatar_format": "VRM, GLB, GLTF, FBX",
                    "status": "Supported",
                    "notes": "No Unity required, in-world creation",
                },
                "cluster": {
                    "name": "Cluster",
                    "engine": "Unity",
                    "sdk": "Cluster Creator Kit",
                    "avatar_format": "VRM preferred",
                    "status": "Supported",
                    "notes": "Popular in Japan",
                },
            },
        }

    async def check_platform_sdk(self, platform: str, project_path: str) -> dict[str, Any]:
        """Check if platform SDK is installed."""
        platform = platform.lower()

        if platform in ["chillout", "chilloutvr", "cvr"]:
            return await self.chillout.check_cck_installed(project_path)
        elif platform in ["cluster"]:
            return await self.cluster.check_cluster_kit_installed(project_path)
        elif platform in ["resonite", "neos"]:
            return {
                "status": "success",
                "installed": True,
                "message": "Resonite doesn't require a Unity SDK - import directly!",
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown platform: {platform}",
                "supported": ["vrchat", "chilloutvr", "resonite", "cluster"],
            }
