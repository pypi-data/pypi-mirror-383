"""
MCP Server implementation for Wise Agent Toolkit.

Provides a complete MCP server that exposes Wise API operations as MCP tools.
"""

import logging
import argparse
import os
from typing import Optional
from pathlib import Path

# Handle imports for both module and standalone execution
try:
  from ..configuration import Configuration, Context, ACTIONS_ALL
  from ..api import WiseAPI
  from .toolkit import WiseAgentToolkit
  from .tool import _fix_mcp_schema
except ImportError:
  # If relative imports fail, try absolute imports
  import sys

  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
  from wise_agent_toolkit.configuration import Configuration, Context
  from wise_agent_toolkit.api import WiseAPI
  from wise_agent_toolkit.mcp.toolkit import WiseAgentToolkit
  from wise_agent_toolkit.mcp.tool import _fix_mcp_schema

# Check for MCP availability
try:
  from mcp.server import Server
  from mcp.server.stdio import stdio_server
  from mcp.types import TextContent, Tool

  _MCP_AVAILABLE = True
except ImportError:
  _MCP_AVAILABLE = False
  Server = None


async def serve(
  api_key: str,
  host: str = "https://api.sandbox.transferwise.tech",
  server_name: str = "wise-agent-toolkit",
  profile_id: Optional[int] = None
) -> None:
  """Serve the MCP server."""
  logger = logging.getLogger(__name__)

  if not _MCP_AVAILABLE:
    logger.error("MCP is not available. Install it with: pip install wise-agent-toolkit[mcp]")
    return

  # Initialize the API client and toolkit locally
  context = Context(profile_id=profile_id)
  toolkit = WiseAgentToolkit(
    api_key=api_key,
    host=host,
    configuration={"actions": ACTIONS_ALL, "context": context}
  )

  # Create a dictionary mapping tool names to tool instances
  tool_name_and_tool = {tool.name: tool for tool in toolkit.get_tools()}

  server = Server(server_name)

  @server.list_tools()
  async def list_tools() -> list[Tool]:
    """List all available Wise API tools."""
    tools = []
    for tool in tool_name_and_tool.values():
      # Convert WiseTool to MCP Tool format with schema fix
      input_schema = {}
      if tool.args_schema:
        original_schema = tool.args_schema.model_json_schema()
        input_schema = _fix_mcp_schema(original_schema)

      tools.append(Tool(
        name=tool.name,
        description=tool.description,
        inputSchema=input_schema
      ))

    return tools

  @server.call_tool()
  async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a Wise API tool."""
    try:
      # Look up the tool in our dictionary
      if name not in tool_name_and_tool:
        return [TextContent(
          type="text",
          text=f"Tool '{name}' not found"
        )]

      tool = tool_name_and_tool[name]
      result = tool.execute(arguments)
      return [TextContent(
        type="text",
        text=result
      )]
    except Exception as e:
      logger.error(f"Error executing tool {name}: {str(e)}")
      return [TextContent(
        type="text",
        text=f"Error executing {name}: {str(e)}"
      )]

  # Run the server
  options = server.create_initialization_options()
  async with stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream, options, raise_exceptions=True)


def main():
  """Main entry point for running the MCP server."""
  # Set up logging to stderr
  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # This writes to stderr by default
  )
  logger = logging.getLogger(__name__)

  parser = argparse.ArgumentParser(description="Wise Agent Toolkit MCP Server")
  parser.add_argument(
    "--api_key",
    default=os.getenv("WISE_API_KEY"),
    help="Wise API key (default: from WISE_API_KEY environment variable)"
  )
  parser.add_argument(
    "--host",
    default=os.getenv("WISE_API_HOST", "https://api.sandbox.transferwise.tech"),
    help="Wise API host (default: from WISE_API_HOST environment variable or sandbox)"
  )
  parser.add_argument(
    "--server_name",
    default="wise-agent-toolkit",
    help="MCP server name"
  )
  parser.add_argument(
    "--profile_id",
    type=int,
    default=None,
    help="Wise profile ID"
  )

  args = parser.parse_args()

  if not args.api_key:
    logger.error("API key is required. Provide it via --api-key or WISE_API_KEY environment variable.")
    return

  import asyncio
  asyncio.run(serve(
    api_key=args.api_key,
    host=args.host,
    server_name=args.server_name,
    profile_id=args.profile_id,
  ))


if __name__ == "__main__":
  main()
