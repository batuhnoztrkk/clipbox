# agents/base.py

from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel
from typing import Any

class ToolInput(BaseModel):
    pass

class BaseAgentTool(BaseTool):
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("This method must be overridden.")

    def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Async not supported.")
