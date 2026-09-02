"""
Unity API Portmanteau Tool Manager

Consolidates advanced Unity Editor API operations into a unified portmanteau interface.
All operations call the real MCPBridge.cs Editor bridge (HTTP, localhost:10835) when
Unity is running with the bridge installed. If the bridge isn't connected, each
operation returns an honest "bridge not connected" error rather than a fake result.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from ...utils.unity_runtime import execute_bridge_action, get_bridge_client
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
            position: list[float] | None = None,
            fixture: str | None = None,
            anim_mode: str = "spin",
            axis: list[float] | None = None,
            amplitude: float = 0.1,
            damping: float = 0.6,
        ) -> dict[str, Any]:
            """Unity API operations portmanteau tool.

            Consolidates advanced Unity Editor API operations for complex automation.
            All operations require a live Unity Editor session with MCPBridge.cs
            installed and running (HTTP bridge on localhost:10835); if the bridge
            isn't connected, each operation returns an honest "not connected"
            error rather than a fake success.

            Args:
                operation: Operation to perform
                    - "execute_method": Invoke a public static PARAMETERLESS Unity
                      method by name (same constraint as Unity's -executeMethod CLI
                      flag - parameterized calls are not supported)
                    - "get_scene_objects": Get all objects in Unity scene
                    - "modify_object": Modify Unity scene object properties
                    - "create_prefab": Create Unity prefab from scene object
                    - "run_simulation": Run Unity physics simulation
                    - "batch_operations": Execute multiple Unity operations in batch
                    - "move_along_path": Move object along a path (curve types are
                      approximated as straight multi-segment interpolation, not true
                      bezier/spline math)
                    - "create_path_visualization": Create a real LineRenderer tracing the path
                    - "follow_path_2d": Move object along 2D path with forward-looking behavior
                    - "follow_path_3d": Move object along 3D path with banking
                    - "stop_path_movement": Stop object path movement
                    - "animate_object": Loop-animate an object in place - spin (continuous
                      rotation), bob (sinusoidal oscillation), or bounce (real drop-and-rebound
                      physics, not a sine wave - the identical closed-form function already
                      shipped in overte-mcp/resonite-mcp, ported to C# unchanged). Fire-and-
                      forget: ticks inside the Editor's Update() loop and keeps running after
                      this call returns; use "stop_animation" to end it, or pass duration>0 to
                      auto-stop. Requires MCPBridge.cs 2026-09-03+ (adds animate_object/
                      stop_animation actions) - older copies of the bridge script will 404 with
                      "Unknown action".
                    - "stop_animation": Stop an in-progress animate_object animation
                    - "fixture_spawn": Spawn a preset test fixture (box/cup/ball/table/chair)
                      for gripper/manipulation testing - same preset dimensions as overte-mcp/
                      resonite-mcp's equivalent, built from Unity's native Cube/Sphere
                      primitives (no custom mesh generation needed, unlike resonite-mcp's
                      icosahedron ball). Multi-part fixtures (table/chair) spawn as several
                      independent same-colored objects. Also requires MCPBridge.cs 2026-09-03+
                      (uses create_object's new dimensions/color fields).
                class_name: Unity class name containing the method (for execute_method)
                method_name: Method name to execute (for execute_method)
                parameters: Parameters for method execution
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)
                wait_for_completion: Wait for method completion before returning
                object_name: Name of object to modify/move (for object operations); also the
                    target to animate/stop for animate_object/stop_animation, and the base
                    name for the new fixture in fixture_spawn (defaults to the fixture name)
                modifications: Dictionary of modifications to apply (for modify_object)
                prefab_name: Name for the new prefab (for create_prefab)
                duration: Simulation or movement duration in seconds; for animate_object,
                    <=0 (the default) means run until stop_animation is called instead of
                    auto-stopping
                record_data: Record object positions during simulation
                operations: List of operation dictionaries for batch execution
                path_type: Path type ("straight", "bezier", "spline", "catmull_rom")
                path_points: List of points defining the path
                loop: Whether to loop the path animation
                ease_type: Easing function ("linear", "ease_in", "ease_out", "ease_in_out")
                visualization_type: How to visualize ("line", "dotted", "waypoints", "full")
                color: Path color {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}; also fixture_spawn's
                    color, applied uniformly to every part of a multi-part fixture (defaults
                    to Unity's default material color if omitted, not white)
                thickness: Line thickness
                speed: Movement speed (units per second); for animate_object, "spin" is
                    degrees/second (Unity's native Quaternion.AngleAxis convention - NOT
                    radians/second like overte-mcp/resonite-mcp's animate tools), "bob" is
                    oscillations/second, "bounce" scales effective gravity
                look_ahead: Distance to look ahead for rotation
                smooth_rotation: Whether to smoothly rotate towards movement direction
                bank_angle: Maximum banking angle in degrees
                decelerate: Whether to decelerate smoothly when stopping
                deceleration_time: Time to decelerate in seconds
                object_filter: Optional filter pattern for scene objects
                position: [x, y, z] world position (fixture_spawn - where to place it,
                    defaults to the world origin if omitted; Unity Editor has no concept of
                    "the user's" viewpoint to default to instead, unlike overte-mcp/
                    resonite-mcp's live-VR equivalents)
                fixture: Fixture preset name for fixture_spawn: "box", "cup", "ball",
                    "table", or "chair"
                anim_mode: animate_object mode: "spin", "bob", or "bounce"
                axis: [x, y, z] rotation axis for animate_object's "spin" mode (normalized)
                amplitude: animate_object "bob"/"bounce": peak height above the rest
                    position, in meters
                damping: animate_object "bounce" only: energy retained per bounce, 0-1

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

            elif operation == "animate_object":
                return await self._api_animate_object(
                    object_name, anim_mode, axis, speed, amplitude, damping, duration, project_path, scene_path
                )

            elif operation == "stop_animation":
                return await self._api_stop_animation(object_name, project_path, scene_path)

            elif operation == "fixture_spawn":
                return await self._api_fixture_spawn(fixture, position, object_name, color, project_path, scene_path)

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
                        "animate_object",
                        "stop_animation",
                        "fixture_spawn",
                    ],
                }

    # Unity Editor API Implementation Methods (bridge-backed via MCPBridge.cs)
    async def _api_execute_method(
        self,
        class_name: str | None,
        method_name: str | None,
        parameters: dict[str, Any] | None,
        project_path: str | None,
        scene_path: str | None,
        wait_for_completion: bool,
    ) -> dict[str, Any]:
        """Invoke a public static PARAMETERLESS method via the Editor bridge.

        This mirrors Unity's own `-executeMethod` CLI constraint (public,
        static, no parameters) rather than attempting unsafe arbitrary
        parameter marshaling. If `parameters` is non-empty it is reported
        back as ignored, not silently dropped.
        """
        if not class_name or not method_name:
            return {"success": False, "error": "class_name and method_name are required"}

        result = await execute_bridge_action(
            "execute_method",
            bridge=self.bridge,
            class_name=class_name,
            method_name=method_name,
        )
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
            if parameters:
                result["parameters_ignored"] = parameters
                result["note"] = (
                    "The bridge only supports public static parameterless methods "
                    "(same constraint as Unity's -executeMethod CLI flag). The "
                    "parameters you passed were NOT sent or applied."
                )
        return result

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
        """Execute a list of sub-commands sequentially via the Editor bridge.

        Each entry in `operations` must use the same flat command shape as a
        top-level bridge action (action/target/name/...) - Unity's
        JsonUtility can't deserialize free-form heterogeneous dicts, so the
        bridge reuses one schema recursively rather than a per-op schema.
        """
        if not operations:
            return {"success": False, "error": "operations list is required and must be non-empty"}

        result = await execute_bridge_action(
            "batch_operations",
            bridge=self.bridge,
            operations=operations,
        )
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

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
        """Move object along a path via the Editor bridge.

        Curve `path_type`s (bezier/spline/catmull_rom) are approximated as
        straight multi-segment linear interpolation on the C# side - real
        curve math is not implemented, and the bridge response says so.
        """
        if not object_name:
            return {"success": False, "error": "object_name required for move_along_path"}
        if not path_points or len(path_points) < 2:
            return {"success": False, "error": "path_points must contain at least 2 points"}

        result = await execute_bridge_action(
            "move_along_path",
            bridge=self.bridge,
            target=object_name,
            path_points=path_points,
            path_type=path_type,
            duration=duration,
            loop=loop,
            ease_type=ease_type,
        )
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

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
        """Create a real LineRenderer GameObject tracing the path via the Editor bridge.

        `visualization_type` values other than "line" ("dotted", "waypoints",
        "full") are accepted but the bridge currently only draws a plain
        LineRenderer - not yet a distinct rendering per type.
        """
        if not path_points or len(path_points) < 2:
            return {"success": False, "error": "path_points must contain at least 2 points"}

        result = await execute_bridge_action(
            "create_path_visualization",
            bridge=self.bridge,
            path_points=path_points,
            path_type=path_type,
            visualization_type=visualization_type,
            color=color,
            thickness=thickness,
        )
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
            if visualization_type != "line":
                result["note"] = (
                    f"visualization_type='{visualization_type}' requested, but the bridge "
                    "only draws a plain LineRenderer today - 'dotted'/'waypoints'/'full' "
                    "rendering variants are not yet implemented."
                )
        return result

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
        """Follow a 2D path via the Editor bridge (Y locked to the object's current height)."""
        if not object_name:
            return {"success": False, "error": "object_name required for follow_path_2d"}
        if not path_points or len(path_points) < 2:
            return {"success": False, "error": "path_points must contain at least 2 points"}

        result = await execute_bridge_action(
            "follow_path_2d",
            bridge=self.bridge,
            target=object_name,
            path_points=path_points,
            speed=speed,
            look_ahead=look_ahead,
            smooth_rotation=smooth_rotation,
        )
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

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
        """Follow a 3D path with optional banking via the Editor bridge."""
        if not object_name:
            return {"success": False, "error": "object_name required for follow_path_3d"}
        if not path_points or len(path_points) < 2:
            return {"success": False, "error": "path_points must contain at least 2 points"}

        result = await execute_bridge_action(
            "follow_path_3d",
            bridge=self.bridge,
            target=object_name,
            path_points=path_points,
            speed=speed,
            bank_angle=bank_angle,
            look_ahead=look_ahead,
        )
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

    async def _api_stop_path_movement(
        self,
        object_name: str | None,
        decelerate: bool,
        deceleration_time: float,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Stop an in-progress path movement via the Editor bridge.

        With `decelerate=True` the bridge ramps speed to zero over
        `deceleration_time` seconds (ticked on subsequent Editor frames)
        rather than stopping instantly.
        """
        if not object_name:
            return {"success": False, "error": "object_name required for stop_path_movement"}

        result = await execute_bridge_action(
            "stop_path_movement",
            bridge=self.bridge,
            target=object_name,
            decelerate=decelerate,
            deceleration_time=deceleration_time,
        )
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

    # -- Backport from overte-mcp/resonite-mcp (2026-09-03): loop-animate + fixture spawn --

    async def _api_animate_object(
        self,
        object_name: str | None,
        anim_mode: str,
        axis: list[float] | None,
        speed: float,
        amplitude: float,
        damping: float,
        duration: float,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Start a loop animation (spin/bob/bounce) on an object via the Editor bridge.

        Unlike overte-mcp/resonite-mcp's Python-side blocking loop (repeated WebSocket
        updates for duration_s), this is fire-and-forget: MCPBridge.cs ticks the animation
        itself inside the Editor's own Update() loop and this call returns immediately once
        the animation has started - a better fit for Unity's architecture (there's already a
        proven precedent for this exact pattern in move_along_path/stop_path_movement) than
        porting the blocking-call shape unchanged. duration<=0 (the default) means it runs
        until stop_animation is called; duration>0 auto-stops after that many seconds.
        """
        if not object_name:
            return {"success": False, "error": "object_name required for animate_object"}
        if anim_mode not in ("spin", "bob", "bounce"):
            return {"success": False, "error": "anim_mode must be 'spin', 'bob', or 'bounce'"}

        kwargs: dict[str, Any] = {
            "target": object_name,
            "anim_mode": anim_mode,
            "speed": speed,
            "amplitude": amplitude,
            "damping": damping,
            "duration": duration,
        }
        if axis is not None and len(axis) == 3:
            kwargs["axis"] = axis

        result = await execute_bridge_action("animate_object", bridge=self.bridge, **kwargs)
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

    async def _api_stop_animation(
        self,
        object_name: str | None,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Stop an in-progress animate_object animation via the Editor bridge."""
        if not object_name:
            return {"success": False, "error": "object_name required for stop_animation"}

        result = await execute_bridge_action("stop_animation", bridge=self.bridge, target=object_name)
        if result.get("success"):
            result["project_path"] = project_path
            result["scene_path"] = scene_path
        return result

    # Same preset dimensions (meters) as overte-mcp's FIXTURE_PRESETS/resonite-mcp's
    # FIXTURE_PRESETS, built from Unity's own primitives - Unity's Cube/Sphere primitive
    # meshes are exactly 1x1x1/diameter-1 at scale (1,1,1), so `dims` maps straight onto
    # create_object's `dimensions` field with no per-primitive conversion, unlike
    # resonite-mcp's port (which had to hand-build box/icosahedron mesh JSON because
    # ResoniteLink has no built-in primitive-mesh components to call instead).
    _FIXTURE_PRESETS: dict[str, list[dict[str, Any]]] = {
        "box": [
            {"type": "Box", "offset": (0.0, 0.05, 0.0), "dims": (0.1, 0.1, 0.1)},
        ],
        "cup": [
            {"type": "Box", "offset": (0.0, 0.05, 0.0), "dims": (0.08, 0.10, 0.08)},
        ],
        "ball": [
            {"type": "Sphere", "offset": (0.0, 0.035, 0.0), "dims": (0.07, 0.07, 0.07)},
        ],
        "table": [
            {"type": "Box", "offset": (0.0, 0.715, 0.0), "dims": (1.2, 0.05, 0.6)},
            {"type": "Box", "offset": (0.0, 0.35, 0.0), "dims": (0.08, 0.70, 0.08)},
        ],
        "chair": [
            {"type": "Box", "offset": (0.0, 0.45, 0.0), "dims": (0.4, 0.05, 0.4)},
            {"type": "Box", "offset": (0.0, 0.70, -0.18), "dims": (0.4, 0.5, 0.05)},
            {"type": "Box", "offset": (0.0, 0.225, 0.0), "dims": (0.35, 0.45, 0.35)},
        ],
    }

    async def _api_fixture_spawn(
        self,
        fixture: str | None,
        position: list[float] | None,
        object_name: str | None,
        color: dict[str, float] | None,
        project_path: str | None,
        scene_path: str | None,
    ) -> dict[str, Any]:
        """Spawn a preset test fixture (box/cup/ball/table/chair) via repeated create_object
        calls. Multi-part fixtures (table/chair) spawn as several independent same-colored
        objects, not parented - static set-dressing that never needs to move as a unit.

        No avatar-relative default placement exists here (unlike overte-mcp's version) -
        there's no "the user's viewpoint" concept in the Unity Editor to default to, so
        `position` defaults to the world origin if omitted, not somewhere near a person.
        """
        if not fixture or fixture not in self._FIXTURE_PRESETS:
            return {
                "success": False,
                "error": f"Unknown fixture {fixture!r}. Known: {sorted(self._FIXTURE_PRESETS)}",
            }
        parts = self._FIXTURE_PRESETS[fixture]
        base = position if position and len(position) == 3 else [0.0, 0.0, 0.0]
        base_name = object_name or fixture

        instance_ids = []
        for i, part in enumerate(parts):
            ox, oy, oz = part["offset"]
            kwargs: dict[str, Any] = {
                "name": f"{base_name}_{i}" if len(parts) > 1 else base_name,
                "type": part["type"],
                "position": [base[0] + ox, base[1] + oy, base[2] + oz],
                "dimensions": list(part["dims"]),
            }
            if color is not None:
                kwargs["color"] = color

            result = await execute_bridge_action("create_object", bridge=self.bridge, **kwargs)
            if not result.get("success"):
                return {
                    "success": False,
                    "error": f"Fixture part {i} failed: {result.get('error', 'unknown error')}",
                    "fixture": fixture,
                    "instance_ids": instance_ids,
                }
            instance_ids.append(result.get("result", {}).get("instanceID"))

        return {
            "success": True,
            "mode": "bridge",
            "fixture": fixture,
            "instance_ids": instance_ids,
            "position": {"x": base[0], "y": base[1], "z": base[2]},
            "project_path": project_path,
            "scene_path": scene_path,
        }
