"""One-time connection test. Run from the project root:  uv run python check_db.py"""
from sqlalchemy import create_engine, text

from app.config import get_settings

url = get_settings().DATABASE_URL
if not url:
    raise SystemExit("DATABASE_URL is empty. Paste your Neon connection string into .env first.")
if not url.startswith("postgresql+psycopg://"):
    raise SystemExit("DATABASE_URL must start with postgresql+psycopg://  (change the beginning).")

engine = create_engine(url)
with engine.connect() as conn:
    print("SELECT 1 ->", conn.execute(text("SELECT 1")).scalar())
    print("Server   ->", conn.execute(text("SELECT version()")).scalar())
print("Connection works!")