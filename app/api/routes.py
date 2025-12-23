from app.services.detector import scan_prompt
from .schemas import ScanRequest, ScanResponse
import logging
from app.core.metrics import SCAN_REQUESTS_TOTAL
from app.security.jwt import verify_token
from fastapi import APIRouter, Request, Depends



router = APIRouter(prefix="/v1", tags=["scan"])

logger = logging.getLogger("scan")


@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest, request: Request, subject: str = Depends(verify_token),):
    prompt = req.prompt
    decision, risk_score, model_version = scan_prompt(prompt)
    risk_score = float(risk_score)

    SCAN_REQUESTS_TOTAL.labels(decision=decision).inc()

    reason = "threshold_mapping"

    logger.info(
        "scan_completed",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "decision": decision,
            "risk_score": risk_score,
            "model_version": model_version,
            "reason": reason,
            "latency_ms": getattr(request.state, "latency_ms", None),
        },
    )

    return ScanResponse(decision=decision, risk_score=risk_score, model_version=model_version)
