from dataclasses import dataclass

from .db import DBConfig
from .email import EmailConfig


@dataclass
class RuntimeConfig:
    db: DBConfig
    email: EmailConfig
    db_send: bool
    email_send: bool
