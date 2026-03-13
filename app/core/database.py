from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import get_settings

DATABASE_URL = get_settings()["database_url"]

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


COMMENT_TABLE_COLUMNS = {
    "youtube_comment_id": "ALTER TABLE comments ADD COLUMN youtube_comment_id VARCHAR",
    "discovery_query": "ALTER TABLE comments ADD COLUMN discovery_query VARCHAR",
    "author": "ALTER TABLE comments ADD COLUMN author VARCHAR",
    "like_count": "ALTER TABLE comments ADD COLUMN like_count INTEGER DEFAULT 0",
    "reply_count": "ALTER TABLE comments ADD COLUMN reply_count INTEGER DEFAULT 0",
    "published_at": "ALTER TABLE comments ADD COLUMN published_at TIMESTAMP WITH TIME ZONE",
    "ml_score": "ALTER TABLE comments ADD COLUMN ml_score DOUBLE PRECISION DEFAULT 0",
    "detection_reasons": "ALTER TABLE comments ADD COLUMN detection_reasons TEXT",
    "moderation_status": "ALTER TABLE comments ADD COLUMN moderation_status VARCHAR DEFAULT 'pending'",
    "was_deleted": "ALTER TABLE comments ADD COLUMN was_deleted BOOLEAN DEFAULT FALSE",
}


def init_database():
    Base.metadata.create_all(bind=engine)
    _ensure_comment_columns()


def _ensure_comment_columns():
    inspector = inspect(engine)
    if "comments" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("comments")}
    pending_statements = [
        ddl for column_name, ddl in COMMENT_TABLE_COLUMNS.items() if column_name not in existing_columns
    ]

    if not pending_statements:
        return

    with engine.begin() as connection:
        for ddl in pending_statements:
            connection.execute(text(ddl))
