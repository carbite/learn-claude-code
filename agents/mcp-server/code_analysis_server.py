#!/usr/bin/env python3
"""code_analysis_server.py - MCP server for code analysis tasks"""

import ast
import inspect
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio


# Create server instance
server = Server("code-analysis-server")


# ==================== Code Analysis Tools ====================

@server.tool()
async def analyze_python_file(filepath: str) -> str:
    """Analyze a Python file for structure and metrics.
    
    Args:
        filepath: Path to the Python file to analyze
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File '{filepath}' does not exist"
        
        content = path.read_text()
        
        # Parse the AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return f"Syntax error in file: {e}"
        
        # Collect statistics
        stats = {
            "File": str(path.absolute()),
            "Lines": len(content.split('\n')),
            "Characters": len(content),
            "Functions": 0,
            "Classes": 0,
            "Imports": 0,
            "String literals": 0,
            "Comments": 0,
            "TODO comments": 0,
            "FIXME comments": 0,
        }
        
        # Walk through AST
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                stats["Functions"] += 1
            elif isinstance(node, ast.ClassDef):
                stats["Classes"] += 1
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                stats["Imports"] += 1
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                stats["String literals"] += 1
        
        # Count comments and TODOs
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                stats["Comments"] += 1
                if 'TODO' in line.upper():
                    stats["TODO comments"] += 1
                if 'FIXME' in line.upper():
                    stats["FIXME comments"] += 1
        
        # Format results
        result = f"Python File Analysis: {path.name}\n\n"
        for key, value in stats.items():
            result += f"{key}: {value}\n"
        
        return result
        
    except Exception as e:
        return f"Error analyzing file: {e}"


@server.tool()
async def find_python_functions(filepath: str) -> str:
    """Find all functions in a Python file.
    
    Args:
        filepath: Path to the Python file
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File '{filepath}' does not exist"
        
        content = path.read_text()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return f"Syntax error in file: {e}"
        
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function signature
                args = []
                if node.args.args:
                    args = [arg.arg for arg in node.args.args]
                
                # Get decorators
                decorators = []
                if node.decorator_list:
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name):
                            decorators.append(decorator.id)
                
                functions.append({
                    "name": node.name,
                    "args": args,
                    "decorators": decorators,
                    "lineno": node.lineno,
                    "docstring": ast.get_docstring(node) or "No docstring"
                })
        
        if not functions:
            return f"No functions found in {path.name}"
        
        result = f"Functions in {path.name}:\n\n"
        for i, func in enumerate(functions, 1):
            result += f"{i}. {func['name']}({', '.join(func['args'])})\n"
            if func['decorators']:
                result += f"   Decorators: {', '.join(func['decorators'])}\n"
            result += f"   Line: {func['lineno']}\n"
            result += f"   Docstring: {func['docstring'][:100]}...\n" if len(func['docstring']) > 100 else f"   Docstring: {func['docstring']}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error finding functions: {e}"


@server.tool()
async def check_python_syntax(filepath: str) -> str:
    """Check Python file syntax.
    
    Args:
        filepath: Path to the Python file
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File '{filepath}' does not exist"
        
        # Try to parse with python -m py_compile
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"✅ Syntax check passed for {path.name}"
        else:
            return f"❌ Syntax errors in {path.name}:\n{result.stderr}"
        
    except Exception as e:
        return f"Error checking syntax: {e}"


@server.tool()
async def count_code_lines(directory: str = ".", extensions: str = "py,txt,md,json") -> str:
    """Count lines of code in files with given extensions.
    
    Args:
        directory: Directory to scan (default: current directory)
        extensions: Comma-separated list of file extensions (default: "py,txt,md,json")
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        ext_list = [ext.strip().lower() for ext in extensions.split(',')]
        
        results = {}
        total_lines = 0
        total_files = 0
        
        for ext in ext_list:
            pattern = f"**/*.{ext}"
            files = list(dir_path.glob(pattern))
            
            ext_lines = 0
            for file_path in files:
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            ext_lines += len(lines)
                            total_files += 1
                    except:
                        continue
            
            results[ext] = {
                "files": len(files),
                "lines": ext_lines
            }
            total_lines += ext_lines
        
        # Format results
        result = f"Code Line Count for '{directory}':\n\n"
        result += f"Total files scanned: {total_files}\n"
        result += f"Total lines: {total_lines}\n\n"
        result += "By extension:\n"
        
        for ext, data in results.items():
            result += f"  .{ext}: {data['files']} files, {data['lines']} lines\n"
        
        return result
        
    except Exception as e:
        return f"Error counting lines: {e}"


@server.tool()
async def search_in_files(directory: str, pattern: str, file_extensions: str = "py,txt,md") -> str:
    """Search for text pattern in files.
    
    Args:
        directory: Directory to search in
        pattern: Text pattern to search for (regex supported)
        file_extensions: Comma-separated list of file extensions to search
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        ext_list = [ext.strip().lower() for ext in file_extensions.split(',')]
        
        matches = []
        
        for ext in ext_list:
            pattern_glob = f"**/*.{ext}"
            files = list(dir_path.glob(pattern_glob))
            
            for file_path in files:
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for line_num, line in enumerate(lines, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    matches.append({
                                        "file": str(file_path.relative_to(dir_path)),
                                        "line": line_num,
                                        "text": line.strip()[:100]
                                    })
                    except:
                        continue
        
        if not matches:
            return f"No matches found for pattern '{pattern}' in {directory}"
        
        result = f"Search results for '{pattern}' in {directory}:\n\n"
        result += f"Found {len(matches)} matches\n\n"
        
        for i, match in enumerate(matches[:20], 1):  # Limit to 20 matches
            result += f"{i}. {match['file']}:{match['line']}\n"
            result += f"   {match['text']}\n\n"
        
        if len(matches) > 20:
            result += f"... and {len(matches) - 20} more matches\n"
        
        return result
        
    except Exception as e:
        return f"Error searching files: {e}"


@server.tool()
async def get_file_tree(directory: str = ".", max_depth: int = 3) -> str:
    """Get directory tree structure.
    
    Args:
        directory: Directory to show tree for (default: current directory)
        max_depth: Maximum depth to display (default: 3)
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        result = f"Directory tree for '{directory}' (max depth: {max_depth}):\n\n"
        
        def build_tree(path: Path, prefix: str = "", depth: int = 0):
            nonlocal result
            
            if depth > max_depth:
                return
            
            # Get all items
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            except PermissionError:
                return
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                
                if item.is_dir():
                    result += f"{prefix}{'└── ' if is_last else '├── '}📁 {item.name}/\n"
                    extension = "    " if is_last else "│   "
                    build_tree(item, prefix + extension, depth + 1)
                else:
                    size = item.stat().st_size
                    size_str = f" ({size} bytes)" if size < 1024 else f" ({size/1024:.1f} KB)"
                    result += f"{prefix}{'└── ' if is_last else '├── '}📄 {item.name}{size_str}\n"
        
        result += f"{dir_path.name}/\n"
        build_tree(dir_path, "", 1)
        
        return result
        
    except Exception as e:
        return f"Error getting file tree: {e}"


# ==================== Resources ====================

@server.resource("code://analysis/{filepath}")
async def code_analysis_resource(filepath: str) -> str:
    """Get code analysis as a resource."""
    return await analyze_python_file(filepath)


@server.resource("code://functions/{filepath}")
async def functions_resource(filepath: str) -> str:
    """Get function list as a resource."""
    return await find_python_functions(filepath)


# ==================== Main Server Loop ====================

async def main():
    """Run the MCP server."""
    print(f"Starting Code Analysis MCP server...", file=sys.stderr)
    print(f"Available tools:", file=sys.stderr)
    
    tools = [
        "analyze_python_file",
        "find_python_functions", 
        "check_python_syntax",
        "count_code_lines",
        "search_in_files",
        "get_file_tree"
    ]
    
    for tool in tools:
        print(f"  - {tool}", file=sys.stderr)
    
    print(f"\nServer ready. Waiting for connections...", file=sys.stderr)
    
    # Run the server
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    asyncio.run(main())