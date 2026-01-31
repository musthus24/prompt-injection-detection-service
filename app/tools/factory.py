from .registry import ToolRegistry
from .stubs import PdfReadTool, WebSearchTool


def build_default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(WebSearchTool())
    reg.register(PdfReadTool())
    return reg
