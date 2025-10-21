#!/usr/bin/env python3
"""
MCP Server for NLP to SQL conversion using AWS Bedrock and MySQL RDS
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import os
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Import shared utilities
from app.shared_utils import execute_sql_query, get_database_schema, generate_sql_from_nl

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mysql-nlp-mcp")

# Initialize MCP server
server = Server("mysql-nlp-mcp")

# Create a simple notification options object
class SimpleNotificationOptions:
    def __init__(self):
        self.tools_changed = False

# All database and Bedrock operations are now handled by shared_utils

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="query_database",
            description="Execute a natural language query on the MySQL database using AWS Bedrock to convert to SQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about the database"
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="execute_sql",
            description="Execute a raw SQL SELECT query on the MySQL database",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    }
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="get_schema",
            description="Get the database schema including tables, columns, and sample data",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="generate_sql",
            description="Generate SQL query from natural language without executing it",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question to convert to SQL"
                    }
                },
                "required": ["question"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls"""
    try:
        if name == "query_database":
            question = arguments.get("question")
            if not question:
                return [TextContent(type="text", text="Error: Question is required")]
            
            # Get schema for better SQL generation
            schema = get_database_schema()
            schema_str = json.dumps(schema, indent=2)
            
            # Generate SQL from natural language
            sql_query = generate_sql_from_nl(question, schema_str)
            
            # Execute the generated SQL
            result = execute_sql_query(sql_query)
            
            response = {
                "question": question,
                "generated_sql": sql_query,
                "result": result
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "execute_sql":
            sql = arguments.get("sql")
            if not sql:
                return [TextContent(type="text", text="Error: SQL query is required")]
            
            result = execute_sql_query(sql)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_schema":
            schema = get_database_schema()
            return [TextContent(type="text", text=json.dumps(schema, indent=2))]
        
        elif name == "generate_sql":
            question = arguments.get("question")
            if not question:
                return [TextContent(type="text", text="Error: Question is required")]
            
            # Get schema for better SQL generation
            schema = get_database_schema()
            schema_str = json.dumps(schema, indent=2)
            
            # Generate SQL from natural language
            sql_query = generate_sql_from_nl(question, schema_str)
            
            return [TextContent(type="text", text=f"Generated SQL: {sql_query}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mysql-nlp-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=SimpleNotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
