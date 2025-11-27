"""
Example: Composing unity3d-mcp with oscmcp using FastMCP 2.13.1

This demonstrates how to create a unified VRChat pipeline by
mounting multiple MCP servers together.

Requirements:
    pip install fastmcp>=2.13.1
    pip install unity3d-mcp oscmcp

Usage:
    python -m examples.server_composition
"""

from fastmcp import FastMCP, Client

# Create orchestrator server
vr_pipeline = FastMCP(name="VRChat-Pipeline")


# ============================================================================
# Option 1: Mount external servers (when installed as packages)
# ============================================================================

def setup_with_packages():
    """Mount servers when installed as pip packages."""
    try:
        from unity3d_mcp.server import Unity3DMCP
        from oscmcp.server import server as osc_server
        
        unity3d = Unity3DMCP()
        
        # Mount with live linking (as_proxy=True)
        vr_pipeline.mount(unity3d.app, prefix="unity", as_proxy=True)
        vr_pipeline.mount(osc_server, prefix="osc", as_proxy=True)
        
        print("Mounted unity3d-mcp and oscmcp")
        
    except ImportError as e:
        print(f"Package not found: {e}")
        print("Install with: pip install unity3d-mcp oscmcp")


# ============================================================================
# Option 2: Create cross-server workflow tools
# ============================================================================

@vr_pipeline.tool
async def vrchat_send_parameter(parameter_name: str, value: float) -> dict:
    """Send VRChat avatar parameter via OSC.
    
    This is a convenience wrapper that uses oscmcp under the hood.
    """
    async with Client(vr_pipeline) as client:
        return await client.call_tool(
            "osc_send_osc_message",
            host="127.0.0.1",
            port=9000,
            address=f"/avatar/parameters/{parameter_name}",
            values=[value]
        )


@vr_pipeline.tool
async def vrchat_chatbox(message: str, send_immediately: bool = True) -> dict:
    """Send message to VRChat chatbox via OSC."""
    async with Client(vr_pipeline) as client:
        return await client.call_tool(
            "osc_send_osc_message",
            host="127.0.0.1",
            port=9000,
            address="/chatbox/input",
            values=[message, send_immediately, False]
        )


@vr_pipeline.tool
async def full_avatar_deploy(
    vrm_path: str,
    unity_project: str,
    avatar_name: str,
) -> dict:
    """Deploy VRM avatar end-to-end: import → validate → upload.
    
    Args:
        vrm_path: Path to VRM file
        unity_project: Path to Unity project with VRChat SDK
        avatar_name: Name for the uploaded avatar
    """
    async with Client(vr_pipeline) as client:
        # 1. Import VRM into Unity
        import_result = await client.call_tool(
            "unity_import_vrm_avatar",
            vrm_path=vrm_path,
            project_path=unity_project,
            create_prefab=True,
            optimize_for_vrchat=True
        )
        
        if import_result.get("status") == "error":
            return {"status": "error", "step": "import", "details": import_result}
        
        # 2. Validate for VRChat
        validate_result = await client.call_tool(
            "unity_vrchat_validate_avatar",
            avatar_name=avatar_name,
            project_path=unity_project
        )
        
        if validate_result.get("status") == "error":
            return {"status": "error", "step": "validate", "details": validate_result}
        
        # 3. Upload to VRChat
        upload_result = await client.call_tool(
            "unity_upload_vrchat_avatar",
            avatar_prefab=import_result.get("prefab_path", f"Assets/{avatar_name}.prefab"),
            avatar_name=avatar_name
        )
        
        return {
            "status": "success",
            "avatar_name": avatar_name,
            "import": import_result,
            "validation": validate_result,
            "upload": upload_result
        }


# ============================================================================
# VRChat OSC Address Reference
# ============================================================================

VRCHAT_OSC_ADDRESSES = {
    # Avatar Parameters
    "parameter": "/avatar/parameters/{name}",
    "change": "/avatar/change",
    
    # Chatbox
    "chatbox_input": "/chatbox/input",  # [message, send_immediately, play_sound]
    "chatbox_typing": "/chatbox/typing",  # [is_typing]
    
    # Tracking
    "head": "/tracking/trackers/head/position",
    "left_hand": "/tracking/trackers/1/position",
    "right_hand": "/tracking/trackers/2/position",
    
    # Input
    "vertical": "/input/Vertical",
    "horizontal": "/input/Horizontal",
    "jump": "/input/Jump",
    "run": "/input/Run",
}


# ============================================================================
# Main
# ============================================================================

def main():
    """Run the composed server."""
    setup_with_packages()
    
    # List available tools
    print("\n=== VRChat Pipeline Tools ===")
    print("From unity3d-mcp (prefix: unity_):")
    print("  - unity_import_vrm_avatar")
    print("  - unity_upload_vrchat_avatar")
    print("  - unity_vrchat_validate_avatar")
    print("  - unity_check_univrm_installed")
    print("")
    print("From oscmcp (prefix: osc_):")
    print("  - osc_send_osc_message")
    print("  - osc_start_osc_listener")
    print("")
    print("Pipeline tools:")
    print("  - vrchat_send_parameter")
    print("  - vrchat_chatbox")
    print("  - full_avatar_deploy")
    print("")
    print("Starting server...")
    
    # Run in stdio mode
    vr_pipeline.run()


if __name__ == "__main__":
    main()

