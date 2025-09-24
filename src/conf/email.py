from dataclasses import dataclass


@dataclass
class EmailConfig:
    host: str
    port: int
    username: str
    password: str
    from_addr: str
    to_addr: list[str]
    cc_addr: list[str]
