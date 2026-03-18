#!/usr/bin/env python3
"""Test script for the MCP server"""

import subprocess
import json
import time

def test_tool_list():
    """Test that the server responds to tools/list request"""
    print("Testing tools/list request...")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    try:
        # Start the server
        proc = subprocess.Popen(
            ["python3", "simple_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        
        # Wait for response
        time.sleep(0.5)
        
        # Read response
        output = proc.stdout.readline()
        
        # Clean up
        proc.terminate()
        proc.wait()
        
        if output:
            response = json.loads(output)
            print(f"✓ Server responded with {len(response.get('result', {}).get('tools', []))} tools")
            
            # List the tools
            tools = response.get('result', {}).get('tools', [])
            for tool in tools:
                print(f"  - {tool.get('name')}: {tool.get('description', 'No description')}")
            
            return True
        else:
            print("✗ No response from server")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_hello_tool():
    """Test calling the hello tool"""
    print("\nTesting hello tool...")
    
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "hello",
            "arguments": {
                "name": "Test User"
            }
        }
    }
    
    try:
        # Start the server
        proc = subprocess.Popen(
            ["python3", "simple_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        
        # Wait for response
        time.sleep(0.5)
        
        # Read response
        output = proc.stdout.readline()
        
        # Clean up
        proc.terminate()
        proc.wait()
        
        if output:
            response = json.loads(output)
            result = response.get('result', {}).get('content', [{}])[0].get('text', '')
            print(f"✓ Tool response: {result}")
            return True
        else:
            print("✗ No response from tool")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("MCP Server Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 2
    
    if test_tool_list():
        tests_passed += 1
    
    if test_hello_tool():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{tests_total} tests passed")
    print("=" * 50)
    
    if tests_passed == tests_total:
        print("✅ All tests passed! Server is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check server implementation.")
        return 1

if __name__ == "__main__":
    exit(main())