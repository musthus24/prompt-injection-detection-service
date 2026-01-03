from pydantic import BaseModel, Field
from typing import List, Literal, Any, Optional, Dict

MIN_PROMPT_LEN = 1
MAX_PROMPT_LEN = 8000

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length = MIN_PROMPT_LEN, max_length = MAX_PROMPT_LEN)

class RagConfig(BaseModel):
    enabled: bool = False
    query: Optional[str] = None
    top_k: int = Field(default = 5, ge = 1, le = 20)


class ToolRequest(BaseModel):
    """
    Client asks the gateway to invoke a named tool with arguments.
    We keep args as a dict here, but we will validate it strictly per-tool in the registry.
    """
    name: str = Field(..., min_length=1, max_length=64)
    args: Dict[str, Any] = Field(default_factory=dict)

class ToolResult(BaseModel):
    """
    What happened with the tool attempt.
    executed=False means we refused or skipped execution.
    """
    name: str
    executed: bool
    output: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None 


class ChatRequest(BaseModel):
    """
    when the client sends a chat request, meaning a message, this is the format of that
    """
    messages: List[ChatMessage] = Field(..., min_length=1, max_length=50)
    rag: RagConfig = Field(default_factory = RagConfig)
    review_fallback: Literal["none", "respond_without_context"] = "none"
    tool_request: Optional[ToolRequest] = None

class ChatResponse(BaseModel):
    request_id: Optional[str] = None
    decision: Literal["ALLOW", "REQUIRE_HUMAN_REVIEW", "BLOCK"]
    action_taken: Literal["PROCEEDED_NORMAL", "PROCEEDED_NO_CONTEXT", "RETURNED_REVIEW", "BLOCKED"]
    risk_score: float
    reasons: List[str] = Field(default_factory = list)
    llm_output: Optional[str] = None
    model_version: str
    tool_result: Optional[ToolResult] = None



class ScanRequest(BaseModel):
    prompt: str = Field(..., min_length = MIN_PROMPT_LEN, max_length = MAX_PROMPT_LEN)

class ScanResponse(BaseModel):
    """
    This is the format of what the scanner returns
    """
    decision: str
    risk_score: float
    model_version: str

