from fastapi import APIRouter
from app.services.detector import scan_prompt
from .schemas import ScanRequest, ScanResponse

router = APIRouter(prefix="/v1", tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest):
    prompt = req.prompt
    decision, risk_score, model_version = scan_prompt(prompt)
    risk_score = float(risk_score)
    return ScanResponse(decision = decision, risk_score = risk_score, model_version = model_version)
