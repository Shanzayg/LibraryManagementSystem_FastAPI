from dataclasses import dataclass

from fastapi import Depends, Query

from app import store
from app.exceptions import NotFoundError


# 1) Pagination: reuse on every list route ----------------------------------
@dataclass
class Pagination:
    skip: int
    limit: int


def pagination_params(
    skip: int = Query(0, ge=0, description="How many items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
) -> Pagination:
    return Pagination(skip=skip, limit=limit)


# 2) Database: for now it hands out the in-memory dict ----------------------
def get_db() -> dict[int, dict]:
    # Topic 13 will change this to yield a real SQLAlchemy session.
    return store.books


# 3) Find a book or raise 404 (so routes don't repeat this check) -----------
def get_book_or_404(book_id: int, db: dict = Depends(get_db)) -> dict:
    book = db.get(book_id)
    if book is None:
        raise NotFoundError("Book not found")
    return book


# 4) Placeholder "logged-in user". Real version (JWT) comes in topic 17. ----
def get_current_user() -> dict:
    return {"id": 1, "email": "demo@example.com", "role": "librarian"}