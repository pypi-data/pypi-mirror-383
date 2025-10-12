"""
MCP (Model Context Protocol) integration for Wise Agent Toolkit.

This module provides integration with the Model Context Protocol standard,
allowing Wise Agent Toolkit to be used as an MCP server.
"""

# Check for MCP availability
try:
    from .server import WiseMCPServer
    from .toolkit import WiseAgentToolkit
    _MCP_AVAILABLE = True
except ImportError as e:
    _MCP_AVAILABLE = False
    _MCP_ERROR = str(e)

    # Provide fallback classes
    class WiseMCPServer:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "MCP is required for this functionality. "
                "Install it with: pip install wise-agent-toolkit[mcp]"
            )

    class WiseAgentToolkit:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "MCP is required for this functionality. "
                "Install it with: pip install wise-agent-toolkit[mcp]"
            )

__all__ = ["WiseMCPServer", "WiseAgentToolkit", "_MCP_AVAILABLE"]
