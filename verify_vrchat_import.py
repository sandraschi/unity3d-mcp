import asyncio
import os
import sys

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from unity3d_mcp.server import Unity3DConfig, Unity3DMCP


async def verify_pipeline():
    print("Starting VRChat Import Pipeline Verification...")

    # Configuration
    project_path = "C:/Users/sandr/My project"
    model_path = "D:/Models/scout_model.blend"

    config = Unity3DConfig(project_path=project_path)
    server = Unity3DMCP(config)

    # 1. Import Model
    print(f"\n1. Importing model from {model_path}...")
    try:
        import_result = await server.import_export_manager.import_3d_model(
            model_path=model_path, project_path=project_path
        )
        print(f"Import Result: {import_result}")
    except Exception as e:
        print(f"Import Failed: {e}")
        return

    # 2. Setup Avatar Descriptor
    print("\n2. Setting up Avatar Descriptor...")
    avatar_prefab = "Assets/scout_model.blend"  # Using .blend file directly as asset path
    try:
        # Note: server.vrchat_sdk might not be directly exposed as tool, but we registered it in server.py
        # We should call the registered tool method if possible, or direct method
        # The tool registered was 'setup_avatar_descriptor' which calls server.vrchat_sdk.setup_avatar_descriptor
        setup_result = await server.vrchat_sdk.setup_avatar_descriptor(avatar_prefab=avatar_prefab)
        print(f"Setup Result: {setup_result}")
    except Exception as e:
        print(f"Setup Failed: {e}")
        # Proceeding even if setup fails to test upload (which normally requires setup)

    # 3. Upload Avatar
    print("\n3. Uploading Avatar...")
    try:
        upload_result = await server.vrchat_sdk.upload_avatar(
            avatar_prefab=avatar_prefab,
            avatar_name="Scout Little Car",
            description="Imported via MCP",
            tags=["mcp", "auto-import"],
        )
        print(f"Upload Result: {upload_result}")
    except Exception as e:
        print(f"Upload Failed: {e}")


if __name__ == "__main__":
    asyncio.run(verify_pipeline())
