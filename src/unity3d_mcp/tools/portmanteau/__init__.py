"""
Portmanteau Tool Managers for Unity3D MCP Server

Consolidates related tools into unified portmanteau interfaces following
FastMCP 2.13+ patterns for better discoverability and reduced tool explosion.
"""

from .platform import PlatformToolManager
from .unity_api import UnityAPIToolManager
from .unity_asset import UnityAssetToolManager
from .unity_avatar import UnityAvatarToolManager
from .unity_bridge import UnityBridgeToolManager
from .unity_build import UnityBuildToolManager
from .unity_core import UnityCoreToolManager
from .unity_import import UnityImportToolManager
from .unity_jobs import UnityJobsToolManager
from .unity_render import UnityRenderToolManager
from .unity_vision_refine import UnityVisionRefineToolManager
from .unity_scene import UnitySceneToolManager
from .vrchat import VRChatToolManager
from .worldlabs import WorldLabsToolManager

__all__ = [
    "UnityCoreToolManager",
    "UnitySceneToolManager",
    "UnityAvatarToolManager",
    "UnityAssetToolManager",
    "UnityBuildToolManager",
    "VRChatToolManager",
    "WorldLabsToolManager",
    "PlatformToolManager",
    "UnityAPIToolManager",
    "UnityBridgeToolManager",
    "UnityRenderToolManager",
    "UnityJobsToolManager",
    "UnityImportToolManager",
    "UnityVisionRefineToolManager",
]
