import logging
import time
import importlib
from functools import cached_property
from typing import Any

from lerobot.cameras.utils import make_cameras_from_configs

from lerobot.robots.robot import Robot
from .config_bi_starai_follower import BiStaraiFollowerConfig

logger = logging.getLogger(__name__)


class BiStaraiFollower(Robot):
    config_class = BiStaraiFollowerConfig
    name = "lerobot_robot_bimanual_follower"

    def __init__(self, config: BiStaraiFollowerConfig):
        super().__init__(config)
        self.config = config

        ArmCls, ArmCfgCls = self._resolve_arm_classes()

        left_arm_config = ArmCfgCls(
            id=f"{config.id}_left" if config.id else None,
            calibration_dir=config.calibration_dir,
            port=config.left_arm_port,
            disable_torque_on_disconnect=config.left_arm_disable_torque_on_disconnect,
            max_relative_target=config.left_arm_max_relative_target,
            use_degrees=config.left_arm_use_degrees,
            cameras={},
        )

        right_arm_config = ArmCfgCls(
            id=f"{config.id}_right" if config.id else None,
            calibration_dir=config.calibration_dir,
            port=config.right_arm_port,
            disable_torque_on_disconnect=config.right_arm_disable_torque_on_disconnect,
            max_relative_target=config.right_arm_max_relative_target,
            use_degrees=config.right_arm_use_degrees,
            cameras={},
        )

        self.left_arm = ArmCls(left_arm_config)
        self.right_arm = ArmCls(right_arm_config)
        self.cameras = make_cameras_from_configs(config.cameras)

    def _resolve_arm_classes(self):
        name = (self.config.arm_name or "").lower()
        if name not in ("starai_viola", "starai_cello"):
            raise ValueError(
                f"Invalid arm_name '{self.config.arm_name}'. Only 'starai_viola' or 'starai_cello' are supported."
            )
        arm_short = "viola" if name == "starai_viola" else "cello"
        try:
            arm_module = importlib.import_module(f"lerobot_robot_{arm_short}")
            cfg_module = importlib.import_module(f"lerobot_robot_{arm_short}.config_starai_{arm_short}")
            class_name = f"Starai{arm_short.capitalize()}"
            ArmCls = getattr(arm_module, class_name)
            ArmCfgCls = getattr(cfg_module, f"{class_name}Config")
        except Exception as e:
            raise ImportError(
                f"Failed to import classes for '{name}': {e}. Ensure the corresponding package is installed."
            ) from e
        return ArmCls, ArmCfgCls

    @property
    def _motors_ft(self) -> dict[str, type]:
        return {f"left_{motor}.pos": float for motor in self.left_arm.bus.motors} | {
            f"right_{motor}.pos": float for motor in self.right_arm.bus.motors
        }

    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        return {
            cam: (self.config.cameras[cam].height, self.config.cameras[cam].width, 3) for cam in self.cameras
        }

    @cached_property
    def observation_features(self) -> dict[str, type | tuple]:
        return {**self._motors_ft, **self._cameras_ft}

    @cached_property
    def action_features(self) -> dict[str, type]:
        return self._motors_ft

    @property
    def is_connected(self) -> bool:
        return (
            self.left_arm.bus.is_connected
            and self.right_arm.bus.is_connected
            and all(cam.is_connected for cam in self.cameras.values())
        )

    def connect(self, calibrate: bool = True) -> None:
        self.left_arm.connect(calibrate)
        self.right_arm.connect(calibrate)

        for cam in self.cameras.values():
            cam.connect()

    @property
    def is_calibrated(self) -> bool:
        return self.left_arm.is_calibrated and self.right_arm.is_calibrated

    def calibrate(self) -> None:
        self.left_arm.calibrate()
        self.right_arm.calibrate()

    def configure(self) -> None:
        self.left_arm.configure()
        self.right_arm.configure()

    def setup_motors(self) -> None:
        return
        # self.left_arm.setup_motors()
        # self.right_arm.setup_motors()

    def get_observation(self) -> dict[str, Any]:
        obs_dict = {}

        # Add "left_" prefix
        left_obs = self.left_arm.get_observation()
        obs_dict.update({f"left_{key}": value for key, value in left_obs.items()})

        # Add "right_" prefix
        right_obs = self.right_arm.get_observation()
        obs_dict.update({f"right_{key}": value for key, value in right_obs.items()})

        for cam_key, cam in self.cameras.items():
            start = time.perf_counter()
            obs_dict[cam_key] = cam.async_read()
            dt_ms = (time.perf_counter() - start) * 1e3
            logger.debug(f"{self} read {cam_key}: {dt_ms:.1f}ms")

        return obs_dict

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        # Remove "left_" prefix
        left_action = {
            key.removeprefix("left_"): value for key, value in action.items() if key.startswith("left_")
        }
        # Remove "right_" prefix
        right_action = {
            key.removeprefix("right_"): value for key, value in action.items() if key.startswith("right_")
        }

        send_action_left = self.left_arm.send_action(left_action)
        send_action_right = self.right_arm.send_action(right_action)

        # Add prefixes back
        prefixed_send_action_left = {f"left_{key}": value for key, value in send_action_left.items()}
        prefixed_send_action_right = {f"right_{key}": value for key, value in send_action_right.items()}

        return {**prefixed_send_action_left, **prefixed_send_action_right}

    def disconnect(self):
        self.left_arm.disconnect()
        self.right_arm.disconnect()

        for cam in self.cameras.values():
            cam.disconnect()
