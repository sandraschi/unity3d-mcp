"""
Unity API Portmanteau Tool Manager

Consolidates advanced Unity Editor API operations into a unified portmanteau interface.
Note: Most operations are currently scaffolded for future Unity Editor API integration.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from ...utils.unity_runtime import bridge_available, execute_bridge_action, get_bridge_client
from .unity_api_bridge import UnityBridgeClient

logger = logging.getLogger(__name__)


class UnityAPIToolManager:
    """Portmanteau tool manager for advanced Unity Editor API operations."""

    def __init__(self, app: FastMCP, bridge: UnityBridgeClient | None = None):
        """Initialize the Unity API tool manager."""
        self.app = app
        self.bridge = bridge or get_bridge_client()

    def register_tools(self):
        """Register all Unity API portmanteau tools."""

        @self.app.tool
        async def unity_api(
            operation: str,
            class_name: str | None = None,
            method_name: str | None = None,
            parameters: dict[str, Any] | None = None,
            project_path: str | None = None,
            scene_path: str | None = None,
            wait_for_completion: bool = True,
            object_name: str | None = None,
            modifications: dict[str, Any] | None = None,
            prefab_name: str | None = None,
            duration: float = 1.0,
            record_data: bool = False,
            operations: list[dict[str, Any]] | None = None,
            path_type: str = "straight",
            path_points: list[dict[str, float]] | None = None,
            loop: bool = False,
            ease_type: str = "linear",
            visualization_type: str = "line",
            color: dict[str, float] | None = None,
            thickness: float = 0.1,
            speed: float = 1.0,
            look_ahead: float = 0.5,
            smooth_rotation: bool = True,
            bank_angle: float = 0.0,
            decelerate: bool = True,
            deceleration_time: float = 0.5,
            object_filter: str | None = None,
        ) -> dict[str, Any]:
            """Unity API operations portmanteau tool.

            Consolidates advanced Unity Editor API operations for complex automation.
            Most operations are currently scaffolded for future Unity Editor API integration.

            Args:
                operation: Operation to perform
                    - "execute_method": Execute Unity Editor method with full parameter support
                    - "get_scene_objects": Get all objects in Unity scene
                    - "modify_object": Modify Unity scene object properties
                    - "create_prefab": Create Unity prefab from scene object
                    - "run_simulation": Run Unity physics simulation
                    - "batch_operations": Execute multiple Unity operations in batch
                    - "move_along_path": Move object along a path
                    - "create_path_visualization": Create visual representation of a path
                    - "follow_path_2d": Move object along 2D path with forward-looking behavior
                    - "follow_path_3d": Move object along 3D path with banking
                    - "stop_path_movement": Stop object path movement
                class_name: Unity class name containing the method (for execute_method)
                method_name: Method name to execute (for execute_method)
                parameters: Parameters for method execution
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)
                wait_for_completion: Wait for method completion before returning
                object_name: Name of object to modify/move (for object operations)
                modifications: Dictionary of modifications to apply (for modify_object)
                prefab_name: Name for the new prefab (for create_prefab)
                duration: Simulation or movement duration in seconds
                record_data: Record object positions during simulation
                operations: List of operation dictionaries for batch execution
                path_type: Path type ("straight", "bezier", "spline", "catmull_rom")
                path_points: List of points defining the path
                loop: Whether to loop the path animation
                ease_type: Easing function ("linear", "ease_in", "ease_out", "ease_in_out")
                visualization_type: How to visualize ("line", "dotted", "waypoints", "full")
                color: Path color {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}
                thickness: Line thickness
                speed: Movement speed (units per second)
                look_ahead: Distance to look ahead for rotation
                smooth_rotation: Whether to smoothly rotate towards movement direction
                bank_angle: Maximum banking angle in degrees
                decelerate: Whether to decelerate smoothly when stopping
                deceleration_time: Time to decelerate in seconds
                object_filter: Optional filter pattern for scene objects

            Returns:
                Operation-specific result dictionary
            """

            if operation == "execute_method":
                return await self._api_execute_method(
                    class_name, method_name, parameters, project_path, scene_path, wait_for_completion
                )

            elif operation == "get_scene_objects":
                return await self._api_get_scene_objects(project_path, scene_path, object_filter)

            elif operation == "modify_object":
                return await self._api_modify_object(object_name, modifications, project_path, scene_path)

            elif operation == "create_prefab":
                return await self._api_create_prefab(object_name, prefab_name, project_path, scene_path)

            elif operation == "run_simulation":
                return await self._api_run_simulation(duration, project_path, scene_path, record_data)

            elif operation == "batch_operations":
                return await self._api_batch_operations(operations, project_path, scene_path)

            elif operation == "move_along_path":
                return await self._api_move_along_path(
                    object_name, path_type, path_points, duration, loop, ease_type, project_path, scene_path
                )

            elif operation == "create_path_visualization":
                return await self._api_create_path_visualization(
                    path_points, path_type, visualization_type, color, thickness, project_path, scene_path
                )

            elif operation == "follow_path_2d":
                return await self._api_follow_path_2d(
                    object_name, path_points, speed, look_ahead, smooth_rotation, project_path, scene_path
                )

            elif operation == "follow_path_3d":
                return await self._api_follow_path_3d(
                    object_name, path_points, speed, bank_angle, look_ahead, project_path, scene_path
                )

            elif operation == "stop_path_movement":
                return await self._api_stop_path_movement(
                    object_name, decelerate, deceleration_time, project_path, scene_path
                )

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "execute_method",
                        "get_scene_objects",
                        "modify_object",
                        "create_prefab",
                        "run_simulation",
                        "batch_operations",
                        "move_along_path",
                        "create_path_visualization",
                        "follow_path_2d",
                        "follow_path_3d",
                        "stop_path_movement",
                    ],
                }

    # Unity Editor API Implementation Methods (currently scaffolded)
    async def _api_execute_method(
        self,
        class_name: str | None,
        method_name: str | None,
        parameters: dict[str, Any] | None,
        project_path: str | None,
        scene_path: str | None,
        wait_for_completion: bool,
    ) -> dict[str, Any]:
        """Execute Unity Editor method via bridge when available, else CLI fallback hint."""
        if await bridge_available(self.bridge):
            return {
                "success": False,
                "mode": "bridge",
                "error": (
                    "Generic execute_method via bridge not yet implemented. "
                    "Use unity_core operation=execute_method for CLI batch execution."
                ),
                "class_name": class_name,
                "method_name": method_name,
            }
        return {
            "success": False,
            "error": "Unity Editor bridge not connected and CLI execute_method requires project_path",
            "class_name": class_name,
            "method_name": method_name,
            "parameters": parameters,
            "note": "Connect MCPBridge.cs or use unity_core execute_method",
        }

    async def _api_get_scene_objects(
        self,
        project_path: str | None,
        scene_path: str | None,
        object_filter: str | None,
    ) -> dict[str, Any]:
        """Get scene objects via Unity Editor bridge."""
        result = await execute_bridge_action("get_hierarchy", bridge=self.bridge)
        if not result.get("success"):
            return result

        hierarchy = result.get("result") or {}
        objects = hierarchy.get("objects", [])
        if object_filter:
            objects = [obj for obj in objects if object_filter.lower() in str(obj.get("name", "")).lower()]

        return {
            "success": True,
            "mode": "bridge",
            "object_count": len(objects),
            "objects": objects,
            "project_path": project_path,
            "scene_path": scene_path,
            "object_filter": object_filter,
        }

    async def _api_modify_object(
        self,
        object_name: str | None,
        modifications: dict[str, Any] | None,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Modify scene object via Unity Editor bridge."""
        if not object_name:
            return {"success": False, "error": "object_name required for modify_object"}

        mods = modifications or {}
        kwargs: dict[str, Any] = {"target": object_name}
        if "position" in mods:
            kwargs["position"] = mods["position"]
        if "rotation" in mods:
            kwargs["rotation"] = mods["rotation"]

        result = await execute_bridge_action("transform_object", bridge=self.bridge, **kwargs)
        if result.get("success"):
            result["object_name"] = object_name
            result["modifications"] = mods
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

    async def _api_create_prefab(
        self,
        object_name: str | None,
        prefab_name: str | None,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Create prefab via Unity Editor bridge."""
        if not object_name:
            return {"success": False, "error": "object_name required for create_prefab"}

        prefab_path = prefab_name
        if prefab_path and not prefab_path.startswith("Assets/"):
            if prefab_path.endswith(".prefab"):
                prefab_path = f"Assets/Prefabs/{prefab_path}"
            else:
                prefab_path = f"Assets/Prefabs/{prefab_path}.prefab"

        result = await execute_bridge_action(
            "create_prefab",
            bridge=self.bridge,
            target=object_name,
            prefab_path=prefab_path,
            name=prefab_name,
        )
        if result.get("success"):
            result["object_name"] = object_name
            result["prefab_name"] = prefab_name
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

    async def _api_run_simulation(
        self,
        duration: float,
        project_path: str | None,
        scene_path: str | None,
        record_data: bool,
    ) -> dict[str, Any]:
        """Run physics simulation via Unity Editor bridge (play mode)."""
        from unity3d_mcp.utils.simulation_runner import run_bridge_simulation

        result = await run_bridge_simulation(
            duration=duration,
            record_data=record_data,
            timeout=max(duration * 3, 30.0),
            bridge=self.bridge,
        )
        if project_path:
            result["project_path"] = project_path
        if scene_path:
            result["scene_path"] = scene_path
        return result

    async def _api_batch_operations(
        self,
        operations: list[dict[str, Any]] | None,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Execute batch operations via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "operation_count": len(operations) if operations else 0,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_move_along_path(
        self,
        object_name: str | None,
        path_type: str,
        path_points: list[dict[str, float]] | None,
        duration: float,
        loop: bool,
        ease_type: str,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Move object along path via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "path_type": path_type,
            "points_count": len(path_points) if path_points else 0,
            "duration": duration,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_create_path_visualization(
        self,
        path_points: list[dict[str, float]] | None,
        path_type: str,
        visualization_type: str,
        color: dict[str, float] | None,
        thickness: float,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Create path visualization via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "path_type": path_type,
            "visualization_type": visualization_type,
            "points_count": len(path_points) if path_points else 0,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_follow_path_2d(
        self,
        object_name: str | None,
        path_points: list[dict[str, float]] | None,
        speed: float,
        look_ahead: float,
        smooth_rotation: bool,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Follow 2D path via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "path_length": len(path_points) if path_points else 0,
            "speed": speed,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_follow_path_3d(
        self,
        object_name: str | None,
        path_points: list[dict[str, float]] | None,
        speed: float,
        bank_angle: float,
        look_ahead: float,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Follow 3D path with banking via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "path_length": len(path_points) if path_points else 0,
            "banking_enabled": bank_angle > 0,
            "note": "API tools scaffolded for future Unity Editor integration",
        }

    async def _api_stop_path_movement(
        self,
        object_name: str | None,
        decelerate: bool,
        deceleration_time: float,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Stop path movement via Unity Editor API."""
        return {
            "success": False,
            "error": "Unity Editor API not yet implemented",
            "object_name": object_name,
            "deceleration_applied": decelerate,
            "note": "API tools scaffolded for future Unity Editor integration",
        }
