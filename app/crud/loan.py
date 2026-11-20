from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.exceptions import BusinessRuleError, DuplicateError, NotFoundError
from app.models import Book, Loan, User


def get_loan(db: Session, loan_id: int) -> Loan | None:
    return db.get(Loan, loan_id)


def list_loans_for_user(db: Session, user_id: int, active: bool | None = None) -> list[Loan]:
    stmt = select(Loan).where(Loan.user_id == user_id)
    if active is True:
        stmt = stmt.where(Loan.returned_at.is_(None))
    return list(db.scalars(stmt.order_by(Loan.id)))


def list_overdue_loans(db: Session) -> list[Loan]:
    stmt = select(Loan).where(Loan.returned_at.is_(None), Loan.due_date < date.today())
    return list(db.scalars(stmt.order_by(Loan.due_date)))


def count_active_loans(db: Session, user_id: int) -> int:
    stmt = select(func.count()).select_from(Loan).where(Loan.user_id == user_id, Loan.returned_at.is_(None))
    return db.scalar(stmt) or 0


def has_active_loan_for_book(db: Session, user_id: int, book_id: int) -> bool:
    stmt = select(Loan.id).where(Loan.user_id == user_id, Loan.book_id == book_id, Loan.returned_at.is_(None))
    return db.scalar(stmt) is not None


def borrow_book(db: Session, user: User, book_id: int, settings: Settings) -> Loan:
    # with_for_update() locks this book row until we commit, so two people
    # cannot both take the last copy at the same moment.
    book = db.scalar(select(Book).where(Book.id == book_id).with_for_update())
    if book is None:
        raise NotFoundError("Book not found")
    if book.available_copies <= 0:
        raise BusinessRuleError("Book not available")
    if count_active_loans(db, user.id) >= settings.MAX_LOANS_PER_USER:
        raise BusinessRuleError("Borrow limit reached")
    if has_active_loan_for_book(db, user.id, book.id):
        raise DuplicateError("You already have this book on loan")

    book.available_copies -= 1
    loan = Loan(user_id=user.id, book_id=book.id, due_date=date.today() + timedelta(days=settings.LOAN_DAYS))
    db.add(loan)
    db.commit()  # ONE commit: the new loan and the copy count change together, or not at all
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan: Loan) -> Loan:
    if loan.returned_at is not None:
        raise BusinessRuleError("Loan already returned")
    book = db.scalar(select(Book).where(Book.id == loan.book_id).with_for_update())
    book.available_copies += 1
    loan.returned_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(loan)
    return loan