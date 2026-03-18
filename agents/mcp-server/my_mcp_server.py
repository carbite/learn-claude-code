#!/usr/bin/env python3
"""my_mcp_server.py - A comprehensive MCP server with various tools"""

import os
import sys
import json
import math
import platform
import datetime
import subprocess
import textwrap
from typing import Dict, List, Any, Optional
from pathlib import Path

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Create server instance
server = Server("my-mcp-server")


# ==================== Basic Utility Tools ====================

@server.tool()
async def hello(name: str = "World") -> str:
    """Say hello to someone.
    
    Args:
        name: The name to greet (default: "World")
    """
    return f"Hello, {name}! 👋"


@server.tool()
async def add_numbers(a: float, b: float) -> str:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    return f"{a} + {b} = {a + b}"


@server.tool()
async def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: Mathematical expression (e.g., "2 + 3 * 4")
    """
    try:
        # Safe evaluation - only basic math operations
        allowed_names = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'pow': pow, 'sqrt': math.sqrt, 'log': math.log,
            'log10': math.log10, 'exp': math.exp, 'sin': math.sin,
            'cos': math.cos, 'tan': math.tan, 'pi': math.pi, 'e': math.e
        }
        
        # Compile and evaluate safely
        code = compile(expression, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"Use of {name!r} not allowed")
        
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


# ==================== File System Tools ====================

@server.tool()
async def read_file(filepath: str) -> str:
    """Read the contents of a file.
    
    Args:
        filepath: Path to the file to read
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File '{filepath}' does not exist"
        if not path.is_file():
            return f"Error: '{filepath}' is not a file"
        
        content = path.read_text()
        return f"Contents of '{filepath}':\n\n{content}"
    except Exception as e:
        return f"Error reading file: {e}"


@server.tool()
async def write_file(filepath: str, content: str, append: bool = False) -> str:
    """Write content to a file.
    
    Args:
        filepath: Path to the file to write
        content: Content to write to the file
        append: Whether to append to the file (default: False, overwrite)
    """
    try:
        path = Path(filepath)
        mode = 'a' if append else 'w'
        
        with open(path, mode) as f:
            f.write(content)
        
        action = "appended to" if append else "written to"
        return f"Content successfully {action} '{filepath}'"
    except Exception as e:
        return f"Error writing file: {e}"


@server.tool()
async def list_directory(path: str = ".") -> str:
    """List files and directories in a path.
    
    Args:
        path: Directory path to list (default: current directory)
    """
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"Error: Path '{path}' does not exist"
        if not dir_path.is_dir():
            return f"Error: '{path}' is not a directory"
        
        items = []
        for item in dir_path.iterdir():
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            elif item.is_file():
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({size} bytes)")
            else:
                items.append(f"❓ {item.name}")
        
        result = f"Contents of '{path}':\n\n" + "\n".join(sorted(items))
        return result
    except Exception as e:
        return f"Error listing directory: {e}"


@server.tool()
async def get_file_info(filepath: str) -> str:
    """Get information about a file.
    
    Args:
        filepath: Path to the file
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: '{filepath}' does not exist"
        
        stat = path.stat()
        info = {
            "Path": str(path.absolute()),
            "Type": "Directory" if path.is_dir() else "File",
            "Size": f"{stat.st_size} bytes",
            "Created": datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "Modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "Permissions": oct(stat.st_mode)[-3:],
        }
        
        result = "File Information:\n\n"
        for key, value in info.items():
            result += f"{key}: {value}\n"
        
        return result
    except Exception as e:
        return f"Error getting file info: {e}"


# ==================== System Information Tools ====================

@server.tool()
async def system_info() -> str:
    """Get information about the current system."""
    info = {
        "Platform": platform.platform(),
        "System": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "Current Directory": os.getcwd(),
        "User": os.getenv("USER", "Unknown"),
        "Time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    result = "System Information:\n\n"
    for key, value in info.items():
        result += f"{key}: {value}\n"
    
    return result


@server.tool()
async def disk_usage(path: str = ".") -> str:
    """Get disk usage information for a path.
    
    Args:
        path: Path to check disk usage for (default: current directory)
    """
    try:
        import shutil
        
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        percent_used = (usage.used / usage.total) * 100
        
        result = f"Disk Usage for '{path}':\n\n"
        result += f"Total: {total_gb:.2f} GB\n"
        result += f"Used: {used_gb:.2f} GB ({percent_used:.1f}%)\n"
        result += f"Free: {free_gb:.2f} GB ({100 - percent_used:.1f}%)\n"
        
        return result
    except ImportError:
        return "Error: shutil module not available"
    except Exception as e:
        return f"Error getting disk usage: {e}"


# ==================== Web/API Tools ====================

@server.tool()
async def fetch_url(url: str) -> str:
    """Fetch content from a URL.
    
    Args:
        url: URL to fetch
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    return f"JSON Response from {url}:\n\n{json.dumps(data, indent=2)}"
                except:
                    pass
            
            text = response.text
            if len(text) > 2000:
                text = text[:2000] + "\n\n... (truncated)"
            
            return f"Response from {url}:\n\n{text}"
    except httpx.TimeoutException:
        return f"Error: Request to {url} timed out"
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} for {url}"
    except Exception as e:
        return f"Error fetching URL: {e}"


@server.tool()
async def check_website(url: str) -> str:
    """Check if a website is reachable and get its status.
    
    Args:
        url: Website URL to check
    """
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            start_time = datetime.datetime.now()
            response = await client.get(url)
            end_time = datetime.datetime.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result = f"Website Check for {url}:\n\n"
            result += f"Status: HTTP {response.status_code} ({response.reason_phrase})\n"
            result += f"Response Time: {response_time:.2f} ms\n"
            result += f"Content Type: {response.headers.get('content-type', 'Unknown')}\n"
            result += f"Content Length: {response.headers.get('content-length', 'Unknown')} bytes\n"
            
            return result
    except Exception as e:
        return f"Error checking website: {e}"


# ==================== Data Processing Tools ====================

@server.tool()
async def format_json(json_string: str) -> str:
    """Format and validate a JSON string.
    
    Args:
        json_string: JSON string to format
    """
    try:
        data = json.loads(json_string)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        return f"Formatted JSON:\n\n{formatted}"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"
    except Exception as e:
        return f"Error formatting JSON: {e}"


@server.tool()
async def text_statistics(text: str) -> str:
    """Get statistics about a text.
    
    Args:
        text: Text to analyze
    """
    try:
        lines = text.split('\n')
        words = text.split()
        characters = len(text)
        
        stats = {
            "Characters": characters,
            "Characters (no spaces)": len(text.replace(' ', '')),
            "Words": len(words),
            "Lines": len(lines),
            "Average word length": sum(len(word) for word in words) / len(words) if words else 0,
            "Non-empty lines": len([line for line in lines if line.strip()]),
        }
        
        result = "Text Statistics:\n\n"
        for key, value in stats.items():
            if isinstance(value, float):
                result += f"{key}: {value:.2f}\n"
            else:
                result += f"{key}: {value}\n"
        
        return result
    except Exception as e:
        return f"Error analyzing text: {e}"


@server.tool()
async def text_wrap(text: str, width: int = 80) -> str:
    """Wrap text to a specified width.
    
    Args:
        text: Text to wrap
        width: Maximum line width (default: 80)
    """
    try:
        wrapped = textwrap.fill(text, width=width)
        return f"Text wrapped to {width} characters:\n\n{wrapped}"
    except Exception as e:
        return f"Error wrapping text: {e}"


# ==================== Resources ====================

@server.resource("file://{path}")
async def read_file_resource(path: str) -> str:
    """Read a file as a resource."""
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


@server.resource("system://info")
async def system_info_resource() -> str:
    """Get system information as a resource."""
    return await system_info()


# ==================== Main Server Loop ====================

async def main():
    """Run the MCP server."""
    print(f"Starting MCP server 'my-mcp-server'...", file=sys.stderr)
    print(f"Available tools:", file=sys.stderr)
    
    # List available tools
    tools = [
        "hello", "add_numbers", "calculate",
        "read_file", "write_file", "list_directory", "get_file_info",
        "system_info", "disk_usage",
        "fetch_url", "check_website",
        "format_json", "text_statistics", "text_wrap"
    ]
    
    for tool in tools:
        print(f"  - {tool}", file=sys.stderr)
    
    print(f"\nServer ready. Waiting for connections...", file=sys.stderr)
    
    # Run the server
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())