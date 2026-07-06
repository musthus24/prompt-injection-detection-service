"""Pure decision-merging logic for the MCP tool-call boundary.

Deliberately does NOT reuse app.api.routes.map_scan_to_gateway_policy: that
function's review_fallback / action_taken vocabulary is chat-specific and has
no equivalent for a single tool call. This is the tool-call-boundary
equivalent, kept intentionally small.
"""

from typing import Optional, Tuple

Decision = str  # "allow" | "review" | "block"


def map_tool_call_decision(
    deterministic_violation: Optional[str],
    scanner_tier: Optional[str],
) -> Tuple[Decision, str]:
    """Merge the deterministic-check track and the scanner track.

    First block wins: a deterministic violation always blocks, regardless of
    scanner_tier (and the scanner should not even be run in that case).
    scanner_tier is one of "allow" | "review" | "high_risk" | None (None when
    the scanner was not applicable/run for this tool).
    """
    if deterministic_violation is not None:
        return "block", deterministic_violation

    if scanner_tier == "high_risk":
        return "block", "prompt_injection"
    if scanner_tier == "review":
        return "review", "prompt_injection_review"

    return "allow", "ok"
