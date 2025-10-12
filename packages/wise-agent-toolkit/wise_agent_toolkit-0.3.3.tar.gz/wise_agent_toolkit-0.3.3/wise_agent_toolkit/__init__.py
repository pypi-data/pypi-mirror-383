"""
Wise Agent Toolkit

A library for integrating Wise APIs with various AI frameworks and libraries.
"""

__version__ = "0.2.1"

# Core imports (always available)
from .api import WiseAPI
from .configuration import Configuration
from .tools import tools
from .integrations import get_available_integrations as _get_integration_list

# Integration-specific imports (optional)
_langchain_available = False
try:
  import langchain

  _langchain_available = True
except ImportError:
  pass

_mcp_available = False
try:
  import mcp

  _mcp_available = True
except ImportError:
  pass

# Conditional integration exports
__all__ = ["WiseAPI", "Configuration", "tools", "get_available_integrations"]

if _langchain_available:
  from . import langchain as langchain_support

  __all__.append("langchain_support")

if _mcp_available:
  from . import mcp as mcp_support

  __all__.append("mcp_support")


def get_available_integrations():
  """Return a list of available integrations."""
  return _get_integration_list()
