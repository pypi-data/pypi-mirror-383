"""
Base integration for Wise Agent Toolkit.

This module provides base classes and utilities for integrating with different AI frameworks and libraries.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

from ..api import WiseAPI
from ..configuration import Configuration


class BaseIntegrationTool(ABC):
  """Base class for integration-specific tools."""

  def __init__(self, wise_api: WiseAPI, method: str, name: str = "", description: str = "",
               args_schema: Optional[Type[BaseModel]] = None):
    self.wise_api = wise_api
    self.method = method
    self.name = name or method
    self.description = description
    self.args_schema = args_schema

  @abstractmethod
  def execute(self, *args: Any, **kwargs: Any) -> str:
    """Execute the tool with the given arguments."""
    pass


class BaseIntegrationToolkit(ABC):
  """Base class for integration-specific toolkits."""

  def __init__(self, api_key: str, host: str = "https://api.sandbox.transferwise.tech",
               configuration: Optional[Configuration] = None):
    self.api_key = api_key
    self.host = host
    self.configuration = configuration
    self._wise_api = None

  @property
  def wise_api(self) -> WiseAPI:
    """Lazy initialization of WiseAPI."""
    if self._wise_api is None:
      context = self.configuration.get("context") if self.configuration else None
      self._wise_api = WiseAPI(api_key=self.api_key, host=self.host, context=context)
    return self._wise_api

  @abstractmethod
  def get_tools(self) -> List[Any]:
    """Get the tools in the toolkit."""
    pass

  @abstractmethod
  def create_tool(self, tool_config: Dict[str, Any]) -> Any:
    """Create an integration-specific tool from configuration."""
    pass
