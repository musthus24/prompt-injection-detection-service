from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException


def http_exception_handler(_: Request, exc: HTTPException):
    # Use this for errors you intentionally raise.
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "detail": exc.detail,
        },
    )


def validation_exception_handler(_: Request, exc: RequestValidationError):
    # Use this for request schema violations (Pydantic).
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
        },
    )


def unhandled_exception_handler(_: Request, __: Exception):
    # Never leak stack traces to clients.
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error"},
    )
