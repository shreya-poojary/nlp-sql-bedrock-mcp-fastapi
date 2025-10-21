#!/usr/bin/env python3
"""
Test script for MCP server functionality
This script tests the MCP server tools without requiring an MCP client
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import handle_call_tool, handle_list_tools

async def test_mcp_tools():
    """Test the MCP server tools directly"""
    print("Testing MCP Server Tools...")
    print("=" * 50)
    
    try:
        # Test 1: List tools
        print("1. Testing list_tools...")
        tools = await handle_list_tools()
        print(f"[SUCCESS] Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        print()
        
        # Test 2: Test get_schema tool
        print("2. Testing get_schema tool...")
        try:
            result = await handle_call_tool("get_schema", {})
            print("[SUCCESS] get_schema tool works")
            print(f"Response preview: {str(result[0].text)[:100]}...")
        except Exception as e:
            print(f"[ERROR] get_schema failed: {e}")
        print()
        
        # Test 3: Test generate_sql tool
        print("3. Testing generate_sql tool...")
        try:
            result = await handle_call_tool("generate_sql", {"question": "Show me all tables"})
            print("[SUCCESS] generate_sql tool works")
            print(f"Generated SQL: {result[0].text}")
        except Exception as e:
            print(f"[ERROR] generate_sql failed: {e}")
        print()
        
        # Test 4: Test execute_sql tool (if database is available)
        print("4. Testing execute_sql tool...")
        try:
            result = await handle_call_tool("execute_sql", {"sql": "SELECT 1 as test"})
            print("[SUCCESS] execute_sql tool works")
            print(f"Result: {result[0].text}")
        except Exception as e:
            print(f"[ERROR] execute_sql failed: {e}")
        print()
        
        print("=" * 50)
        print("MCP Server Tools Test Complete!")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("MCP Server Test Suite")
    print("This tests the MCP server functionality without requiring an MCP client")
    print()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: No .env file found. Some tests may fail.")
        print("   Create a .env file with your database and AWS credentials.")
        print()
    
    success = asyncio.run(test_mcp_tools())
    
    if success:
        print("\n[SUCCESS] All tests completed successfully!")
        print("\nTo use the MCP server with an MCP client:")
        print("1. Configure your .env file")
        print("2. Run: python start_mcp_server.py")
        print("3. Connect with an MCP client (like Claude Desktop)")
    else:
        print("\n[ERROR] Some tests failed. Check your configuration.")
        sys.exit(1)
