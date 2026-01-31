from __future__ import annotations

from typing import Any, Dict, Type

from pydantic import BaseModel


class UnknownToolError(Exception):
    pass


class BaseTool:
    """
    A tool is just:
      - a stable name (string)
      - an ArgsModel (Pydantic schema)
      - a run() method that returns a dict
    """
    name: str
    ArgsModel: Type[BaseModel]

    def run(self, args: BaseModel) -> Dict[str, Any]:
        raise NotImplementedError


class ToolRegistry:
    """
    Central allowlist. Only tools registered here can run.
    Also enforces strict args validation using each tool's ArgsModel.
    """
    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def execute(self, name: str, raw_args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._tools:
            raise UnknownToolError(f"unknown_tool:{name}")

        tool = self._tools[name]


        args_obj = tool.ArgsModel.model_validate(raw_args)

        return tool.run(args_obj)

