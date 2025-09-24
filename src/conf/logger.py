from dataclasses import dataclass


@dataclass
class LoggerFilePathConfig:
    folder_location: str
    name: str
    when: str
    backup_count: int


@dataclass
class LoggerQueueManagerConfig:
    maxsize: int


@dataclass
class LoggerConfig:
    level: str
    handlers: list[str]
    fmt: str
    file: LoggerFilePathConfig
    queue: LoggerQueueManagerConfig
