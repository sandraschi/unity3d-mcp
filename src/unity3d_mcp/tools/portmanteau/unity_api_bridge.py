from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class UnityBridgeClient:
    """SOTA Unity Editor Bridge Client.
    Communicates with the C# Bridge script running inside Unity Editor.
    """

    def __init__(self, host: str = "localhost", port: int = 10835):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        self.timeout = 30.0

    async def is_alive(self) -> bool:
        """Check if the Unity Editor Bridge is reachable."""
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                response = await client.post(f"{self.url}/", json={"action": "ping"})
                return response.status_code == 200
        except Exception:
            return False

    async def execute_command(self, action: str, target: str | None = None, **kwargs) -> dict[str, Any]:
        """Send a JSON command to the Unity Editor Bridge."""
        payload: dict[str, Any] = {"action": action}
        if target is not None:
            payload["target"] = target
        payload.update(kwargs)
        logger.debug("unity3d.bridge.command_sent", action=action, target=target)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.url}/", json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error("unity3d.bridge.error", status_code=response.status_code, text=response.text)
                    return {"error": f"Bridge returned status {response.status_code}", "details": response.text}
        except httpx.ConnectError:
            return {"error": "Unity Editor Bridge not found. Is Unity running with MCPBridge.cs installed?"}
        except Exception as e:
            logger.exception("unity3d.bridge.exception")
            return {"error": str(e)}

    # High-level helper methods
    async def capture_game_view(
        self,
        output_path: str,
        width: int = 1920,
        height: int = 1080,
    ) -> dict[str, Any]:
        """Capture active scene camera to PNG via Editor bridge."""
        return await self.execute_command(
            "capture_game_view",
            output_path=output_path,
            width=width,
            height=height,
        )

    async def capture_multi_angle(
        self,
        output_dir: str,
        angles: int = 4,
        width: int = 1280,
        height: int = 720,
    ) -> dict[str, Any]:
        return await self.execute_command(
            "capture_multi_angle",
            output_dir=output_dir,
            angles=angles,
            width=width,
            height=height,
        )

    async def get_scene_summary(self) -> dict[str, Any]:
        return await self.execute_command("get_scene_summary")

    async def validate_scene(self) -> dict[str, Any]:
        return await self.execute_command("validate_scene")

    async def create_prefab(
        self,
        target: str,
        prefab_path: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        return await self.execute_command(
            "create_prefab",
            target=target,
            prefab_path=prefab_path,
            name=name,
        )

    async def run_simulation(self, duration: float = 1.0, record_data: bool = False) -> dict[str, Any]:
        return await self.execute_command(
            "run_simulation",
            duration=duration,
            record_data=1 if record_data else 0,
        )

    async def simulation_status(self) -> dict[str, Any]:
        return await self.execute_command("simulation_status")

    async def stop_simulation(self) -> dict[str, Any]:
        return await self.execute_command("stop_simulation")

    async def get_hierarchy(self) -> dict[str, Any]:
        return await self.execute_command("get_hierarchy")

    async def transform_object(
        self, target: str, position: list[float] | None = None, rotation: list[float] | None = None
    ) -> dict[str, Any]:
        return await self.execute_command("transform_object", target=target, position=position, rotation=rotation)

    async def create_object(self, name: str, type: str = "GameObject") -> dict[str, Any]:
        return await self.execute_command("create_object", name=name, type=type)

    async def delete_object(self, target: str) -> dict[str, Any]:
        return await self.execute_command("delete_object", target=target)
