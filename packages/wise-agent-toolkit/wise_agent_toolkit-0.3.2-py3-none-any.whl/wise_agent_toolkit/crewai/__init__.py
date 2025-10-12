"""
CrewAI integration for Wise Agent Toolkit.

This module will provide CrewAI-specific tools and utilities for the Wise API.
Requires CrewAI to be installed: pip install wise-agent-toolkit[crewai]

This is a placeholder for future implementation.
"""

# Check for CrewAI availability
try:
  import crewai

  _CREWAI_AVAILABLE = True
except ImportError:
  _CREWAI_AVAILABLE = False

# Future implementation will go here
# from .toolkit import WiseCrewAIToolkit
# from .tool import WiseCrewAITool

__all__ = []


def check_crewai_availability():
  """Check if CrewAI is available for use."""
  if not _CREWAI_AVAILABLE:
    raise ImportError(
      "CrewAI is required for this functionality. "
      "Install it with: pip install wise-agent-toolkit[crewai]"
    )
  return True
