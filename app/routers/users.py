from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

# Every route in this router now requires a "logged-in user" (placeholder for now).
router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)])


# TEMPORARY placeholder so Users shows up in Swagger. Replace with real routes later.
@router.get("/ping")
def ping(current_user: dict = Depends(get_current_user)):
    return {"router": "users", "current_user": current_user["email"]}