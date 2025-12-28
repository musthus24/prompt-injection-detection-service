from app.services.detector import scan_prompt
import logging
from app.core.metrics import SCAN_REQUESTS_TOTAL
from app.security.jwt import verify_token
from fastapi import APIRouter, Request, Depends, HTTPException
from .schemas import ScanRequest, ScanResponse, ChatRequest, ChatResponse



router = APIRouter(prefix="/v1", tags=["gateway"])
logger = logging.getLogger("gateway")


def map_scan_to_gateway_policy(scan_decision: str, review_fallback: str):
    """
    Converts scan output -> gateway decision + action_taken.
    scan_decision: allow | review | high_risk
    decision: ALLOW | REQUIRE_HUMAN_REVIEW | BLOCK
    action_taken: PROCEEDED_NORMAL | PROCEEDED_NO_CONTEXT | RETURNED_REVIEW | BLOCKED
    """
    reasons = ["threshold_mapping"]

    if scan_decision == "high_risk":
        return "BLOCK", "BLOCKED", reasons

    if scan_decision == "review":
        if review_fallback == "respond_without_context":
            return "REQUIRE_HUMAN_REVIEW", "PROCEEDED_NO_CONTEXT", reasons
        return "REQUIRE_HUMAN_REVIEW", "RETURNED_REVIEW", reasons

    if scan_decision == "allow":
        return "ALLOW", "PROCEEDED_NORMAL", reasons

    return "REQUIRE_HUMAN_REVIEW", "RETURNED_REVIEW", ["unknown_scan_decision"]

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
            "caller_id": subject,
            "decision": decision,
            "risk_score": risk_score,
            "model_version": model_version,
            "reason": reason,
            "latency_ms": getattr(request.state, "latency_ms", None),
        },
    )

    return ScanResponse(decision=decision, risk_score=risk_score, model_version=model_version)



@router.post("/chat", response_model = ChatResponse)
def chat(req: ChatRequest, request: Request, subject: str = Depends(verify_token)):

    combined = "\n".join([m.content for m in req.messages])

    scan_decision, risk_score, model_version = scan_prompt(combined)
    risk_score = float(risk_score)

    decision, action_taken, reasons = map_scan_to_gateway_policy(scan_decision, req.review_fallback)

    if decision == "BLOCK":
        logger.info(
            "chat_blocked",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "caller_id": subject,
                "decision": decision,
                "action_taken": action_taken,
                "risk_score": risk_score,
                "model_version": model_version,
                "reasons": reasons,
                "latency_ms": getattr(request.state, "latency_ms", None),
            },
        )
        raise HTTPException(
            status_code=403,
            detail={
                "request_id": getattr(request.state, "request_id", None),
                "error": {"code": "POLICY_BLOCK", "message": "Request blocked by security policy"},
            },
        )

    if decision == "REQUIRE_HUMAN_REVIEW" and action_taken == "RETURNED_REVIEW":
        logger.info(
            "chat_review_required",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "caller_id": subject,
                "decision": decision,
                "action_taken": action_taken,
                "risk_score": risk_score,
                "model_version": model_version,
                "reasons": reasons,
                "latency_ms": getattr(request.state, "latency_ms", None),
            },
        )
        return ChatResponse(
            request_id=getattr(request.state, "request_id", None),
            decision=decision,
            action_taken=action_taken,
            risk_score=risk_score,
            reasons=reasons,
            llm_output=None,
            model_version=model_version,
        )


    llm_output = "stubbed_response"

    logger.info(
        "chat_completed",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "caller_id": subject,
            "decision": decision,
            "action_taken": action_taken,
            "risk_score": risk_score,
            "model_version": model_version,
            "reasons": reasons,
            "latency_ms": getattr(request.state, "latency_ms", None),
        },
    )

    return ChatResponse(
        request_id=getattr(request.state, "request_id", None),
        decision=decision,
        action_taken=action_taken,
        risk_score=risk_score,
        reasons=reasons,
        llm_output=llm_output,
        model_version=model_version,
    )
