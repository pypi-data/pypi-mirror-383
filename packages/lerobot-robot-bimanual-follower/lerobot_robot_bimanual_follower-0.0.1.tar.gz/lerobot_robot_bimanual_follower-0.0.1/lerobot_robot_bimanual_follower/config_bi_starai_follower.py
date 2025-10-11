from dataclasses import dataclass, field

from lerobot.cameras import CameraConfig

from lerobot.robots.config import RobotConfig

@RobotConfig.register_subclass("lerobot_robot_bimanual_follower")
@dataclass
class BiStaraiFollowerConfig(RobotConfig):
    left_arm_port: str
    right_arm_port: str

    arm_name: str = ""

    # Optional
    left_arm_disable_torque_on_disconnect: bool = True
    left_arm_max_relative_target: int | None = None
    left_arm_use_degrees: bool = False
    right_arm_disable_torque_on_disconnect: bool = True
    right_arm_max_relative_target: int | None = None
    right_arm_use_degrees: bool = False

    # cameras (shared between both arms)
    cameras: dict[str, CameraConfig] = field(default_factory=dict)
