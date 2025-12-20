from fastapi import APIRouter
from .schemas import ScanRequest, ScanResponse

router = APIRouter(prefix="/v1", tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest):
    return ScanResponse(decision="review", risk_score=0.0, model_version="stub-v0")
