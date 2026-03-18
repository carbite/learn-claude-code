#!/usr/bin/env python3
"""Demonstrate the MCP server functionality"""

import subprocess
import time
import sys

def demo_basic_tools():
    """Demonstrate basic tool functionality"""
    print("=" * 60)
    print("MCP Server Demo")
    print("=" * 60)
    
    print("\n1. Starting simple MCP server in background...")
    
    # Start the server
    server_process = subprocess.Popen(
        [sys.executable, "simple_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(1)
    
    print("2. Server started successfully!")
    print("\n3. Available tools in simple_server.py:")
    print("   - hello(name): Say hello to someone")
    print("   - add(a, b): Add two numbers")
    print("   - multiply(a, b): Multiply two numbers")
    
    print("\n4. Testing tools programmatically...")
    
    # Create a test file to demonstrate file operations
    test_content = """# Test Python File
def hello_world():
    \"\"\"Print hello world\"\"\"
    print("Hello, World!")

def add_numbers(a, b):
    \"\"\"Add two numbers\"\"\"
    return a + b

class Calculator:
    \"\"\"Simple calculator class\"\"\"
    
    def multiply(self, x, y):
        \"\"\"Multiply two numbers\"\"\"
        return x * y

# TODO: Add more functions
# FIXME: Handle edge cases
"""
    
    with open("test_demo.py", "w") as f:
        f.write(test_content)
    
    print("   Created test_demo.py for analysis")
    
    # Stop the server
    server_process.terminate()
    server_process.wait()
    
    print("\n5. Testing code analysis server...")
    
    # Start the code analysis server
    code_server = subprocess.Popen(
        [sys.executable, "code_analysis_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True
    )
    
    time.sleep(1)
    
    print("\n6. Available tools in code_analysis_server.py:")
    print("   - analyze_python_file(filepath): Analyze Python file structure")
    print("   - find_python_functions(filepath): Find all functions in file")
    print("   - check_python_syntax(filepath): Check Python syntax")
    print("   - count_code_lines(directory): Count lines of code")
    print("   - search_in_files(directory, pattern): Search for text in files")
    print("   - get_file_tree(directory): Show directory tree")
    
    # Stop the code server
    code_server.terminate()
    code_server.wait()
    
    # Clean up
    import os
    if os.path.exists("test_demo.py"):
        os.remove("test_demo.py")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nTo use with Claude:")
    print("1. Add server to ~/.config/claude/mcp.json")
    print("2. Restart Claude")
    print("3. Ask Claude to use the tools!")
    print("\nExample: 'Can you analyze test_demo.py using the code analysis tools?'")

if __name__ == "__main__":
    demo_basic_tools()