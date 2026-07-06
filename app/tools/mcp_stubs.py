import uuid
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from app.mcp.sandbox import SANDBOX_DIR

from .registry import BaseTool


class ReadFileArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., min_length=1, max_length=260)


class ReadFileTool(BaseTool):
    """Reads from a fixed sandbox directory. Real reads only; no writes.

    Path-escape containment is enforced upstream by the MCP middleware
    (app.mcp.sandbox.check_path) before this ever runs.
    """

    name = "read_file"
    ArgsModel = ReadFileArgs

    def run(self, args: ReadFileArgs) -> Dict[str, Any]:
        full = SANDBOX_DIR / args.path
        try:
            content = full.read_text()
        except FileNotFoundError:
            return {"path": args.path, "error": "not_found"}
        return {"path": args.path, "content": content}


class FetchUrlArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(..., min_length=1, max_length=500)


class FetchUrlTool(BaseTool):
    """Stubbed fetch - never dials out. SSRF/scheme checks happen upstream
    in the MCP middleware (app.mcp.ssrf.check_url) before this ever runs."""

    name = "fetch_url"
    ArgsModel = FetchUrlArgs

    def run(self, args: FetchUrlArgs) -> Dict[str, Any]:
        return {"url": args.url, "status": 200, "body": "fixture_fetch_response"}


class SendEmailArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    to: str = Field(..., min_length=3, max_length=200)
    body: str = Field(..., min_length=1, max_length=5000)


class SendEmailTool(BaseTool):
    """Stubbed send - never actually sends. Recipient allowlisting and body
    injection scanning happen upstream in the MCP middleware before this
    ever runs."""

    name = "send_email"
    ArgsModel = SendEmailArgs

    def run(self, args: SendEmailArgs) -> Dict[str, Any]:
        return {
            "to": args.to,
            "message_id": f"fake-{uuid.uuid4()}",
            "status": "queued_stub",
        }
