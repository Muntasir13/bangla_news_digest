from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


# create_engine options are tuned for production (override via env if needed)
def get_engine(
    database_url: str,
    pool_size: int,
    max_overflow: int,
    pool_recycle: int,
    ssl_mode: str | None = None,
    ssl_ca_path: str | None = None,
    ssl_cert: str | None = None,
    ssl_key: str | None = None,
) -> Engine:
    connect_args = {}
    if ssl_mode:
        connect_args["ssl_mode"] = ssl_mode
    if ssl_ca_path:
        connect_args["ca"] = ssl_ca_path
    if ssl_cert:
        connect_args["cert"] = ssl_cert
    if ssl_key:
        connect_args["key"] = ssl_key

    return create_engine(
        url=database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        pool_pre_ping=True,
        future=True,
        connect_args={"ssl": connect_args} if connect_args else {},
    )


@contextmanager
def get_session(
    database_url: str,
    pool_size: int,
    max_overflow: int,
    pool_recycle: int,
    ssl_mode: str | None = None,
    ssl_ca_path: str | None = None,
    ssl_cert: str | None = None,
    ssl_key: str | None = None,
) -> Generator[Session]:
    """Yield a SQLAlchemy Session and commit or rollback on exit."""

    # Create a Session factory bound to the engine
    engine = get_engine(
        database_url,
        pool_size,
        max_overflow,
        pool_recycle,
        ssl_mode,
        ssl_ca_path,
        ssl_cert,
        ssl_key,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
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
