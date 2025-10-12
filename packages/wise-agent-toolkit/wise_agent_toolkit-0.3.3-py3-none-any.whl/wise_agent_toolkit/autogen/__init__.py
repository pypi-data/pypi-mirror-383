"""
AutoGen integration for Wise Agent Toolkit.

This module will provide AutoGen-specific tools and utilities for the Wise API.
Requires AutoGen to be installed: pip install wise-agent-toolkit[autogen]

This is a placeholder for future implementation.
"""

# Check for AutoGen availability
try:
  import autogen

  _AUTOGEN_AVAILABLE = True
except ImportError:
  _AUTOGEN_AVAILABLE = False

# Future implementation will go here
# from .toolkit import WiseAutoGenToolkit
# from .tool import WiseAutoGenTool

__all__ = []


def check_autogen_availability():
  """Check if AutoGen is available for use."""
  if not _AUTOGEN_AVAILABLE:
    raise ImportError(
      "AutoGen is required for this functionality. "
      "Install it with: pip install wise-agent-toolkit[autogen]"
    )
  return True
