from uuid import uuid4

from sqlalchemy import TIMESTAMP, Column, Index, MetaData, String, Text, func
from sqlalchemy.orm import DeclarativeBase

# Use naming_convention so Alembic generates deterministic names across DBs
# ix = Index, uq = Unique, fk = Foreign key, pk = Primary key, ck =
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(String(36), primary_key=True, unique=True, default=str(uuid4()))
    url = Column(String(512), nullable=False, unique=True)  # long enough for URLs
    title = Column(String(512), nullable=True)
    body = Column(Text, nullable=True)
    fingerprint = Column(String(128), nullable=False, unique=True)  # e.g. sha256 hex
    published_at = Column(TIMESTAMP(timezone=True), nullable=True)
    source = Column(String(128), nullable=True)  # site identifier
    source_url = Column(String(512), nullable=True)  # site url
    scraped_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    language = Column(String(10), nullable=True)

    __table_args__ = (
        # Useful indexes
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_source_published", "source", "published_at"),
        # MySQL-specific table options
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id} url={self.url!r})>"
