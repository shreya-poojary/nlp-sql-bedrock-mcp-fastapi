# MySQL NLP MCP Server

A comprehensive Natural Language Processing server for MySQL databases using AWS Bedrock and FastAPI, with full MCP (Model Context Protocol) support.

## Features

- **Natural Language to SQL**: Convert natural language questions into SQL queries using AWS Bedrock Claude 3.5 Sonnet
- **MCP Protocol Support**: Full Model Context Protocol implementation for AI tool integration
- **FastAPI REST API**: Traditional REST API endpoints for direct integration
- **Security**: Read-only SQL execution with input validation and SQL injection protection
- **Schema Awareness**: Automatic database schema detection for better SQL generation
- **Error Handling**: Comprehensive error handling and logging
- **Shared Architecture**: Clean, maintainable code with shared utilities
- **Production Ready**: Fully tested and optimized for production deployment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │   MCP Client    │    │   REST Client   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    MySQL NLP Server       │
                    │  ┌─────────────────────┐  │
                    │  │   MCP Server        │  │
                    │  │   (mcp_server.py)   │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   FastAPI Server    │  │
                    │  │   (app/main.py)     │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │  Shared Utilities   │  │
                    │  │ (app/shared_utils)  │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      AWS Bedrock          │
                    │   (Claude 3.5 Sonnet)     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     MySQL RDS            │
                    └───────────────────────────┘
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp-mysql
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Copy `.env.example` to `.env` and update with your configuration:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` file:
   ```env
   # Database Configuration
   DB_HOST=your-rds-endpoint.amazonaws.com
   DB_PORT=3306
   DB_NAME=your_database_name
   DB_USER=your_username
   DB_PASSWORD=your_password

   # AWS Configuration
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
   ```

4. **Configure AWS Credentials**:
   Ensure your AWS credentials are configured for Bedrock access:
   ```bash
   aws configure
   ```
   Or set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

## Usage

### Option 1: MCP Server (Recommended for AI Integration)

Run the MCP server for integration with AI tools that support MCP:

```bash
python start_mcp_server.py
```

The MCP server provides these tools:
- `query_database`: Execute natural language queries
- `execute_sql`: Execute raw SQL SELECT queries
- `get_schema`: Get database schema information
- `generate_sql`: Generate SQL from natural language without execution

### Option 1a: Terminal MCP Client (Interactive)

For interactive terminal usage:

```bash
python terminal_mcp_client.py
```

This provides an interactive terminal interface with commands:
- `ask <question>` - Ask natural language questions
- `sql <query>` - Execute raw SQL queries
- `schema` - Get database schema
- `generate <question>` - Generate SQL without executing
- `help` - Show all commands

### Option 1b: Command Line Interface (Quick Commands)

For quick command-line usage:

```bash
# List available tools
python mcp_cli.py list

# Get database schema
python mcp_cli.py schema

# Execute SQL query
python mcp_cli.py sql "SELECT * FROM Courses LIMIT 5"

# Ask natural language question
python mcp_cli.py ask "Show me all courses"

# Generate SQL without executing
python mcp_cli.py generate "Find students from California"
```

### Option 2: FastAPI Server (Traditional REST API)

Run the FastAPI server for traditional REST API access:

```bash
python start_fastapi_server.py
```

Access the API documentation at: `http://localhost:8000/docs`

#### API Endpoints

- `GET /`: API information and available endpoints
- `GET /test-db`: Test database connection
- `GET /schema`: Get database schema
- `POST /query`: Process natural language query
- `POST /sql`: Execute raw SQL query
- `POST /generate-sql`: Generate SQL from natural language

#### Example Usage

**Natural Language Query**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all users from California"}'
```

**Raw SQL Query**:
```bash
curl -X POST "http://localhost:8000/sql" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users WHERE state = \"CA\""}'
```

**Generate SQL Only**:
```bash
curl -X POST "http://localhost:8000/generate-sql" \
  -H "Content-Type: application/json" \
  -d '{"question": "Find all orders from last month"}'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL host address | localhost |
| `DB_PORT` | MySQL port | 3306 |
| `DB_NAME` | Database name | mcpdemo1 |
| `DB_USER` | Database username | root |
| `DB_PASSWORD` | Database password | password |
| `AWS_REGION` | AWS region for Bedrock | us-east-1 |
| `BEDROCK_MODEL_ID` | Bedrock model ID | anthropic.claude-3-5-sonnet-20240620-v1:0 |
| `API_HOST` | FastAPI host | 0.0.0.0 |
| `API_PORT` | FastAPI port | 8000 |
| `API_RELOAD` | Enable auto-reload | true |

### Database Requirements

- MySQL 5.7+ or MySQL 8.0+
- Read access to the target database
- Network connectivity from the server to the database

### AWS Requirements

- AWS account with Bedrock access
- IAM permissions for `bedrock:InvokeModel`
- Proper AWS credentials configured

## Security Features

- **Read-only queries**: Only SELECT statements are allowed
- **SQL injection protection**: Parameterized queries and input validation
- **Schema validation**: Automatic schema detection and validation
- **Error handling**: Comprehensive error handling without exposing sensitive information

## Development

### Project Structure

```
mcp-mysql/
├── app/
│   ├── main.py          # FastAPI server implementation
│   ├── config.py        # Configuration management
│   └── shared_utils.py  # Shared utilities (database + Bedrock)
├── mcp_server.py       # MCP server implementation
├── start_mcp_server.py # MCP server startup script
├── start_fastapi_server.py # FastAPI server startup script
├── terminal_mcp_client.py # Interactive terminal MCP client
├── mcp_cli.py          # Command-line MCP interface
├── test_mcp_server.py  # MCP server testing script
├── test_rds_connection.py # Database connection testing
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

### Adding New Features

1. **For MCP tools**: Add new tool definitions in `mcp_server.py`
2. **For API endpoints**: Add new routes in `app/main.py`
3. **For database operations**: Extend functions in `app/shared_utils.py`
4. **For configuration**: Update `app/config.py` for new settings

### Testing

Test the database connection:
```bash
curl http://localhost:8000/test-db
```

Test natural language query:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the first 5 records from any table"}'
```

## Recent Improvements

### ✅ **Version 2.0 Updates**

- **🔧 Fixed AWS Bedrock Integration**: Updated to correct Claude 3.5 Sonnet API format
- **🏗️ Shared Architecture**: Eliminated code duplication with centralized utilities
- **🛡️ Enhanced Security**: Improved SQL injection protection and input validation
- **⚡ Performance**: Optimized database connections and error handling
- **🧹 Code Cleanup**: Removed redundant files and improved maintainability
- **📚 Better Documentation**: Updated architecture diagrams and usage examples

### **Key Changes:**
- ✅ **Unified Codebase**: Both MCP and FastAPI servers use shared utilities
- ✅ **Fixed Bedrock Requests**: Correct API format for Claude 3.5 Sonnet
- ✅ **Enhanced Error Handling**: Better error messages and debugging
- ✅ **Cleaner Architecture**: Removed duplicate code and files
- ✅ **Production Ready**: Fully tested and optimized

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check database credentials in `.env`
   - Ensure database is accessible from the server
   - Verify MySQL service is running

2. **AWS Bedrock Error**:
   - Verify AWS credentials are configured
   - Check IAM permissions for Bedrock
   - Ensure the model ID is correct
   - **Note**: Make sure you're using the correct Claude 3.5 Sonnet model ID

3. **Import Errors**:
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility
   - Ensure all files are in the correct directory structure

4. **MCP Server Issues**:
   - Verify the MCP server starts without errors: `python mcp_server.py`
   - Check that shared utilities are properly imported
   - Ensure environment variables are configured

### Logs

Both servers provide detailed logging. Check the console output for error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Create an issue in the repository
