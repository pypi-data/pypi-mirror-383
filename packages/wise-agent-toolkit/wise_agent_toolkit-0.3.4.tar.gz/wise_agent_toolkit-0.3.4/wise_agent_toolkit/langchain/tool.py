from __future__ import annotations

from typing import Any, Optional, Type
from pydantic import BaseModel, Field

# Check for LangChain availability
try:
  from langchain.tools import BaseTool

  _LANGCHAIN_AVAILABLE = True
except ImportError:
  _LANGCHAIN_AVAILABLE = False


  # Create a dummy base class if LangChain is not available
  class BaseTool:
    pass

from ..api import WiseAPI
from ..integrations.base import BaseIntegrationTool


class WiseTool(BaseTool, BaseIntegrationTool):
  """Tool for interacting with the Wise API using LangChain."""

  # Define Pydantic fields for the attributes that BaseIntegrationTool uses
  wise_api: WiseAPI = Field(...)
  method: str = Field(...)

  def __init__(self, wise_api: WiseAPI, method: str, name: str = "", description: str = "",
               args_schema: Optional[Type[BaseModel]] = None):
    if not _LANGCHAIN_AVAILABLE:
      raise ImportError(
        "LangChain is required for this functionality. "
        "Install it with: pip install wise-agent-toolkit[langchain]"
      )

    # Initialize LangChain BaseTool with Pydantic fields
    BaseTool.__init__(
      self,
      name=name or method,
      description=description,
      args_schema=args_schema,
      wise_api=wise_api,
      method=method
    )

  def _run(
    self,
    *args: Any,
    **kwargs: Any,
  ) -> str:
    """Use the Wise API to run an operation (LangChain interface)."""
    return self.execute(*args, **kwargs)

  def execute(self, *args: Any, **kwargs: Any) -> str:
    """Execute the tool with the given arguments (BaseIntegrationTool interface)."""
    return self.wise_api.run(self.method, *args, **kwargs)
