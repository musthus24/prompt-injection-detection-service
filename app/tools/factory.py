from .mcp_stubs import FetchUrlTool, ReadFileTool, SendEmailTool
from .registry import ToolRegistry
from .stubs import PdfReadTool, WebSearchTool


def build_default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(WebSearchTool())
    reg.register(PdfReadTool())
    return reg


def build_mcp_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(ReadFileTool())
    reg.register(FetchUrlTool())
    reg.register(SendEmailTool())
    return reg
