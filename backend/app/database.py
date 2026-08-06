from collections.abc import Generator
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


def normalize_database_url(url: str) -> str:
    """Neon / Heroku sometimes use postgres:// — SQLAlchemy needs postgresql://."""
    url = (url or "").strip().strip('"').strip("'")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    # Prefer psycopg2 driver explicitly
    if url.startswith("postgresql://") and "+psycopg2" not in url and "+asyncpg" not in url:
        url = "postgresql+psycopg2://" + url[len("postgresql://") :]

    # Ensure SSL for Neon if missing
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    host = (parsed.hostname or "").lower()
    if "neon.tech" in host and "sslmode" not in query:
        query["sslmode"] = "require"
        parsed = parsed._replace(query=urlencode(query))
        url = urlunparse(parsed)
    return url


settings = get_settings()
DATABASE_URL = normalize_database_url(settings.database_url)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 15},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> dict:
    """Quick connectivity check used by /health and startup."""
    with engine.connect() as conn:
        row = conn.execute(text("SELECT version()")).fetchone()
        return {"ok": True, "version": row[0] if row else None}
