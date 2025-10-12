"""Main application for the token validator service."""

from contextlib import asynccontextmanager
from typing import Annotated

from ab_core.dependency import Depends, inject
from ab_core.logging.config import LoggingConfig
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, JWTError

from ab_service.token_validator.routes.validate import router as validate_router


@inject
@asynccontextmanager
async def lifespan(
    _app: FastAPI,
    logging_config: Annotated[LoggingConfig, Depends(LoggingConfig, persist=True)],
):
    """Lifespan context manager to handle startup and shutdown events."""
    logging_config.apply()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(validate_router)


@app.exception_handler(ExpiredSignatureError)
async def expired_signature_handler(_request: Request, _exc: ExpiredSignatureError):
    """Handle expired token errors."""
    return JSONResponse(
        status_code=401,
        content={"detail": "Token expired"},
    )


@app.exception_handler(JWTError)
async def jwt_error_handler(_request: Request, exc: JWTError):
    """Handle generic JWT errors."""
    return JSONResponse(
        status_code=401,
        content={"detail": f"Token validation failed: {exc}"},
    )
