"""
LangChain integration for Wise Agent Toolkit.

This module provides LangChain-specific tools and utilities for the Wise API.
Requires LangChain to be installed: pip install wise-agent-toolkit[langchain]
"""

# Check for LangChain availability
try:
  import langchain

  _LANGCHAIN_AVAILABLE = True
except ImportError:
  _LANGCHAIN_AVAILABLE = False

# Conditional imports
if _LANGCHAIN_AVAILABLE:
  from .toolkit import WiseAgentToolkit
  from .tool import WiseTool

  __all__ = ["WiseAgentToolkit", "WiseTool"]
else:
  __all__ = []


def check_langchain_availability():
  """Check if LangChain is available for use."""
  if not _LANGCHAIN_AVAILABLE:
    raise ImportError(
      "LangChain is required for this functionality. "
      "Install it with: pip install wise-agent-toolkit[langchain]"
    )
  return True
