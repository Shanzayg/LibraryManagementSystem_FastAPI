from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

# The engine = the connection to Neon. pool_pre_ping re-checks a connection before using it
# (Neon can put an idle database to sleep).
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# A SessionLocal() call gives you one session = one "conversation" with the database.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All models inherit from this. Alembic reads Base.metadata to find your tables."""