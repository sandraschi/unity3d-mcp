from typing import Any, Dict, List

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

    async def execute_command(self, action: str, target: str = None, **kwargs) -> Dict[str, Any]:
        """Send a JSON command to the Unity Editor Bridge."""
        payload = {"action": action, "target": target, **kwargs}
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
    ) -> Dict[str, Any]:
        """Capture active scene camera to PNG via Editor bridge."""
        return await self.execute_command(
            "capture_game_view",
            output_path=output_path,
            width=width,
            height=height,
        )

    async def get_hierarchy(self) -> Dict[str, Any]:
        return await self.execute_command("get_hierarchy")

    async def transform_object(
        self, target: str, position: List[float] = None, rotation: List[float] = None
    ) -> Dict[str, Any]:
        return await self.execute_command("transform_object", target=target, position=position, rotation=rotation)

    async def create_object(self, name: str, type: str = "GameObject") -> Dict[str, Any]:
        return await self.execute_command("create_object", name=name, type=type)

    async def delete_object(self, target: str) -> Dict[str, Any]:
        return await self.execute_command("delete_object", target=target)
