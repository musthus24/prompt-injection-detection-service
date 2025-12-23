from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.routes import router as scan_router
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from fastapi import Response
from app.security.jwt import get_jwt_secret

configure_logging()

app = FastAPI(title="Prompt Injection Detection Service", version="0.1.0")
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(RequestContextMiddleware)

app.include_router(scan_router)

@app.on_event("startup")
def validate_security_config():
    get_jwt_secret()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type = CONTENT_TYPE_LATEST)
