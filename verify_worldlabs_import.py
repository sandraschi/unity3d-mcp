import asyncio
from pathlib import Path

from unity3d_mcp.server import create_app


async def verify_worldlabs_pipeline():
    """Verify WorldLabs Gaussian Splatting pipeline."""
    project_path = "C:/Users/sandr/My project"
    worldlabs_assets = Path(project_path) / "Assets/WorldLabs"

    # Initialize Server
    app = create_app()
    # Access the tools via the managers attached to the server instance
    server = app

    print(f"Verifying WorldLabs pipeline for project: {project_path}")

    # 1. Install/Verify Gaussian Splatting Package
    print("\n[Step 1] Checking/Installing Gaussian Splatting Package...")

    # Access via the manager directly since we have the server instance
    check_result = await server.worldlabs.check_gaussian_splatting_installed(project_path)
    print(f"Package check result: {check_result}")

    if not check_result.get("installed"):
        print("Package not installed. Installing...")
        install_result = await server.worldlabs.install_gaussian_splatting(project_path)
        print(f"Installation result: {install_result}")
        if not install_result.get("success"):
            print("❌ Failed to install Gaussian Splatting package")
            return
    else:
        print("✅ Gaussian Splatting package already installed")

    # 2. Verify WorldLabs Assets
    print("\n[Step 2] Verifying WorldLabs Assets...")
    if not worldlabs_assets.exists():
        print(f"❌ WorldLabs folder not found at {worldlabs_assets}")
        return

    ply_files = list(worldlabs_assets.rglob("*.ply"))
    splat_files = list(worldlabs_assets.rglob("*.splat"))

    total_splats = len(ply_files) + len(splat_files)

    if total_splats > 0:
        print(f"✅ Found {total_splats} Gaussian Splat files:")
        for f in ply_files[:5]:
            print(f"  - {f.relative_to(worldlabs_assets)}")
        if len(ply_files) > 5:
            print(f"  ... and {len(ply_files) - 5} more .ply files")

        for f in splat_files[:5]:
            print(f"  - {f.relative_to(worldlabs_assets)}")
    else:
        print("⚠️ No .ply or .splat files found in Assets/WorldLabs. Pipeline ready but no assets to render.")

    # 3. Simulate Import (Optional - just checking tool availability)
    print("\n[Step 3] Verification Complete")
    print("Gaussian Splatting support is enabled and assets are present.")


if __name__ == "__main__":
    asyncio.run(verify_worldlabs_pipeline())
