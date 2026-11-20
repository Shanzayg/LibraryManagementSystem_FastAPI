from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud import book as book_crud
from app.dependencies import Pagination, get_book_or_404, get_db, pagination_params, require_librarian
from app.exceptions import DuplicateError
from app.models import Book
from app.schemas.book import BookCreate, BookOut, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookOut], status_code=status.HTTP_200_OK)
def list_books(
    title: str | None = None,
    author: str | None = None,
    available: bool | None = None,
    page: Pagination = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    return book_crud.list_books(db, page.skip, page.limit, title, author, available)


@router.get("/{book_id}", response_model=BookOut, status_code=status.HTTP_200_OK)
def get_book(book: Book = Depends(get_book_or_404)):
    return book


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_librarian)])
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    if book_crud.get_book_by_isbn(db, data.isbn):
        raise DuplicateError("A book with this ISBN already exists")
    return book_crud.create_book(db, data)


def _check_isbn_free(db: Session, isbn: str, book: Book) -> None:
    existing = book_crud.get_book_by_isbn(db, isbn)
    if existing and existing.id != book.id:
        raise DuplicateError("A book with this ISBN already exists")


@router.put("/{book_id}", response_model=BookOut, status_code=status.HTTP_200_OK, dependencies=[Depends(require_librarian)])
def replace_book(data: BookCreate, book: Book = Depends(get_book_or_404), db: Session = Depends(get_db)):
    """Full update: you must send every field."""
    _check_isbn_free(db, data.isbn, book)
    return book_crud.update_book(db, book, data.model_dump())


@router.patch("/{book_id}", response_model=BookOut, status_code=status.HTTP_200_OK, dependencies=[Depends(require_librarian)])
def update_book(data: BookUpdate, book: Book = Depends(get_book_or_404), db: Session = Depends(get_db)):
    """Partial update: send only the fields you want to change."""
    changes = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if "isbn" in changes:
        _check_isbn_free(db, changes["isbn"], book)
    return book_crud.update_book(db, book, changes)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_librarian)])
def delete_book(book: Book = Depends(get_book_or_404), db: Session = Depends(get_db)):
    book_crud.delete_book(db, book)