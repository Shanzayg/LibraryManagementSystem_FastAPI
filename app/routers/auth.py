from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.dependencies import get_db
from app.exceptions import DuplicateError, UnauthorizedError
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_email(db, data.email):
        raise DuplicateError("Email already registered")
    # Only the hash is stored. The role is NOT taken from the request: new users are "member".
    return user_crud.create_user(db, data, hash_password(data.password))


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm calls the email field "username". That's the standard name.
    user = user_crud.get_user_by_email(db, form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        # Same message for "no such email" and "wrong password" so nobody can probe which emails exist.
        raise UnauthorizedError("Incorrect email or password")
    return Token(access_token=create_access_token(user.id))