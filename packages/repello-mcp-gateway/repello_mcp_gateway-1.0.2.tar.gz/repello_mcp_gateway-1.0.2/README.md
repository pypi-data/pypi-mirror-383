# Repello MCP Gateway with ARGUS Integration

The Repello MCP Gateway is an advanced intermediary solution for Model Context Protocol (MCP) servers, architected to integrate directly with **Repello's ARGUS API**. It centralizes your AI infrastructure and secures it by analyzing every request and response.

The Gateway acts as an intermediary between your development environment (like Cursor or Claude Desktop) and other MCP servers. It:

1.  Reads server configurations from an `mcp.json` file.
2.  Manages the lifecycle of these configured MCP servers.
3.  Intercepts all tool calls and responses.
4.  Sends the content of each request and response to the **Repello ARGUS API** for real-time analysis.
5.  Provides a unified interface for discovering and interacting with all proxied MCPs.

## Installation

### Python (recommended)

Install the repello-mcp-gateway package:

```bash
pip install repello-mcp-gateway
```

## How It Works

The Gateway requires credentials for the Repello ARGUS API to function. You must provide a **Tracking ID** and an **API Key** via command-line arguments at startup.

When a tool is called (e.g., from an editor like Cursor), the Gateway intercepts the call. Before forwarding it to the downstream MCP server (like a filesystem server), it sends the request payload to `https://argusapi.repello.ai/analyze-prompt`. If the API approves the request, it's sent to the tool.

When the tool returns a result, the Gateway intercepts the response. It sends this response to `https://argusapi.repello.ai/analyze-response`. If the API approves, the final result is sent back to the client application.

If the ARGUS API detects a threat in either the request or response, it will return an error, and the Gateway will block the action, raising an `AnalysisError`.

## Usage

You must start the gateway with your `mcp.json` path, a valid tracking ID, and an API key.

```bash
repello-mcp-gateway --mcp-json-path ~/.cursor/mcp.json --tracking-id <your-tracking-id> --api-key <your-api-key>
```

At startup, the gateway will make a test call to the Repello API to validate the provided credentials. If the credentials are not valid, the gateway will fail to start.

### Example `mcp.json` Configuration

The client application (e.g., Cursor) should be configured to launch the gateway. The gateway, in turn, is configured to launch the downstream MCP servers. The client **only** needs to know about the gateway.

<details>
<summary>Cursor example:</summary>

```json
{
  "mcpServers": {
    "repello-mcp-gateway": {
      "command": "repello-mcp-gateway",
      "args": [
        "--mcp-json-path",
        "~/.cursor/mcp.json",
        "--tracking-id",
        "YOUR_TRACKING_ID_HERE",
        "--api-key",
        "YOUR_API_KEY_HERE"
      ],
      "servers": {
        "filesystem": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
        }
      }
    }
  }
}
```

</details>

<details>
<summary>Claude example:</summary>

First, find your python path:

```bash
which python
```

Then, configure your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "repello-mcp-gateway": {
      "command": "<python path>",
      "args": [
        "-m",
        "mcp_gateway.server",
        "--mcp-json-path",
        "<path to claude_desktop_config>",
        "--tracking-id",
        "YOUR_TRACKING_ID_HERE",
        "--api-key",
        "YOUR_API_KEY_HERE"
      ],
      "servers": {
        "filesystem": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
        }
      }
    }
  }
}
```

</details>

## Gateway Tools

The Gateway provides one primary tool for discovery:

- **`get_metadata`**: Provides information about all available proxied MCPs to help LLMs understand which tools and resources are available through the gateway.

The tools from downstream servers (like `list_directory` from the filesystem server) will be dynamically registered on the gateway with a prefix (e.g., `filesystem_list_directory`).
