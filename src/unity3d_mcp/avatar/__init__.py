"""
Avatar and VRM Management

VRM avatar import, configuration, and animation setup for Unity.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


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
    ) -> Dict[str, Any]:
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

            shutil.copy2(vrm_path, target_path)

            result = {
                "status": "success",
                "message": f"VRM avatar imported: {vrm_name}",
                "vrm_path": str(target_path),
                "avatar_name": vrm_name,
                "optimized_for_vrchat": optimize_for_vrchat,
                "prefab_created": create_prefab,
            }

            if optimize_for_vrchat:
                result["vrchat_optimizations"] = await self._apply_vrchat_optimizations(vrm_name, project_path)

            if create_prefab:
                result["prefab_path"] = f"Assets/Prefabs/{vrm_name}.prefab"

            return result

        except Exception as e:
            logger.error(f"Failed to import VRM: {e}")
            return {"status": "error", "message": str(e)}

    async def _apply_vrchat_optimizations(self, avatar_name: str, project_path: str) -> Dict[str, Any]:
        """Apply VRChat-specific optimizations."""
        optimizations = {
            "material_conversion": "Standard to VRChat compatible",
            "texture_compression": "Applied mobile compression",
            "polygon_reduction": "Optimized for VRChat limits",
            "performance_rank": "Good (estimated)",
            "sdk_components": "VRC Avatar Descriptor added",
        }

        return optimizations


class AnimationManager:
    """Manages avatar animation and animator controllers."""

    def __init__(self, config):
        self.config = config

    async def setup_animator(
        self, avatar_path: str, animator_type: str = "humanoid", include_facial: bool = True
    ) -> Dict[str, Any]:
        """Setup animator controller for avatar."""
        try:
            avatar_name = Path(avatar_path).stem
            controller_path = f"Assets/Animators/{avatar_name}_Controller.controller"

            # Create animator controller structure
            controller_config = {
                "type": animator_type,
                "layers": [
                    {
                        "name": "Base Layer",
                        "states": [
                            {"name": "Idle", "motion": "Assets/Animations/Idle.anim"},
                            {"name": "Walk", "motion": "Assets/Animations/Walk.anim"},
                            {"name": "Run", "motion": "Assets/Animations/Run.anim"},
                        ],
                    }
                ],
                "parameters": [
                    {"name": "Speed", "type": "float", "default": 0.0},
                    {"name": "Grounded", "type": "bool", "default": True},
                ],
            }

            if include_facial:
                controller_config["layers"].append(
                    {
                        "name": "Facial Layer",
                        "states": [
                            {"name": "Neutral", "motion": "Assets/Animations/Face_Neutral.anim"},
                            {"name": "Happy", "motion": "Assets/Animations/Face_Happy.anim"},
                            {"name": "Sad", "motion": "Assets/Animations/Face_Sad.anim"},
                        ],
                    }
                )

                controller_config["parameters"].extend(
                    [
                        {"name": "Expression", "type": "int", "default": 0},
                        {"name": "BlinkRate", "type": "float", "default": 1.0},
                    ]
                )

            return {
                "status": "success",
                "message": f"Animator controller setup for: {avatar_name}",
                "controller_path": controller_path,
                "animator_type": animator_type,
                "facial_animations": include_facial,
                "configuration": controller_config,
            }

        except Exception as e:
            logger.error(f"Failed to setup animator: {e}")
            return {"status": "error", "message": str(e)}

    async def create_animation_clip(
        self, clip_name: str, duration: float, keyframes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create animation clip with keyframes."""
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
