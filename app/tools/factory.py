from .registry import ToolRegistry
from .stubs import WebSearchTool, PdfReadTool


def build_default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(WebSearchTool())
    reg.register(PdfReadTool())
    return reg
