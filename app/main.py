from fastapi import FastAPI, status

from app.config import get_settings
from app.exceptions import register_exception_handlers
from app.middleware import register_middleware
from app.routers import auth, books, loans, users

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version="0.1.0", debug=settings.DEBUG)
register_exception_handlers(app)
register_middleware(app)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(books.router, prefix=API_PREFIX)
app.include_router(loans.router, prefix=API_PREFIX)


@app.get("/health", response_model=dict[str, str], status_code=status.HTTP_200_OK, tags=["Health"])
def health():
    return {"status": "ok"}