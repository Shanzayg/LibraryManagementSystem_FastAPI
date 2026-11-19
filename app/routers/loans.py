from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.dependencies import get_current_user

# Every route in this router now requires a "logged-in user" (placeholder for now).
router = APIRouter(prefix="/loans", tags=["Loans"], dependencies=[Depends(get_current_user)])


# TEMPORARY placeholder so Loans shows up in Swagger. Replace with real routes later.
@router.get("/ping")
def ping(current_user: dict = Depends(get_current_user)):
    return {"router": "loans", "current_user": current_user["email"]}


# TEMPORARY: shows the settings values. The real borrow-limit check comes on Day 5.
@router.get("/limit")
def loan_limit(settings: Settings = Depends(get_settings)):
    return {"max_loans_per_user": settings.MAX_LOANS_PER_USER, "loan_days": settings.LOAN_DAYS}