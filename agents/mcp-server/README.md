# MCP Server Examples

This directory contains examples of MCP (Model Context Protocol) servers that can be used with Claude.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI assistants like Claude to interact with external services through a standardized interface. MCP servers expose:
- **Tools**: Functions that Claude can call
- **Resources**: Data that Claude can read
- **Prompts**: Pre-built prompt templates

## Files

1. **`my_mcp_server.py`** - Comprehensive server with 14+ tools
2. **`simple_server.py`** - Minimal server for testing
3. **`requirements.txt`** - Python dependencies

## Installation

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Test with MCP Inspector:
```bash
npx @anthropics/mcp-inspector python3 my_mcp_server.py
```

### Or run directly:
```bash
python3 my_mcp_server.py
```

## Register with Claude

To use with Claude Desktop or Claude Code:

1. Edit the MCP configuration file:
   - **macOS/Linux**: `~/.config/claude/mcp.json`
   - **Windows**: `%APPDATA%\Claude\mcp.json`

2. Add configuration:
   ```json
   {
     "mcpServers": {
       "my-mcp-server": {
         "command": "python3",
         "args": ["/full/path/to/mcp-server/my_mcp_server.py"],
         "env": {
           "PYTHONPATH": "/full/path/to/mcp-server"
         }
       }
     }
   }
   ```

3. Restart Claude

## Available Tools in `my_mcp_server.py`

### Basic Utilities
- `hello(name)` - Greet someone
- `add_numbers(a, b)` - Add two numbers
- `calculate(expression)` - Evaluate math expression

### File System
- `read_file(filepath)` - Read file contents
- `write_file(filepath, content, append)` - Write to file
- `list_directory(path)` - List directory contents
- `get_file_info(filepath)` - Get file information

### System Information
- `system_info()` - Get system details
- `disk_usage(path)` - Check disk usage

### Web/API
- `fetch_url(url)` - Fetch content from URL
- `check_website(url)` - Check website status

### Data Processing
- `format_json(json_string)` - Format and validate JSON
- `text_statistics(text)` - Analyze text statistics
- `text_wrap(text, width)` - Wrap text to specified width

## Testing

### Manual Test
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 my_mcp_server.py
```

### Test Tool Call
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"hello","arguments":{"name":"Alice"}}}' | python3 my_mcp_server.py
```

## Creating Your Own MCP Server

1. Start with the template in `simple_server.py`
2. Add your own tools using the `@server.tool()` decorator
3. Test with the MCP Inspector
4. Register with Claude

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Examples](https://github.com/modelcontextprotocol/servers)