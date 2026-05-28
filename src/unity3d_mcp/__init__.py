"""
Unity3D MCP Server

FastMCP 2.10 compliant server for Unity 3D automation with dual stdio/HTTP interface.
Comprehensive Unity Editor automation, VRM avatar pipeline, and VRChat integration.
"""

__version__ = "1.3.0"
__author__ = "Sandra"
__license__ = "MIT"

from .server import Unity3DMCP, create_app

__all__ = ["Unity3DMCP", "create_app"]
