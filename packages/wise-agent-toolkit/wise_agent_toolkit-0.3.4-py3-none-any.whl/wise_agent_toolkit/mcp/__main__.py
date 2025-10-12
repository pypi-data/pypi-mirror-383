"""
Main entry point for the MCP module.

This allows running the MCP server with:
python -m wise_agent_toolkit.mcp --api-key "your_api_key" --host "https://api.transferwise.com"
"""

from .server import main

if __name__ == "__main__":
    main()