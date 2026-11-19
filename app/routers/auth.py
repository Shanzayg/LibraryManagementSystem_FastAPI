from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


# TEMPORARY placeholder so Auth shows up in Swagger. Replace with real routes later.
@router.get("/ping")
def ping():
    return {"router": "auth"}