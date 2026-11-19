from fastapi import APIRouter, Depends, status

from app.dependencies import Pagination, get_book_or_404, get_db, pagination_params
from app.exceptions import DuplicateError
from app.schemas.book import BookCreate, BookOut, BookUpdate
from app.store import book_ids, isbn_taken

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookOut], status_code=status.HTTP_200_OK)
def list_books(page: Pagination = Depends(pagination_params), db: dict = Depends(get_db)):
    all_books = list(db.values())
    return all_books[page.skip : page.skip + page.limit]


@router.get("/{book_id}", response_model=BookOut, status_code=status.HTTP_200_OK)
def get_book(book: dict = Depends(get_book_or_404)):
    return book


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, db: dict = Depends(get_db)):
    if isbn_taken(db, data.isbn):
        raise DuplicateError("A book with this ISBN already exists")
    new_id = next(book_ids)
    db[new_id] = {"id": new_id, **data.model_dump()}
    return db[new_id]


@router.put("/{book_id}", response_model=BookOut, status_code=status.HTTP_200_OK)
def replace_book(data: BookCreate, book: dict = Depends(get_book_or_404), db: dict = Depends(get_db)):
    """Full update: you must send every field."""
    if isbn_taken(db, data.isbn, ignore_id=book["id"]):
        raise DuplicateError("A book with this ISBN already exists")
    book.update(data.model_dump())
    return book


@router.patch("/{book_id}", response_model=BookOut, status_code=status.HTTP_200_OK)
def update_book(data: BookUpdate, book: dict = Depends(get_book_or_404), db: dict = Depends(get_db)):
    """Partial update: send only the fields you want to change."""
    changes = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if "isbn" in changes and isbn_taken(db, changes["isbn"], ignore_id=book["id"]):
        raise DuplicateError("A book with this ISBN already exists")
    book.update(changes)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book: dict = Depends(get_book_or_404), db: dict = Depends(get_db)):
    del db[book["id"]]