from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.crud import loan as loan_crud
from app.dependencies import get_current_user, get_db, require_librarian
from app.exceptions import ForbiddenError, NotFoundError
from app.models import User
from app.schemas.loan import LoanCreate, LoanOut

# Every route in this router requires a logged-in user.
router = APIRouter(prefix="/loans", tags=["Loans"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
def borrow(
    data: LoanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Borrow a book. The user comes from the login token."""
    return loan_crud.borrow_book(db, current_user, data.book_id, settings)


# Fixed paths (/me, /overdue) are declared before anything with {loan_id}.
@router.get("/me", response_model=list[LoanOut])
def my_loans(active: bool | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Your loans. Use ?active=true to see only the books you still have."""
    return loan_crud.list_loans_for_user(db, current_user.id, active)


@router.get("/overdue", response_model=list[LoanOut], dependencies=[Depends(require_librarian)])
def overdue_loans(db: Session = Depends(get_db)):
    """Librarians only: loans past their due date and not returned."""
    return loan_crud.list_overdue_loans(db)


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_book(loan_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = loan_crud.get_loan(db, loan_id)
    if loan is None:
        raise NotFoundError("Loan not found")
    if loan.user_id != current_user.id and current_user.role != "librarian":
        raise ForbiddenError("You can only return your own loans")
    return loan_crud.return_loan(db, loan)