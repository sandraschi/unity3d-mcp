"""
Portmanteau Tool Managers for Unity3D MCP Server

Consolidates related tools into unified portmanteau interfaces following
FastMCP 2.13+ patterns for better discoverability and reduced tool explosion.
"""

from .unity_core import UnityCoreToolManager
from .unity_scene import UnitySceneToolManager
from .unity_avatar import UnityAvatarToolManager
from .unity_asset import UnityAssetToolManager
from .unity_build import UnityBuildToolManager
from .vrchat import VRChatToolManager
from .worldlabs import WorldLabsToolManager
from .platform import PlatformToolManager
from .unity_api import UnityAPIToolManager

__all__ = [
    'UnityCoreToolManager',
    'UnitySceneToolManager',
    'UnityAvatarToolManager',
    'UnityAssetToolManager',
    'UnityBuildToolManager',
    'VRChatToolManager',
    'WorldLabsToolManager',
    'PlatformToolManager',
    'UnityAPIToolManager',
]