from dataclasses import dataclass

from .logger import LoggerConfig
from .runtime import RuntimeConfig
from .webdriver import WebDriverConfig


@dataclass
class ProjectConfig:
    runtime: RuntimeConfig
    logging: LoggerConfig
    webdriver: WebDriverConfig
    max_retries: int
