import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings


async def logging_middleware(request: Request, call_next):
    """Prints: METHOD /path -> status (duration)."""
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    print(f"{request.method} {request.url.path} -> {response.status_code} ({ms:.1f} ms)", flush=True)
    return response


async def timing_middleware(request: Request, call_next):
    """Adds an X-Process-Time header (seconds) to every response."""
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
    return response


def register_middleware(app: FastAPI) -> None:
    # ORDER MATTERS: the LAST one added is the OUTERMOST, so it runs FIRST on the way in.
    # Here the request goes: CORS -> timing -> logging -> your route (and back out in reverse).
    app.middleware("http")(logging_middleware)
    app.middleware("http")(timing_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )