[![Add to Cursor](https://fastmcp.me/badges/cursor_dark.svg)](https://fastmcp.me/MCP/Details/1298/gotify-notifications)
[![Add to VS Code](https://fastmcp.me/badges/vscode_dark.svg)](https://fastmcp.me/MCP/Details/1298/gotify-notifications)
[![Add to Claude](https://fastmcp.me/badges/claude_dark.svg)](https://fastmcp.me/MCP/Details/1298/gotify-notifications)
[![Add to ChatGPT](https://fastmcp.me/badges/chatgpt_dark.svg)](https://fastmcp.me/MCP/Details/1298/gotify-notifications)
[![Add to Codex](https://fastmcp.me/badges/codex_dark.svg)](https://fastmcp.me/MCP/Details/1298/gotify-notifications)
[![Add to Gemini](https://fastmcp.me/badges/gemini_dark.svg)](https://fastmcp.me/MCP/Details/1298/gotify-notifications)

# MCP-gotify

MCP server for sending gotify push notifications.

## Installation

### stdio

claude json:

```json5
{
    "mcpServers": {
        "mcp-gotify": {
            "command": "uvx",
            "args": ["mcp-gotify"],
            "env": {
                "GOTIFY_SERVER": "http://localhost:2081", // Change this to your gotify server
                "GOTIFY_TOKEN": "YOUR TOKEN" // Get this from gotify
            }
        }
    }
}
```

### sse

```bash
git clone https://github.com/SecretiveShell/mcp-gotify
cd mcp-gotify
uv run mcp-gotify-sse
```

## License

MIT
