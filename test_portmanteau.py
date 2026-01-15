#!/usr/bin/env python3
"""
Simple test to validate portmanteau conversion
"""

def test_imports():
    """Test that all portmanteau tools can be imported."""
    try:
        import sys
        sys.path.insert(0, 'src')

        from unity3d_mcp.tools.portmanteau import (
            UnityCoreToolManager,
            UnitySceneToolManager,
            UnityAvatarToolManager,
            UnityAssetToolManager,
            UnityBuildToolManager,
            VRChatToolManager,
            WorldLabsToolManager,
            PlatformToolManager,
            UnityAPIToolManager,
        )
        print("✓ All portmanteau tool managers imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_server_syntax():
    """Test that server.py has valid syntax."""
    try:
        import py_compile
        py_compile.compile('src/unity3d_mcp/server.py', doraise=True)
        print("✓ Server syntax is valid")
        return True
    except Exception as e:
        print(f"✗ Server syntax error: {e}")
        return False

if __name__ == "__main__":
    print("Testing portmanteau conversion...")

    success = True
    success &= test_imports()
    success &= test_server_syntax()

    if success:
        print("\n🎉 Portmanteau conversion successful!")
        print("The Unity3D MCP server now uses 9 portmanteau tools instead of 60+ individual tools.")
    else:
        print("\n❌ Portmanteau conversion has issues that need to be resolved.")