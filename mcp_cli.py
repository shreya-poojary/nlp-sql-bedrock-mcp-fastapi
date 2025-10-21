#!/usr/bin/env python3
"""
Simple Command Line Interface for MySQL NLP MCP Server
Usage: python mcp_cli.py <command> [arguments]
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import handle_call_tool, handle_list_tools

async def execute_command(command, *args):
    """Execute a single MCP command"""
    try:
        if command == "list":
            tools = await handle_list_tools()
            print("Available MCP Tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            return True
            
        elif command == "schema":
            result = await handle_call_tool("get_schema", {})
            print("Database Schema:")
            try:
                schema_data = json.loads(result[0].text)
                for table_name, table_info in schema_data.items():
                    print(f"\nTable: {table_name}")
                    print(f"  Columns: {len(table_info.get('columns', []))}")
                    if table_info.get('sample_data'):
                        print(f"  Sample rows: {len(table_info['sample_data'])}")
            except:
                print(result[0].text)
            return True
            
        elif command == "sql":
            if not args:
                print("Error: Please provide a SQL query")
                return False
            sql_query = " ".join(args)
            result = await handle_call_tool("execute_sql", {"sql": sql_query})
            print("SQL Result:")
            try:
                result_data = json.loads(result[0].text)
                if 'rows' in result_data:
                    print(f"Rows returned: {result_data.get('row_count', 0)}")
                    if result_data.get('rows'):
                        for row in result_data['rows']:
                            print(f"  {row}")
                else:
                    print(result_data)
            except:
                print(result[0].text)
            return True
            
        elif command == "ask":
            if not args:
                print("Error: Please provide a question")
                return False
            question = " ".join(args)
            result = await handle_call_tool("query_database", {"question": question})
            print("Query Result:")
            try:
                result_data = json.loads(result[0].text)
                if 'generated_sql' in result_data:
                    print(f"Generated SQL: {result_data['generated_sql']}")
                    if 'result' in result_data:
                        db_result = result_data['result']
                        if 'rows' in db_result:
                            print(f"Rows returned: {db_result.get('row_count', 0)}")
                            if db_result.get('rows'):
                                for row in db_result['rows']:
                                    print(f"  {row}")
                else:
                    print(result_data)
            except:
                print(result[0].text)
            return True
            
        elif command == "generate":
            if not args:
                print("Error: Please provide a question")
                return False
            question = " ".join(args)
            result = await handle_call_tool("generate_sql", {"question": question})
            print("Generated SQL:")
            print(result[0].text.replace("Generated SQL: ", ""))
            return True
            
        else:
            print(f"Unknown command: {command}")
            print("Available commands: list, schema, sql, ask, generate")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def show_usage():
    """Show usage information"""
    print("MySQL NLP MCP CLI")
    print("="*40)
    print("Usage: python mcp_cli.py <command> [arguments]")
    print()
    print("Commands:")
    print("  list                    - List available MCP tools")
    print("  schema                  - Get database schema")
    print("  sql <query>             - Execute SQL query")
    print("  ask <question>          - Ask natural language question")
    print("  generate <question>     - Generate SQL without executing")
    print()
    print("Examples:")
    print("  python mcp_cli.py list")
    print("  python mcp_cli.py schema")
    print("  python mcp_cli.py sql 'SELECT * FROM Courses LIMIT 5'")
    print("  python mcp_cli.py ask 'Show me all courses'")
    print("  python mcp_cli.py generate 'Find students from California'")
    print()
    print("Interactive mode:")
    print("  python terminal_mcp_client.py")

async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: No .env file found.")
        print("   Some features may not work without proper configuration.")
        print()
    
    success = await execute_command(command, *args)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
