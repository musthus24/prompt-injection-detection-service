from pydantic import BaseModel, Field
from typing import List, Optional, Literal

MIN_PROMPT_LEN = 1
MAX_PROMPT_LEN = 8000

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length = MIN_PROMPT_LEN, max_length = MAX_PROMPT_LEN)

class RagConfig(BaseModel):
    enabled: bool = False
    query: Optional[str] = None
    top_k: int = Field(default = 5, ge = 1, le = 20)

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1, max_length=50)
    rag: RagConfig = Field(default_factory = RagConfig)
    review_fallback: Literal["none", "respond_without_context"] = "none"

class ChatResponse(BaseModel):
    request_id: Optional[str] = None
    decision: Literal["ALLOW", "REQUIRE_HUMAN_REVIEW", "BLOCK"]
    action_taken: Literal["PROCEEDED_NORMAL", "PROCEEDED_NO_CONTEXT", "RETURNED_REVIEW", "BLOCKED"]
    risk_score: float
    reasons: List[str] = Field(default_factory = list)
    llm_output: Optional[str] = None
    model_version: str


class ScanRequest(BaseModel):
    prompt: str = Field(..., min_length = MIN_PROMPT_LEN, max_length = MAX_PROMPT_LEN)

class ScanResponse(BaseModel):
    decision: str
    risk_score: float
    model_version: str
