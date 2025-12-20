from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.routes import router as scan_router

app = FastAPI(title="Prompt Injection Detection Service", version="0.1.0")
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(scan_router)


@app.get("/health")
def health():
    return {"status": "ok"}
