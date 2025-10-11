from dataclasses import dataclass

from lerobot.teleoperators.config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("lerobot_teleoperator_bimanual_leader")
@dataclass
class BiStaraiLeaderConfig(TeleoperatorConfig):
    left_arm_port: str
    right_arm_port: str
