# MCP Server Setup Guide

## What We've Built

We've created 4 different MCP servers in the `mcp-server` directory:

### 1. **`my_mcp_server.py`** - Comprehensive General Purpose Server
- **14+ tools** for various tasks
- File system operations, system info, web tools, data processing
- Perfect for everyday use with Claude

### 2. **`simple_server.py`** - Minimal Test Server
- **3 basic tools** (hello, add, multiply)
- Great for testing and learning MCP basics

### 3. **`code_analysis_server.py`** - Code Analysis Server
- **6 specialized tools** for code analysis
- Analyze Python files, find functions, check syntax, count lines
- Ideal for developers and code review tasks

### 4. **`weather_server.py`** - Weather API Server
- **5 weather-related tools**
- Get current weather, forecasts, air quality, convert temperatures
- Demonstrates external API integration

## Quick Start

### 1. Setup Environment
```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Test a Server
```bash
# Test the simple server
python3 simple_server.py

# In another terminal, test with:
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 simple_server.py
```

### 3. Register with Claude

Edit your Claude MCP configuration:

**macOS/Linux:** `~/.config/claude/mcp.json`
**Windows:** `%APPDATA%\Claude\mcp.json`

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python3",
      "args": ["/FULL/PATH/TO/mcp-server/my_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/FULL/PATH/TO/mcp-server"
      }
    },
    "code-analysis": {
      "command": "python3", 
      "args": ["/FULL/PATH/TO/mcp-server/code_analysis_server.py"]
    }
  }
}
```

Replace `/FULL/PATH/TO/` with your actual path.

### 4. Restart Claude and Use Tools!

## Using with Claude

Once configured, you can ask Claude to use the tools:

```
"Can you analyze the current directory structure?"
"Check the weather in London for me"
"Count the lines of code in this project"
"Read the contents of README.md"
```

## Advanced Configuration

### Environment Variables
For the weather server to get real data:
```bash
export OPENWEATHER_API_KEY="your_api_key_here"
```

### Multiple Servers
You can run multiple servers simultaneously by adding multiple entries to `mcp.json`.

## Testing Your Own Tools

1. Copy `simple_server.py` as a template
2. Add your own tools with `@server.tool()` decorator
3. Test with the MCP Inspector:
```bash
npx @anthropics/mcp-inspector python3 your_server.py
```

## Common Issues & Solutions

### 1. "Server not found" error
- Check the path in `mcp.json` is correct
- Ensure Python can execute the script
- Check file permissions: `chmod +x your_server.py`

### 2. "Module not found" error
- Make sure dependencies are installed: `pip install mcp httpx`
- Check `PYTHONPATH` in environment variables

### 3. Server starts but tools don't appear
- Restart Claude completely
- Check server logs for errors
- Verify tool definitions have proper docstrings

### 4. Slow response times
- Tools should be async (`async def`)
- Use timeouts for external API calls
- Cache frequent requests if possible

## Creating Custom Tools

### Basic Tool Template
```python
@server.tool()
async def my_tool(param1: str, param2: int = 10) -> str:
    """Description of what the tool does.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter with default
    """
    # Your implementation here
    return f"Result: {param1} {param2}"
```

### Best Practices
1. **Clear descriptions**: Claude uses these to decide when to call tools
2. **Type hints**: Helps Claude understand parameter types
3. **Error handling**: Always return helpful error messages
4. **Async by default**: Use `async/await` for I/O operations
5. **Security**: Never expose sensitive operations without validation

## Resources

- [Official MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [Example MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Claude Desktop Documentation](https://docs.anthropic.com/claude/docs/claude-desktop)