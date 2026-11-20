from dataclasses import dataclass

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.crud import book as book_crud
from app.crud import user as user_crud
from app.database import SessionLocal
from app.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.models import Book, User
from app.security import decode_access_token


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


# 2) Database session: one session per request, always closed afterwards -----
def get_db():
    db: Session = SessionLocal()
    try:
        yield db          # the route runs here, using this session
    finally:
        db.close()        # runs even if the route raised an error


# 3) Find a book or raise 404 (so routes don't repeat this check) -----------
def get_book_or_404(book_id: int, db: Session = Depends(get_db)) -> Book:
    book = book_crud.get_book(db, book_id)
    if book is None:
        raise NotFoundError("Book not found")
    return book


# 4) Authentication: who is making this request? ------------------------------
# tokenUrl tells Swagger where to log in (gives you the green "Authorize" button).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise UnauthorizedError("Invalid or expired token")
    user = user_crud.get_user(db, user_id)
    if user is None:
        raise UnauthorizedError("User no longer exists")
    return user


# 5) Authorization: is this user allowed to do this? --------------------------
def require_librarian(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "librarian":
        raise ForbiddenError("Librarian access required")
    return current_user