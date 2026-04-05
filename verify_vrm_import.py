import asyncio
import os
import sys
from pathlib import Path

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from unity3d_mcp.server import Unity3DConfig, Unity3DMCP


async def verify_pipeline():
    print("Starting VRM Import Verification...")

    # Configuration
    project_path = "C:/Users/sandr/My project"
    model_path = "C:/Users/sandr/.avatarmcp/models/Nekomimi-chan.vrm"

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

    # 2. Setup Avatar Descriptor (Note: Unity might need UniVRM for full VRM support)
    # For now, we verify the file is present in Assets
    print("\n2. Verifying Asset Presence...")
    expected_path = Path(project_path) / "Assets" / "Nekomimi-chan.vrm"
    if expected_path.exists():
        print(f"SUCCESS: VRM file found at {expected_path}")
    else:
        print(f"FAILURE: VRM file not found at {expected_path}")


if __name__ == "__main__":
    asyncio.run(verify_pipeline())
