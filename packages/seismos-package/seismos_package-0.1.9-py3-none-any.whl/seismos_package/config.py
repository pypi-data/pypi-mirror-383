import os
from dataclasses import dataclass, field


@dataclass
class SeismosConfig:
    APP_NAME: str = field(init=False)
    ENVIRONMENT: str = field(init=False)
    LOG_LEVEL: str = field(init=False)

    def __post_init__(self):
        self.APP_NAME = os.getenv("APP_NAME", "SeismosApp")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


config = SeismosConfig()
