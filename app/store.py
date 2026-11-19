"""TEMPORARY in-memory "database". Deleted in topics 13-15 when PostgreSQL arrives.

It lives in its own file so routers can import it without importing main.py
(importing main.py from a router would create a circular import).
"""
from itertools import count

books: dict[int, dict] = {}
book_ids = count(1)  # next(book_ids) gives 1, 2, 3, ...


def isbn_taken(db: dict, isbn: str, ignore_id: int | None = None) -> bool:
    return any(b["isbn"] == isbn and b["id"] != ignore_id for b in db.values())