# Wise (TransferWise) Agent Toolkit

The Wise Agent Toolkit enables the integration of various AI frameworks and libraries with Wise APIs to create and manage transfers programmatically. This library simplifies working with the Wise API and empowers developers to embed financial operations into AI-driven workflows using Python.

The toolkit supports multiple AI libraries through optional dependencies, allowing you to install only what you need.

Included below are basic instructions, but refer to the Python package documentation for more information.

## Python

### Installation

#### Core Installation
For the basic toolkit without any AI library integrations:
```bash
pip install wise-agent-toolkit
```

#### Integration-Specific Installation
Choose your AI library and install the corresponding extra:

**LangChain Integration:**
```bash
pip install "wise-agent-toolkit[langchain]"
```

**MCP (Model Context Protocol) Integration:**
```bash
pip install "wise-agent-toolkit[mcp]"
```

**All Integrations (if you want everything):**
```bash
pip install "wise-agent-toolkit[all]"
```

**Development Installation:**
```bash
pip install "wise-agent-toolkit[dev]"
```

> **Note for macOS/zsh users:** The package name must be quoted to prevent shell interpretation of square brackets. Alternatively, you can escape the brackets: `pip install wise-agent-toolkit\[mcp\]`

### Supported Integrations
- ✅ **LangChain** - Full support with `wise-agent-toolkit[langchain]`
- ✅ **MCP (Model Context Protocol)** - Full support with `wise-agent-toolkit[mcp]`
- 🚧 **CrewAI** - Coming soon with `wise-agent-toolkit[crewai]`
- 🚧 **AutoGen** - Coming soon with `wise-agent-toolkit[autogen]`

### Requirements
- Python 3.11+

### Usage

#### LangChain Integration
The library needs to be configured with your Wise API key, which is available in your Wise account dashboard.

```python
from wise_agent_toolkit.langchain.toolkit import WiseAgentToolkit

wise_agent_toolkit = WiseAgentToolkit(
    api_key="YOUR_WISE_API_KEY",
    host="https://api.transferwise.com",
    configuration={
        "actions": {
            "transfers": {
                "create": True,
            },
        }
    },
)
```

The toolkit works with LangChain and can be passed as a list of tools. For example:

```python
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
wise_tools = wise_agent_toolkit.get_tools()

agent = initialize_agent(
    tools=wise_tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
)

# Example usage of the agent
response = agent.run("Create a transfer of 100 EUR to John Doe's account.")
print(response)
```

#### MCP (Model Context Protocol) Integration

The MCP integration allows you to expose Wise API operations as an MCP server, which can be consumed by MCP-compatible clients like Claude Desktop, Cline, or other MCP clients.

**Installation for MCP Integration Only:**
```bash
pip install wise-agent-toolkit[mcp]
```

**Environment Setup:**
Set your Wise API credentials as environment variables:
```bash
export WISE_API_KEY="your_wise_api_key_here"
export WISE_API_HOST="https://api.transferwise.com"  # or https://api.sandbox.transferwise.tech for testing
```

**Starting the MCP Server:**
Run the MCP server from the command line:
```bash
python -m wise_agent_toolkit.mcp --api_key $WISE_API_KEY --host $WISE_API_HOST
```

Or with explicit values:
```bash
python -m wise_agent_toolkit.mcp --api_key "your_api_key" --host "https://api.transferwise.com"
```

**Using as an MCP Toolkit (Programmatic):**
If you want to integrate the MCP tools programmatically:
```python
from wise_agent_toolkit.mcp.toolkit import WiseAgentToolkit

wise_agent_toolkit = WiseAgentToolkit(
    api_key="YOUR_WISE_API_KEY",
    host="https://api.transferwise.com",
    configuration={
        "actions": {
            "transfers": {
                "create": True,
            },
        }
    },
)

# Get MCP-compatible tools
tools = wise_agent_toolkit.get_tools()
```

**Server Configuration:**
The MCP server supports the following command-line options:
- `--api_key`: Your Wise API key (required)
- `--host`: Wise API host URL (default: sandbox)
- `--server_name`: MCP server name (default: "wise-agent-toolkit")
- `--profile_id`: Wise profile ID (optional)

For production use, always use `https://api.transferwise.com` as the host.
For testing and development, use `https://api.sandbox.transferwise.tech` (default).

#### Checking Available Integrations
You can check which integrations are available in your installation:

```python
from wise_agent_toolkit import get_available_integrations

print("Available integrations:", get_available_integrations())
```

### Examples
For detailed examples, refer to the `/examples` directory in the source repository.

### Context
In some cases, you will want to provide default values for specific API requests. The context parameter allows you to specify these defaults. For example:

```python
wise_agent_toolkit = WiseAgentToolkit(
    api_key="YOUR_WISE_API_KEY",
    configuration={
        "context": {
            "profile_id": 42,
        }
    },
)
```

### Adding New Integration Support
The library is designed to be extensible. To add support for a new AI library:

1. Create a new directory under `wise_agent_toolkit/` for your integration
2. Implement the integration-specific toolkit and tool classes inheriting from the base classes
3. Add the optional dependency to `pyproject.toml`
4. Update the main `__init__.py` to conditionally import your integration

## Supported API Methods
### Quotes
- Create a quote
- Update a quote
- Get quote by ID

### Recipients
- List recipient accounts
- Create recipient account
- Get recipient account by ID
- Deactivate recipient account
- Get account requirements for a quote

### Transfers
- Create a transfer
- Get transfer by ID
- List transfers
- Cancel a transfer

### Profiles
- List profiles
- Get profile by ID

### Activities
- List activities
