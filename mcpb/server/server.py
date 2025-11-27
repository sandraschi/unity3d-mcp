"""MCP server entry point for Unity3D-MCP.

This is the MCPB-compliant server wrapper that launches the Unity3D-MCP server.
"""

import sys
from pathlib import Path

# Add parent directory to path to import main server
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Import and run main server
try:
    from server import main
except ImportError:
    try:
        from unity3d_mcp.server import main
    except ImportError:
        import unity3d_mcp

        main = unity3d_mcp.main

if __name__ == "__main__":
    main()
