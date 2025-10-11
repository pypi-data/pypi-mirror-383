from dataclasses import dataclass

from lerobot.teleoperators.config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("lerobot_teleoperator_violin")
@dataclass
class StaraiViolinConfig(TeleoperatorConfig):
    # Port to connect to the arm
    port: str

    use_degrees: bool = False
