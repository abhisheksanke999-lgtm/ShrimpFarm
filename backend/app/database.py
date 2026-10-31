import os
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

_on_render = os.getenv("RENDER") == "true" or bool(os.getenv("RENDER_SERVICE_ID"))
_pool_size = 2 if _on_render else 5
_max_overflow = 3 if _on_render else 10

if _on_render:
    print("Database engine: Render mode (small connection pool)")
else:
    print("Database engine: local/dev mode")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=_pool_size,
    max_overflow=_max_overflow,
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
