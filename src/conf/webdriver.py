from dataclasses import dataclass


@dataclass
class WebDriverConfig:
    driver_name: str
    options: dict[str, str | bool]
