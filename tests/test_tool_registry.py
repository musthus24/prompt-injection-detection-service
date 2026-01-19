import pytest
from pydantic import ValidationError
from app.tools.factory import build_default_registry
from app.tools.registry import UnknownToolError


def test_unknown_tool_rejected():
    reg = build_default_registry()
    with pytest.raises(UnknownToolError):
        reg.execute("not_a_real_tool", {})


def test_extra_args_rejected():
    reg = build_default_registry()
    with pytest.raises(ValidationError):
        reg.execute("web_search", {"query": "hi", "unexpected": 123})
