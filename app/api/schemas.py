from pydantic import BaseModel, Field

MAX_PROMPT_LEN = 8000


class ScanRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=MAX_PROMPT_LEN)


class ScanResponse(BaseModel):
    decision: str
    risk_score: float
    model_version: str
