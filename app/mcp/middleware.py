"""The MCP tool-call boundary: on_call_tool middleware.

Every call is intercepted here before the tool ever runs. Two tracks feed a
single decision:
  - deterministic argument checks (path traversal, SSRF, recipient allowlist)
  - the existing, unmodified Scanner, run only on send_email's free-text body

First block wins. See app.mcp.policy.map_tool_call_decision for the merge.
"""

from typing import Any, Dict, Optional, Tuple

from pydantic import ValidationError

from app.services.detector import scan_prompt
from app.tools.factory import build_mcp_registry

from . import ssrf
from .allowlist import ALLOWED_RECIPIENTS
from .audit import log_decision
from .policy import map_tool_call_decision
from .sandbox import check_path

_registry = build_mcp_registry()


def _deterministic_check(name: str, args: Any) -> Optional[str]:
    if name == "read_file":
        return check_path(args.path)
    if name == "fetch_url":
        return ssrf.check_url(args.url)
    if name == "send_email":
        if args.to not in ALLOWED_RECIPIENTS:
            return "recipient_not_allowed"
        return None
    return None


def decide(name: str, raw_args: Dict[str, Any]) -> Tuple[str, str, Optional[Any]]:
    """Pure decision function, factored out of the FastMCP hook so it's
    testable/usable (eval harness, unit tests) without a real MiddlewareContext.

    Returns (decision, reason, args_obj). args_obj is None when the call
    never got past schema validation.
    """
    tool = _registry.get(name)
    if tool is None:
        return "block", "unknown_tool", None

    try:
        args_obj = tool.ArgsModel.model_validate(raw_args)
    except ValidationError:
        return "block", "schema_invalid", None

    deterministic_violation = _deterministic_check(name, args_obj)

    scanner_tier = None
    if deterministic_violation is None and name == "send_email":
        scan_decision, _risk_score, _model_version = scan_prompt(args_obj.body)
        scanner_tier = scan_decision

    decision, reason = map_tool_call_decision(deterministic_violation, scanner_tier)
    return decision, reason, args_obj


def _blocked_tool_result(reason: str):
    # Imported lazily so this module can be unit-tested without fastmcp
    # installed being a hard requirement for the pure `decide()` path.
    from fastmcp.tools.tool import ToolResult

    return ToolResult(content=f"blocked: {reason}", is_error=True)


async def on_call_tool(context, call_next):
    name = context.message.name
    raw_args = context.message.arguments or {}

    decision, reason, args_obj = decide(name, raw_args)

    log_decision(tool=name, raw_args=raw_args, decision=decision, reason=reason)

    if decision == "block":
        return _blocked_tool_result(reason)
    if decision == "review":
        # Held + logged, no UI: not executed in this demo (no review queue to
        # hand it to). Distinct reason so the eval harness/logs can tell it
        # apart from a hard block.
        return _blocked_tool_result(reason)

    return await call_next(context)


def _make_middleware():
    from fastmcp.server.middleware import Middleware

    class ToolCallGatewayMiddleware(Middleware):
        async def on_call_tool(self, context, call_next):
            return await on_call_tool(context, call_next)

    return ToolCallGatewayMiddleware()
