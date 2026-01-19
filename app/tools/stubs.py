from typing import Any, Dict, Literal
from pydantic import BaseModel, ConfigDict, Field
from .registry import BaseTool


class WebSearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., min_length=1, max_length=200)
    top_k: int = Field(default=3, ge=1, le=5)


class WebSearchTool(BaseTool):
    name = "web_search"
    ArgsModel = WebSearchArgs

    def run(self, args: WebSearchArgs) -> Dict[str, Any]:
        return {
            "results": [
                {"title": "fixture_result_1", "snippet": f"query={args.query}"},
                {"title": "fixture_result_2", "snippet": f"top_k={args.top_k}"},
            ]
        }


class PdfReadArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: Literal["policy_pdf", "readme_pdf"]
    page: int = Field(default=1, ge=1, le=5)


class PdfReadTool(BaseTool):
    name = "pdf_read"
    ArgsModel = PdfReadArgs

    def run(self, args: PdfReadArgs) -> Dict[str, Any]:
        return {"text": f"fixture_pdf:{args.doc_id}:page={args.page}"}
