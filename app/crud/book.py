from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleError
from app.models import Book
from app.schemas.book import BookCreate


def get_book(db: Session, book_id: int) -> Book | None:
    return db.get(Book, book_id)


def get_book_by_isbn(db: Session, isbn: str) -> Book | None:
    return db.scalar(select(Book).where(Book.isbn == isbn))


def list_books(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    title: str | None = None,
    author: str | None = None,
    available: bool | None = None,
) -> list[Book]:
    stmt = select(Book)
    if title:
        stmt = stmt.where(Book.title.ilike(f"%{title}%"))
    if author:
        stmt = stmt.where(Book.author.ilike(f"%{author}%"))
    if available is True:
        stmt = stmt.where(Book.available_copies > 0)
    stmt = stmt.order_by(Book.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create_book(db: Session, data: BookCreate) -> Book:
    book = Book(
        title=data.title,
        author=data.author,
        isbn=data.isbn,
        published_year=data.published_year,
        total_copies=data.total_copies,
        available_copies=data.total_copies,  # a new book starts with all copies on the shelf
    )
    db.add(book)
    db.commit()
    db.refresh(book)  # loads the generated id
    return book


def update_book(db: Session, book: Book, changes: dict) -> Book:
    if "total_copies" in changes:
        # keep available_copies in step: more total copies = more available copies
        new_available = book.available_copies + (changes["total_copies"] - book.total_copies)
        if new_available < 0:
            raise BusinessRuleError("Total copies cannot be lower than the copies currently on loan")
        book.available_copies = new_available
    for field, value in changes.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: Book) -> None:
    if book.loans:
        raise BusinessRuleError("Cannot delete a book that has loan records")
    db.delete(book)
    db.commit()