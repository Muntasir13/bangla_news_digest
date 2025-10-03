from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.conf import DBConfig


# create_engine options are tuned for production (override via env if needed)
def get_engine(cfg: DBConfig) -> Engine:
    connect_args = {}
    if cfg.ssl.mode:
        connect_args["ssl_mode"] = cfg.ssl.mode
    if cfg.ssl.ca_path:
        connect_args["ca"] = cfg.ssl.ca_path

    return create_engine(
        url=cfg.url,
        pool_size=cfg.pool.size,
        max_overflow=cfg.pool.max_overflow,
        pool_recycle=cfg.pool.recycle_time,
        pool_pre_ping=cfg.pool.pre_ping,
        connect_args={"ssl": connect_args} if connect_args else {},
    )


@contextmanager
def get_session(cfg: DBConfig) -> Generator[Session]:
    """Yield a SQLAlchemy Session and commit or rollback on exit."""

    # Create a Session factory bound to the engine
    engine = get_engine(cfg=cfg)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
