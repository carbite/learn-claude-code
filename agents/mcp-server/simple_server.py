#!/usr/bin/env python3
"""simple_server.py - A minimal MCP server for testing"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio

# Create server instance
server = Server("simple-server")

# Define a simple tool
@server.tool()
async def hello(name: str = "World") -> str:
    """Say hello to someone.
    
    Args:
        name: The name to greet (default: "World")
    """
    return f"Hello, {name}! 👋"

@server.tool()
async def add(a: float, b: float) -> str:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
    """
    return f"{a} + {b} = {a + b}"

@server.tool()
async def multiply(a: float, b: float) -> str:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
    """
    return f"{a} × {b} = {a * b}"

# Run server
async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())