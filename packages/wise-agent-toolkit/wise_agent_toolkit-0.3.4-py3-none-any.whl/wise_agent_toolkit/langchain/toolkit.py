from typing import List, Optional, Dict, Any
from pydantic import PrivateAttr

from ..tools import tools
from ..configuration import Configuration, is_tool_allowed
from ..integrations.base import BaseIntegrationToolkit

# Check for LangChain availability
try:
  from .tool import WiseTool

  _LANGCHAIN_AVAILABLE = True
except ImportError as e:
  _LANGCHAIN_AVAILABLE = False
  _LANGCHAIN_ERROR = str(e)


  # Provide a fallback class for WiseTool
  class WiseTool:
    def __init__(self, *args, **kwargs):
      raise ImportError(
        "LangChain is required for this functionality. "
        "Install it with: pip install wise-agent-toolkit[langchain]"
      )


class WiseAgentToolkit(BaseIntegrationToolkit):
  """Wise Agent Toolkit for LangChain integration."""

  _tools: List = PrivateAttr(default=[])

  def __init__(
    self,
    api_key: str,
    host: str = "https://api.sandbox.transferwise.tech",
    configuration: Optional[Configuration] = None
  ):
    if not _LANGCHAIN_AVAILABLE:
      raise ImportError(
        "LangChain is required for this functionality. "
        "Install it with: pip install wise-agent-toolkit[langchain]"
      )

    super().__init__(api_key=api_key, host=host, configuration=configuration)

    filtered_tools = [
      tool for tool in tools if is_tool_allowed(tool, configuration)
    ]

    self._tools = [
      self.create_tool(tool) for tool in filtered_tools
    ]

  def get_tools(self) -> List:
    """Get the tools in the toolkit."""
    return self._tools

  def create_tool(self, tool_config: Dict[str, Any]) -> WiseTool:
    """Create a LangChain-specific tool from configuration."""
    return WiseTool(
      name=tool_config["method"],
      description=tool_config["description"],
      method=tool_config["method"],
      wise_api=self.wise_api,
      args_schema=tool_config.get("args_schema", None),
    )
