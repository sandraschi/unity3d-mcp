import os
from typing import Any, Dict, List

import structlog
import UnityPy

logger = structlog.get_logger(__name__)


class UnityDiskOps:
    """SOTA Unity "Hands-Off" Disk Operations.
    Manipulate project assets directly using UnityPy and YAML parsing.
    """

    @staticmethod
    def inspect_file(file_path: str) -> Dict[str, Any]:
        """Inspect a serialized Unity file (.unity, .prefab, .asset) without Unity launched."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        try:
            env = UnityPy.load(file_path)
            assets = []

            for obj in env.objects:
                asset_info = {
                    "type": str(obj.type),
                    "path_id": obj.path_id,
                }

                # Extract more readable info if possible
                if obj.type.name in ["GameObject", "MonoBehaviour", "Texture2D", "Mesh"]:
                    try:
                        data = obj.read()
                        asset_info["name"] = getattr(data, "name", "Unnamed")
                        if hasattr(data, "m_TagString"):
                            asset_info["tag"] = data.m_TagString
                    except Exception:
                        pass

                assets.append(asset_info)

            return {
                "file": os.path.basename(file_path),
                "object_count": len(env.objects),
                "objects": assets[:100],  # Limit output
            }
        except Exception as e:
            logger.exception("unity3d.disk.inspect_error", path=file_path)
            return {"error": f"Failed to load Unity file: {str(e)}"}

    @staticmethod
    def list_textures(file_path: str) -> List[Dict[str, Any]]:
        """List all textures inside a Unity file."""
        try:
            env = UnityPy.load(file_path)
            textures = []
            for obj in env.objects:
                if obj.type.name == "Texture2D":
                    data = obj.read()
                    textures.append(
                        {
                            "name": data.name,
                            "width": data.m_Width,
                            "height": data.m_Height,
                            "format": str(data.m_TextureFormat),
                            "path_id": obj.path_id,
                        }
                    )
            return textures
        except Exception as e:
            logger.error("unity3d.disk.list_textures_error", error=str(e))
            return []

    # YAML-based manipulation for Source assets
    @staticmethod
    def modify_yaml_property(file_path: str, component_type: str, property_name: str, new_value: Any) -> Dict[str, Any]:
        """Simple regex-based YAML modification for Unity source files (Prefabs/Scenes).
        This is safer than a full YAML parser for Unity's specific dialect.
        """
        if not file_path.endswith((".prefab", ".unity", ".asset")):
            return {"error": "Only .prefab, .unity, and .asset files are supported for YAML modification."}

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            in_component = False

            for i, line in enumerate(lines):
                if component_type in line:
                    in_component = True
                elif line.startswith("--- !u!"):
                    in_component = False

                if in_component and f"{property_name}:" in line:
                    lines[i] = f"    {property_name}: {new_value}\n"
                    modified = True
                    break

            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return {"status": "success", "file": file_path}
            else:
                return {"error": f"Property '{property_name}' in component '{component_type}' not found."}

        except Exception as e:
            return {"error": str(e)}
