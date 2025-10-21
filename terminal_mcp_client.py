#!/usr/bin/env python3
"""
Terminal-based MCP Client for MySQL NLP Server
This allows you to interact with the MCP server directly from the terminal
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import handle_call_tool, handle_list_tools

class TerminalMCPClient:
    def __init__(self):
        self.running = True
        
    async def list_tools(self):
        """List all available MCP tools"""
        try:
            tools = await handle_list_tools()
            print("\n" + "="*60)
            print("AVAILABLE MCP TOOLS")
            print("="*60)
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.name}")
                print(f"   Description: {tool.description}")
                print(f"   Required: {list(tool.inputSchema.get('required', []))}")
                print()
            return tools
        except Exception as e:
            print(f"[ERROR] Failed to list tools: {e}")
            return []
    
    async def execute_tool(self, tool_name, arguments):
        """Execute an MCP tool with given arguments"""
        try:
            result = await handle_call_tool(tool_name, arguments)
            return result[0].text if result else "No result"
        except Exception as e:
            return f"Error: {e}"
    
    async def interactive_mode(self):
        """Interactive terminal interface"""
        print("MySQL NLP MCP Server - Terminal Interface")
        print("="*50)
        print("Type 'help' for commands, 'quit' to exit")
        print()
        
        # Load available tools
        tools = await self.list_tools()
        tool_names = [tool.name for tool in tools]
        
        while self.running:
            try:
                # Get user input
                user_input = input("\nMCP> ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                    
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                    
                elif user_input.lower() == 'tools':
                    await self.list_tools()
                    print("\n" + "="*60)
                    print("TERMINAL COMMANDS (Use these instead!)")
                    print("="*60)
                    print("ask <question>     - Natural language to SQL + execute")
                    print("sql <query>       - Direct SQL execution")
                    print("generate <question> - Natural language to SQL only")
                    print("schema            - Get database schema")
                    print("="*60)
                    continue
                    
                elif user_input.lower() == 'schema':
                    print("Getting database schema...")
                    result = await self.execute_tool("get_schema", {})
                    print("\nDatabase Schema:")
                    print("-" * 40)
                    try:
                        schema_data = json.loads(result)
                        for table_name, table_info in schema_data.items():
                            print(f"\nTable: {table_name}")
                            print(f"Columns: {len(table_info.get('columns', []))}")
                            if table_info.get('sample_data'):
                                print(f"Sample rows: {len(table_info['sample_data'])}")
                    except:
                        print(result)
                    continue
                    
                elif user_input.lower().startswith('sql '):
                    sql_query = user_input[4:].strip()
                    if not sql_query:
                        print("Please provide a SQL query after 'sql '")
                        continue
                    print(f"Executing SQL: {sql_query}")
                    result = await self.execute_tool("execute_sql", {"sql": sql_query})
                    print("\nResult:")
                    print("-" * 40)
                    try:
                        result_data = json.loads(result)
                        if 'rows' in result_data:
                            print(f"Rows returned: {result_data.get('row_count', 0)}")
                            if result_data.get('rows'):
                                print("Data:")
                                for row in result_data['rows'][:10]:  # Show first 10 rows
                                    print(f"  {row}")
                                if len(result_data['rows']) > 10:
                                    print(f"  ... and {len(result_data['rows']) - 10} more rows")
                        else:
                            print(result)
                    except:
                        print(result)
                    continue
                    
                elif user_input.lower().startswith('ask '):
                    question = user_input[4:].strip()
                    if not question:
                        print("Please provide a question after 'ask '")
                        continue
                    print(f"Processing question: {question}")
                    result = await self.execute_tool("query_database", {"question": question})
                    print("\nResult:")
                    print("-" * 40)
                    try:
                        result_data = json.loads(result)
                        if 'generated_sql' in result_data:
                            print(f"Generated SQL: {result_data['generated_sql']}")
                            print(f"Question: {result_data['question']}")
                            if 'result' in result_data:
                                db_result = result_data['result']
                                if 'rows' in db_result:
                                    print(f"Rows returned: {db_result.get('row_count', 0)}")
                                    if db_result.get('rows'):
                                        print("Data:")
                                        for row in db_result['rows'][:10]:  # Show first 10 rows
                                            print(f"  {row}")
                                        if len(db_result['rows']) > 10:
                                            print(f"  ... and {len(db_result['rows']) - 10} more rows")
                        else:
                            print(result)
                    except:
                        print(result)
                    continue
                    
                elif user_input.lower().startswith('generate '):
                    question = user_input[9:].strip()
                    if not question:
                        print("Please provide a question after 'generate '")
                        continue
                    print(f"Generating SQL for: {question}")
                    result = await self.execute_tool("generate_sql", {"question": question})
                    print("\nGenerated SQL:")
                    print("-" * 40)
                    print(result.replace("Generated SQL: ", ""))
                    continue
                    
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Show help information"""
        print("\n" + "="*60)
        print("MCP TERMINAL CLIENT - COMMANDS")
        print("="*60)
        print("help          - Show this help message")
        print("tools         - List all available MCP tools")
        print("schema        - Get database schema information")
        print("sql <query>   - Execute a raw SQL query")
        print("ask <question> - Ask a natural language question")
        print("generate <question> - Generate SQL without executing")
        print("quit/exit/q   - Exit the client")
        print()
        print("IMPORTANT: Use these commands, NOT the MCP tool names!")
        print("[CORRECT] Use: ask, sql, generate, schema")
        print("[WRONG] Don't use: query_database, execute_sql, generate_sql")
        print()
        print("Examples:")
        print("  sql SELECT * FROM Courses LIMIT 5")
        print("  ask Show me all courses")
        print("  generate Find all students from California")
        print("="*60)

async def main():
    """Main entry point"""
    print("Starting MySQL NLP MCP Terminal Client...")
    print("Make sure your .env file is configured with database and AWS credentials.")
    print()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: No .env file found.")
        print("   Create a .env file with your database and AWS credentials.")
        print("   The client will still start but some features may not work.")
        print()
    
    client = TerminalMCPClient()
    await client.interactive_mode()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error starting terminal client: {e}")
        sys.exit(1)
