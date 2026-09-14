from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


@lru_cache(maxsize=1)
def get_engine():
    url = settings.DATABASE_URL or settings.VECTOR_DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL/VECTOR_DATABASE_URL غير مجهزة")
    return create_engine(url, pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def get_db():
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
