"""Structured audit logging for MCP tool-call decisions.

Follows the same ad-hoc logger.info(event, extra={...}) convention already
used in app/api/routes.py, on its own named logger.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("mcp_gateway")

_REDACT_KEYS = {"body"}
_MAX_VALUE_LEN = 80


def _redact_args(raw_args: Dict[str, Any]) -> Dict[str, Any]:
    redacted = {}
    for key, value in raw_args.items():
        if key in _REDACT_KEYS:
            redacted[key] = "<redacted>"
        elif isinstance(value, str) and len(value) > _MAX_VALUE_LEN:
            redacted[key] = value[:_MAX_VALUE_LEN] + "...<truncated>"
        else:
            redacted[key] = value
    return redacted


def log_decision(
    tool: str,
    raw_args: Dict[str, Any],
    decision: str,
    reason: str,
    caller: Optional[str] = None,
) -> None:
    logger.info(
        "mcp_tool_call_decision",
        extra={
            "tool": tool,
            "args": _redact_args(raw_args),
            "decision": decision,
            "reason": reason,
            "caller": caller,
        },
    )
