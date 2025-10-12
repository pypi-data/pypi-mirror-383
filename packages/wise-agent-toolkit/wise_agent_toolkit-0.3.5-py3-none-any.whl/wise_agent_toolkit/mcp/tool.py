"""
MCP Tool implementation for Wise Agent Toolkit.

Provides MCP-compatible tool wrapper for Wise API operations.
"""

import json
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

from ..integrations.base import BaseIntegrationTool
from ..api import WiseAPI

# Check for MCP availability
try:
    from mcp.types import Tool, TextContent
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    # Provide fallback types
    class Tool:
        def __init__(self, *args, **kwargs):
            pass

    class TextContent:
        def __init__(self, *args, **kwargs):
            pass


def _fix_mcp_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix schema for MCP clients by removing optional (null) types for non-string fields.

    This is a workaround for MCP clients that send strings for optional integer fields.
    We keep the original schema intact but modify the MCP-exposed version to require
    proper types for non-string fields.

    Args:
        schema: The original JSON schema

    Returns:
        Modified schema safe for MCP clients
    """
    if not isinstance(schema, dict):
        return schema

    # Create a deep copy to avoid modifying the original
    fixed_schema = {}

    for key, value in schema.items():
        if key == "properties" and isinstance(value, dict):
            # Fix each property
            fixed_properties = {}
            for prop_name, prop_schema in value.items():
                if isinstance(prop_schema, dict) and "anyOf" in prop_schema:
                    # Handle anyOf pattern used by Pydantic for Optional fields
                    any_of = prop_schema["anyOf"]
                    if isinstance(any_of, list) and len(any_of) == 2:
                        # Check if this is Optional[Type] pattern (Type and null)
                        non_null_types = [t for t in any_of if t.get("type") != "null"]
                        null_types = [t for t in any_of if t.get("type") == "null"]

                        if len(non_null_types) == 1 and len(null_types) == 1:
                            # This is an Optional field
                            field_type = non_null_types[0].get("type")

                            # For non-string optional fields, make them required with proper type
                            # This prevents MCP clients from sending strings for int/number fields
                            if field_type and field_type != "string":
                                # Use the non-null type directly
                                fixed_properties[prop_name] = non_null_types[0]
                            else:
                                # Keep string optionals as-is
                                fixed_properties[prop_name] = prop_schema
                        else:
                            fixed_properties[prop_name] = prop_schema
                    else:
                        fixed_properties[prop_name] = prop_schema
                else:
                    # Recursively fix nested schemas
                    fixed_properties[prop_name] = _fix_mcp_schema(prop_schema)
            fixed_schema[key] = fixed_properties
        elif isinstance(value, dict):
            # Recursively fix nested objects
            fixed_schema[key] = _fix_mcp_schema(value)
        elif isinstance(value, list):
            # Recursively fix lists
            fixed_schema[key] = [_fix_mcp_schema(item) if isinstance(item, dict) else item for item in value]
        else:
            fixed_schema[key] = value

    return fixed_schema


class WiseTool(BaseIntegrationTool):
    """MCP-compatible tool for Wise API operations."""

    def __init__(
        self,
        name: str,
        description: str,
        method: str,
        wise_api: WiseAPI,
        args_schema: Optional[Type[BaseModel]] = None,
    ):
        if not _MCP_AVAILABLE:
            raise ImportError(
                "MCP is required for this functionality. "
                "Install it with: pip install wise-agent-toolkit[mcp]"
            )

        super().__init__(
            wise_api=wise_api,
            method=method,
            name=name,
            description=description,
            args_schema=args_schema
        )

    def to_mcp_tool(self) -> Tool:
        """Convert to MCP Tool format."""
        input_schema = {}
        if self.args_schema:
            # Generate schema and apply MCP client fix
            original_schema = self.args_schema.model_json_schema()
            input_schema = _fix_mcp_schema(original_schema)

        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=input_schema
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        """Execute the tool with MCP-formatted arguments."""
        try:
            # Use the WiseAPI.run method to execute the tool
            result = self.wise_api.run(self.method, **arguments)
            return result

        except Exception as e:
            return f"Error executing {self.method}: {str(e)}"

    async def call(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """MCP-compatible call method."""
        result = self.execute(arguments)
        return [TextContent(
            type="text",
            text=result
        )]