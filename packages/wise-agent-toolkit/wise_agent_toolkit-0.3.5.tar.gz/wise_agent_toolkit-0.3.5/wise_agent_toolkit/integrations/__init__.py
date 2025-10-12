"""
Integration support for Wise Agent Toolkit.

This package provides integrations with various AI frameworks and libraries.
Each integration is optional and requires the respective library to be installed.
"""

from typing import List

# Check for available integrations
_available_integrations = []

# LangChain support
try:
  import langchain

  _available_integrations.append("langchain")
except ImportError:
  pass

# MCP support
try:
  import mcp

  _available_integrations.append("mcp")
except ImportError:
  pass


# Future integration checks can be added here
# try:
#     import crewai
#     _available_integrations.append("crewai")
# except ImportError:
#     pass

def get_available_integrations() -> List[str]:
  """Return a list of available integrations."""
  return _available_integrations.copy()


def check_integration_availability(integration: str) -> bool:
  """Check if a specific integration is available."""
  return integration in _available_integrations


__all__ = ["get_available_integrations", "check_integration_availability"]
