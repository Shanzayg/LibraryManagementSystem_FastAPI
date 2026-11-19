from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for our own errors. Each child sets its HTTP status code."""
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str):
        self.message = message


class NotFoundError(AppError):
    """Book, user or loan does not exist."""
    status_code = status.HTTP_404_NOT_FOUND


class DuplicateError(AppError):
    """Same ISBN or email already exists."""
    status_code = status.HTTP_409_CONFLICT


class BusinessRuleError(AppError):
    """No copies left, loan already returned, borrow limit reached."""
    status_code = status.HTTP_400_BAD_REQUEST


class ForbiddenError(AppError):
    """A normal user tried a librarian-only action."""
    status_code = status.HTTP_403_FORBIDDEN


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        # Same shape as FastAPI's own HTTPException: {"detail": "..."}
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})