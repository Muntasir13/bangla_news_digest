import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional, Sequence, cast

from sqlalchemy import delete as sql_delete
from sqlalchemy import func
from sqlalchemy import insert as sql_insert
from sqlalchemy import select
from sqlalchemy import update as sql_update

# dialect helpers
from sqlalchemy.dialects import postgresql as pg_dialects
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql._typing import _DMLTableArgument

from src.conf import DBConfig

from .models import Base, NewsArticle
from .session import get_session

log = logging.getLogger(__name__)

BATCH_SIZE = 500


# ---------- Schema helper ----------
def ensure_tables(engine: Engine) -> None:
    """Create tables from models (dev helper). Production: use Alembic migrations."""
    Base.metadata.create_all(bind=engine)


# ---------- Create ----------
def create_article(session: Session, payload: dict[str, Any]) -> NewsArticle:
    """
    Create a single NewsArticle row and return the ORM object.
    Raises IntegrityError if unique constraints fail.
    """
    obj = NewsArticle(**payload)
    session.add(obj)
    session.flush()  # assign PK, validate constraints now
    # refresh to load defaults from DB (e.g., scraped_at)
    session.refresh(obj)
    return obj


# ---------- Read ----------
def get_article_by_id(session: Session, article_id: int) -> Optional[NewsArticle]:
    stmt = select(NewsArticle).where(NewsArticle.id == article_id).order_by(NewsArticle.scraped_at)
    return session.execute(stmt).scalars().first()


def get_article_by_url(session: Session, url: str) -> Optional[NewsArticle]:
    stmt = select(NewsArticle).where(NewsArticle.url == url).order_by(NewsArticle.scraped_at)
    return session.execute(stmt).scalars().first()


def get_article_by_date(session: Session, search_datetime: date) -> list[NewsArticle]:
    stmt = (
        select(NewsArticle)
        .filter(
            (NewsArticle.scraped_at >= str(datetime.combine(search_datetime, datetime.min.time())))
            & (NewsArticle.scraped_at <= str(datetime.combine(search_datetime, datetime.max.time())))
        )
        .order_by(NewsArticle.scraped_at)
    )
    return list(session.execute(stmt).scalars().all())


def list_articles(
    session: Session,
    *,
    source: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    order_by_newest: bool = True,
) -> list[NewsArticle]:
    """
    List articles with simple filters and pagination.
    """
    stmt = select(NewsArticle)
    if source is not None:
        stmt = stmt.where(NewsArticle.source == source)
    if order_by_newest:
        stmt = stmt.order_by(NewsArticle.published_at.desc().nullslast())
    else:
        stmt = stmt.order_by(NewsArticle.published_at.asc().nullsfirst())
    stmt = stmt.limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())


def count_articles(session: Session, *, source: Optional[str] = None) -> int:
    stmt = select(func.count(NewsArticle.id))
    if source is not None:
        stmt = stmt.where(NewsArticle.source == source)
    return int(session.execute(stmt).scalar_one())


# ---------- Update ----------
def update_article_by_id(session: Session, article_id: str, updates: dict[str, Any]) -> int:
    """
    Update an article by id. Returns number of rows updated (0 or 1).
    """
    stmt = sql_update(NewsArticle).where(NewsArticle.id == article_id).values(**updates)
    res = session.execute(stmt)
    return res.rowcount or 0


def update_article_by_url(session: Session, url: str, updates: dict[str, Any]) -> int:
    stmt = sql_update(NewsArticle).where(NewsArticle.url == url).values(**updates)
    res = session.execute(stmt)
    return res.rowcount or 0


# ---------- Delete ----------
def delete_article_by_id(session: Session, article_id: int) -> int:
    stmt = sql_delete(NewsArticle).where(NewsArticle.id == article_id)
    res = session.execute(stmt)
    return res.rowcount or 0


def delete_article_by_url(session: Session, url: str) -> int:
    stmt = sql_delete(NewsArticle).where(NewsArticle.url == url)
    res = session.execute(stmt)
    return res.rowcount or 0


def bulk_delete_by_source(session: Session, source: str) -> int:
    """Delete all articles from a source. Returns rows deleted."""
    stmt = sql_delete(NewsArticle).where(NewsArticle.source == source)
    res = session.execute(stmt)
    return res.rowcount or 0


# ---------- Batch insert (assumes caller ensures uniqueness of id/url) ----------
def _insert_chunk_plain(session: Session, table: _DMLTableArgument, rows: Sequence[dict[str, Any]]) -> None:
    """
    Portable executemany insert. Works for all DBs and is fast for moderate batches.
    """
    stmt = sql_insert(table)
    session.execute(stmt, rows)
    return


def insert_articles_batch(
    session: Session,
    items: list[dict[str, Any]],
    batch_size: int = BATCH_SIZE,
    ignore_conflicts: bool = False,
) -> int:
    """
    Insert items in batches. If ignore_conflicts is True and DB supports it (Postgres),
    conflicts will be ignored (ON CONFLICT DO NOTHING). Otherwise IntegrityError is raised on duplicates.
    """
    if not items:
        return 0

    table = cast(_DMLTableArgument, NewsArticle.__table__)
    dialect = session.bind.dialect.name.lower()  # type: ignore
    total = 0

    for i in range(0, len(items), batch_size):
        chunk = items[i : i + batch_size]
        try:
            if ignore_conflicts and dialect.startswith("postgres"):
                stmt = pg_dialects.insert(table).on_conflict_do_nothing(index_elements=["url"])
                session.execute(stmt, chunk)
            else:
                _insert_chunk_plain(session, table, chunk)
            total += len(chunk)
        except IntegrityError:
            # This exception should be rare.
            log.exception("IntegrityError while inserting chunk %d..%d", i, i + len(chunk) - 1)
            raise
    return total


# ---------- Convenience wrappers that manage sessions ----------
def save_scraped_items(database_config: DBConfig, items: list[dict[str, Any]]) -> int:
    """
    Convenience entrypoint: upsert (default) or insert items into DB.
    """
    if not items:
        return 0
    with get_session(database_config) as session:
        return insert_articles_batch(session, items)


def get_articles_by_start_and_end_date(database_config: DBConfig, start_date: date, end_date: date) -> list[dict[str, Any]]:
    news_articles = []
    with get_session(database_config) as session:
        for day in (start_date + timedelta(n) for n in range((end_date - start_date).days)):
            news_articles.extend([article.__dict__ for article in get_article_by_date(session=session, search_datetime=day)])
    return news_articles
