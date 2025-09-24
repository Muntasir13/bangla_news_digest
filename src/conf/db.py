from dataclasses import dataclass


@dataclass
class DBPoolConfig:
    size: int
    max_overflow: int
    recycle_time: int


@dataclass
class DBSSLConfig:
    mode: str
    ca_path: str


@dataclass
class DBConfig:
    driver: str
    host: str
    port: int
    user: str
    password: str
    database_name: str
    pool: DBPoolConfig
    ssl: DBSSLConfig
