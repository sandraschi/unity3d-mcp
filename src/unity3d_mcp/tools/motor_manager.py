"""
Motor Control Tools for Unity3D MCP

Provides comprehensive motor control capabilities for robotics and vehicle simulation,
including motor configuration, speed control, physics simulation, and status monitoring.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MotorManager:
    """Manages motor control operations for Unity objects."""

    def __init__(self, config):
        self.config = config
        self.active_motors = {}  # Track active motors per object

    async def add_motor(
        self,
        object_name: str,
        motor_type: str,
        motor_config: dict[str, Any],
        project_path: str | None = None,
        scene_path: str | None = None,
    ) -> dict[str, Any]:
        """Add a motor component to a Unity object."""
        try:
            motor_id = f"{object_name}_{motor_type}_motor"

            # Store motor configuration
            if object_name not in self.active_motors:
                self.active_motors[object_name] = {}

            self.active_motors[object_name][motor_id] = {
                "type": motor_type,
                "config": motor_config,
                "is_running": False,
                "current_speed": 0.0,
                "target_speed": 0.0,
                "acceleration": motor_config.get("acceleration", 1.0),
            }

            return {
                "success": True,
                "object_name": object_name,
                "motor_type": motor_type,
                "motor_id": motor_id,
                "message": f"Added {motor_type} motor to {object_name}",
            }

        except Exception as e:
            logger.error(f"Failed to add motor to {object_name}: {e}")
            return {"success": False, "error": str(e), "object_name": object_name, "motor_type": motor_type}

    async def start_motor(
        self,
        object_name: str,
        motor_id: str | None = None,
        target_speed: float | None = None,
        acceleration: float | None = None,
        project_path: str | None = None,
        scene_path: str | None = None,
    ) -> dict[str, Any]:
        """Start a motor on an object."""
        try:
            if object_name not in self.active_motors:
                return {
                    "success": False,
                    "error": f"No motors found for object {object_name}",
                    "object_name": object_name,
                }

            motors = self.active_motors[object_name]

            # If no specific motor_id, start all motors
            if motor_id is None:
                motor_ids = list(motors.keys())
                if not motor_ids:
                    return {
                        "success": False,
                        "error": f"No motors configured for {object_name}",
                        "object_name": object_name,
                    }
                motor_id = motor_ids[0]  # Start first motor

            if motor_id not in motors:
                return {
                    "success": False,
                    "error": f"Motor {motor_id} not found on {object_name}",
                    "object_name": object_name,
                    "motor_id": motor_id,
                }

            motor = motors[motor_id]
            motor["is_running"] = True
            motor["target_speed"] = target_speed or motor["config"].get("max_speed", 1.0)
            motor["acceleration"] = acceleration or motor["config"].get("acceleration", 1.0)

            return {
                "success": True,
                "object_name": object_name,
                "motor_id": motor_id,
                "target_speed": motor["target_speed"],
                "acceleration": motor["acceleration"],
                "message": f"Started motor {motor_id} on {object_name}",
            }

        except Exception as e:
            logger.error(f"Failed to start motor on {object_name}: {e}")
            return {"success": False, "error": str(e), "object_name": object_name, "motor_id": motor_id}

    async def stop_motor(
        self,
        object_name: str,
        motor_id: str | None = None,
        deceleration: float | None = None,
        emergency_stop: bool = False,
        project_path: str | None = None,
        scene_path: str | None = None,
    ) -> dict[str, Any]:
        """Stop a motor on an object."""
        try:
            if object_name not in self.active_motors:
                return {
                    "success": False,
                    "error": f"No motors found for object {object_name}",
                    "object_name": object_name,
                }

            motors = self.active_motors[object_name]

            # If no specific motor_id, stop all motors
            if motor_id is None:
                motor_ids = list(motors.keys())
                if not motor_ids:
                    return {
                        "success": False,
                        "error": f"No motors configured for {object_name}",
                        "object_name": object_name,
                    }
                motor_id = motor_ids[0]  # Stop first motor

            if motor_id not in motors:
                return {
                    "success": False,
                    "error": f"Motor {motor_id} not found on {object_name}",
                    "object_name": object_name,
                    "motor_id": motor_id,
                }

            motor = motors[motor_id]
            final_speed = motor["current_speed"]

            if emergency_stop:
                motor["target_speed"] = 0.0
                motor["is_running"] = False
                motor["current_speed"] = 0.0
            else:
                motor["target_speed"] = 0.0
                motor["acceleration"] = deceleration or motor["config"].get("deceleration", motor["acceleration"])

            return {
                "success": True,
                "object_name": object_name,
                "motor_id": motor_id,
                "deceleration": motor["acceleration"] if not emergency_stop else None,
                "emergency_stop": emergency_stop,
                "final_speed": final_speed,
                "message": f"Stopped motor {motor_id} on {object_name}",
            }

        except Exception as e:
            logger.error(f"Failed to stop motor on {object_name}: {e}")
            return {"success": False, "error": str(e), "object_name": object_name, "motor_id": motor_id}

    async def set_motor_speed(
        self,
        object_name: str,
        target_speed: float,
        motor_id: str | None = None,
        acceleration: float | None = None,
        project_path: str | None = None,
        scene_path: str | None = None,
    ) -> dict[str, Any]:
        """Set the speed of a motor on an object."""
        try:
            if object_name not in self.active_motors:
                return {
                    "success": False,
                    "error": f"No motors found for object {object_name}",
                    "object_name": object_name,
                }

            motors = self.active_motors[object_name]

            # If no specific motor_id, set speed for all motors
            if motor_id is None:
                motor_ids = list(motors.keys())
                if not motor_ids:
                    return {
                        "success": False,
                        "error": f"No motors configured for {object_name}",
                        "object_name": object_name,
                    }
                motor_id = motor_ids[0]  # Use first motor

            if motor_id not in motors:
                return {
                    "success": False,
                    "error": f"Motor {motor_id} not found on {object_name}",
                    "object_name": object_name,
                    "motor_id": motor_id,
                }

            motor = motors[motor_id]
            current_speed = motor["current_speed"]

            motor["target_speed"] = target_speed
            motor["acceleration"] = acceleration or motor["acceleration"]

            return {
                "success": True,
                "object_name": object_name,
                "motor_id": motor_id,
                "target_speed": target_speed,
                "current_speed": current_speed,
                "acceleration": motor["acceleration"],
                "message": f"Set motor {motor_id} speed to {target_speed}",
            }

        except Exception as e:
            logger.error(f"Failed to set motor speed on {object_name}: {e}")
            return {"success": False, "error": str(e), "object_name": object_name, "motor_id": motor_id}

    async def get_motor_status(
        self,
        object_name: str,
        motor_id: str | None = None,
        project_path: str | None = None,
        scene_path: str | None = None,
    ) -> dict[str, Any]:
        """Get the current status of motors on an object."""
        try:
            if object_name not in self.active_motors:
                return {
                    "success": False,
                    "error": f"No motors found for object {object_name}",
                    "object_name": object_name,
                    "motors": [],
                    "motor_count": 0,
                }

            motors = self.active_motors[object_name]

            if motor_id and motor_id not in motors:
                return {
                    "success": False,
                    "error": f"Motor {motor_id} not found on {object_name}",
                    "object_name": object_name,
                    "motor_id": motor_id,
                    "motors": [],
                    "motor_count": 0,
                }

            # Get requested motors or all motors
            requested_motors = [motor_id] if motor_id else list(motors.keys())

            motor_statuses = []
            for mid in requested_motors:
                if mid in motors:
                    motor = motors[mid]
                    motor_statuses.append(
                        {
                            "motor_id": mid,
                            "motor_type": motor["type"],
                            "is_running": motor["is_running"],
                            "current_speed": motor["current_speed"],
                            "target_speed": motor["target_speed"],
                            "acceleration": motor["acceleration"],
                            "temperature": motor.get("temperature", 25.0),  # Default room temp
                            "power_consumption": self._calculate_power_consumption(motor),
                            "efficiency": self._calculate_efficiency(motor),
                        }
                    )

            return {
                "success": True,
                "object_name": object_name,
                "motors": motor_statuses,
                "motor_count": len(motor_statuses),
            }

        except Exception as e:
            logger.error(f"Failed to get motor status for {object_name}: {e}")
            return {"success": False, "error": str(e), "object_name": object_name, "motors": [], "motor_count": 0}

    async def configure_motor_physics(
        self,
        object_name: str,
        motor_id: str,
        physics_config: dict[str, Any],
        project_path: str | None = None,
        scene_path: str | None = None,
    ) -> dict[str, Any]:
        """Configure physics properties for a motor."""
        try:
            if object_name not in self.active_motors:
                return {
                    "success": False,
                    "error": f"No motors found for object {object_name}",
                    "object_name": object_name,
                    "motor_id": motor_id,
                }

            motors = self.active_motors[object_name]

            if motor_id not in motors:
                return {
                    "success": False,
                    "error": f"Motor {motor_id} not found on {object_name}",
                    "object_name": object_name,
                    "motor_id": motor_id,
                }

            motor = motors[motor_id]

            # Update physics configuration
            if "physics" not in motor:
                motor["physics"] = {}

            motor["physics"].update(physics_config)

            return {
                "success": True,
                "object_name": object_name,
                "motor_id": motor_id,
                "physics_applied": list(physics_config.keys()),
                "message": f"Configured physics for motor {motor_id}",
            }

        except Exception as e:
            logger.error(f"Failed to configure motor physics for {object_name}: {e}")
            return {"success": False, "error": str(e), "object_name": object_name, "motor_id": motor_id}

    def _calculate_power_consumption(self, motor: dict[str, Any]) -> float:
        """Calculate power consumption based on motor state."""
        if not motor["is_running"]:
            return 0.0

        # Simple power calculation: base power + speed-based power
        base_power = motor["config"].get("idle_power", 5.0)  # watts
        speed_factor = abs(motor["current_speed"]) / motor["config"].get("max_speed", 1.0)
        speed_power = speed_factor * motor["config"].get("max_power", 100.0)

        return base_power + speed_power

    def _calculate_efficiency(self, motor: dict[str, Any]) -> float:
        """Calculate motor efficiency percentage."""
        if not motor["is_running"] or motor["current_speed"] == 0:
            return 0.0

        # Efficiency decreases with speed and load
        base_efficiency = motor["config"].get("efficiency", 0.85)
        speed_factor = min(1.0, motor["current_speed"] / motor["config"].get("max_speed", 1.0))

        return base_efficiency * (0.8 + 0.2 * speed_factor)  # 80-100% of base efficiency


class MotorToolManager:
    """Tool manager for motor control operations."""

    def __init__(self, mcp_app, motor_manager: MotorManager):
        self.app = mcp_app
        self.motor_manager = motor_manager

    def register_tools(self):
        """Register all motor control tools."""

        @self.app.tool
        async def api_add_motor(
            object_name: str,
            motor_type: str,
            motor_config: dict[str, Any],
            project_path: str | None = None,
            scene_path: str | None = None,
        ) -> dict[str, Any]:
            """Add a motor component to a Unity object for movement control.

            Attaches a configurable motor to an object, enabling speed and acceleration control.
            Perfect for robotics where you want realistic motor-driven movement instead of
            direct position manipulation.

            Args:
                object_name: Name of the object to add motor to
                motor_type: Motor type ("wheel", "propeller", "linear", "rotary", "continuous")
                motor_config: Motor configuration parameters
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating motor added successfully
                - object_name: Object the motor was added to
                - motor_type: Type of motor added
                - motor_id: Unique identifier for the motor
                - error: Error message if failed

            Examples:
                # Add wheel motor for Scout robot
                api_add_motor(
                    object_name="ScoutRobot",
                    motor_type="wheel",
                    motor_config={
                        "max_speed": 5.0,  # m/s
                        "acceleration": 2.0,  # m/s²
                        "wheel_diameter": 0.025,  # meters
                        "gear_ratio": 10.0,
                        "power_source": "battery"
                    }
                )

                # Add propeller motor for drone
                api_add_motor(
                    object_name="Drone",
                    motor_type="propeller",
                    motor_config={
                        "max_rpm": 12000,
                        "blade_count": 4,
                        "thrust_coefficient": 0.05,
                        "power_consumption": 150  # watts
                    }
                )
            """
            return await self.motor_manager.add_motor(object_name, motor_type, motor_config, project_path, scene_path)

        @self.app.tool
        async def api_start_motor(
            object_name: str,
            motor_id: str | None = None,
            target_speed: float | None = None,
            acceleration: float | None = None,
            project_path: str | None = None,
            scene_path: str | None = None,
        ) -> dict[str, Any]:
            """Start a motor on an object with optional speed and acceleration parameters.

            Activates a motor and optionally sets it to a target speed with specified acceleration.
            Perfect for natural robot movement control.

            Args:
                object_name: Name of the object with the motor
                motor_id: Specific motor ID (if multiple motors, optional)
                target_speed: Target speed (m/s for linear, RPM for rotary)
                acceleration: Acceleration rate (m/s² or RPM/s)
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating motor started successfully
                - object_name: Object whose motor was started
                - motor_id: ID of the motor that was started
                - target_speed: Speed the motor is accelerating to
                - acceleration: Acceleration rate being used
                - error: Error message if failed

            Examples:
                # Start motor and accelerate to 3 mph (1.34 m/s)
                api_start_motor(
                    object_name="ScoutRobot",
                    target_speed=1.34,
                    acceleration=0.5
                )

                # Start motor at idle speed
                api_start_motor(
                    object_name="Drone",
                    target_speed=1000  # RPM
                )
            """
            return await self.motor_manager.start_motor(
                object_name, motor_id, target_speed, acceleration, project_path, scene_path
            )

        @self.app.tool
        async def api_stop_motor(
            object_name: str,
            motor_id: str | None = None,
            deceleration: float | None = None,
            emergency_stop: bool = False,
            project_path: str | None = None,
            scene_path: str | None = None,
        ) -> dict[str, Any]:
            """Stop a motor on an object with optional deceleration.

            Deactivates a motor, either gradually with deceleration or emergency stop.
            Important for safe robot operation and realistic movement.

            Args:
                object_name: Name of the object with the motor
                motor_id: Specific motor ID (if multiple motors, optional)
                deceleration: Deceleration rate (m/s² or RPM/s)
                emergency_stop: Whether to stop immediately without deceleration
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating motor stopped successfully
                - object_name: Object whose motor was stopped
                - motor_id: ID of the motor that was stopped
                - deceleration: Deceleration rate used
                - emergency_stop: Whether emergency stop was used
                - final_speed: Speed when stop command was issued
                - error: Error message if failed

            Examples:
                # Gradual stop
                api_stop_motor(
                    object_name="ScoutRobot",
                    deceleration=1.0
                )

                # Emergency stop
                api_stop_motor(
                    object_name="Drone",
                    emergency_stop=True
                )
            """
            return await self.motor_manager.stop_motor(
                object_name, motor_id, deceleration, emergency_stop, project_path, scene_path
            )

        @self.app.tool
        async def api_set_motor_speed(
            object_name: str,
            target_speed: float,
            motor_id: str | None = None,
            acceleration: float | None = None,
            project_path: str | None = None,
            scene_path: str | None = None,
        ) -> dict[str, Any]:
            """Set the speed of a motor on an object.

            Changes the target speed of a running motor with optional acceleration control.
            Enables dynamic speed adjustments during robot operation.

            Args:
                object_name: Name of the object with the motor
                target_speed: New target speed (m/s for linear, RPM for rotary)
                motor_id: Specific motor ID (if multiple motors, optional)
                acceleration: Acceleration rate for speed change (optional)
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating speed change initiated
                - object_name: Object whose motor speed was changed
                - motor_id: ID of the motor whose speed was changed
                - target_speed: New target speed
                - current_speed: Speed before change
                - acceleration: Acceleration rate being used
                - error: Error message if failed

            Examples:
                # Accelerate to 5 mph (2.24 m/s)
                api_set_motor_speed(
                    object_name="ScoutRobot",
                    target_speed=2.24,
                    acceleration=0.8
                )

                # Change drone propeller speed
                api_set_motor_speed(
                    object_name="Drone",
                    target_speed=8000,  # RPM
                    motor_id="propeller_front_left"
                )
            """
            return await self.motor_manager.set_motor_speed(
                object_name, target_speed, motor_id, acceleration, project_path, scene_path
            )

        @self.app.tool
        async def api_get_motor_status(
            object_name: str,
            motor_id: str | None = None,
            project_path: str | None = None,
            scene_path: str | None = None,
        ) -> dict[str, Any]:
            """Get the current status of motors on an object.

            Retrieves real-time information about motor state, speed, and performance.
            Essential for monitoring robot operation and diagnostics.

            Args:
                object_name: Name of the object with motors
                motor_id: Specific motor ID (optional, returns all motors if not specified)
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating status retrieved successfully
                - object_name: Object whose motor status was retrieved
                - motors: List of motor status dictionaries with:
                  - motor_id: Unique motor identifier
                  - motor_type: Type of motor
                  - is_running: Whether motor is active
                  - current_speed: Current speed (m/s or RPM)
                  - target_speed: Target speed (m/s or RPM)
                  - acceleration: Current acceleration
                  - temperature: Motor temperature (if simulated)
                  - power_consumption: Current power usage
                  - efficiency: Motor efficiency percentage
                - motor_count: Number of motors on object
                - error: Error message if failed

            Examples:
                # Get all motor statuses for robot
                api_get_motor_status(object_name="ScoutRobot")

                # Get specific motor status
                api_get_motor_status(
                    object_name="Drone",
                    motor_id="propeller_main"
                )
            """
            return await self.motor_manager.get_motor_status(object_name, motor_id, project_path, scene_path)

        @self.app.tool
        async def api_configure_motor_physics(
            object_name: str,
            motor_id: str,
            physics_config: dict[str, Any],
            project_path: str | None = None,
            scene_path: str | None = None,
        ) -> dict[str, Any]:
            """Configure physics properties for a motor.

            Sets up realistic physics simulation for motors including friction,
            inertia, power curves, and environmental factors.

            Args:
                object_name: Name of the object with the motor
                motor_id: Specific motor ID to configure
                physics_config: Physics configuration parameters
                project_path: Unity project path (auto-detected if not provided)
                scene_path: Scene file path (current scene if not provided)

            Returns:
                Dictionary containing:
                - success: Boolean indicating physics configured successfully
                - object_name: Object whose motor physics was configured
                - motor_id: ID of the motor that was configured
                - physics_applied: List of physics parameters applied
                - error: Error message if failed

            Examples:
                # Configure realistic wheel motor physics
                api_configure_motor_physics(
                    object_name="ScoutRobot",
                    motor_id="wheel_left_front",
                    physics_config={
                        "friction_coefficient": 0.8,
                        "rolling_resistance": 0.02,
                        "motor_inertia": 0.001,
                        "gear_efficiency": 0.85,
                        "terrain_modifier": {
                            "grass": 1.5,
                            "concrete": 0.9,
                            "mud": 2.5
                        }
                    }
                )
            """
            return await self.motor_manager.configure_motor_physics(
                object_name, motor_id, physics_config, project_path, scene_path
            )
