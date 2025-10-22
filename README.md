# MySQL NLP MCP Server

A comprehensive Natural Language Processing server for MySQL databases using AWS Bedrock and FastAPI, with full MCP (Model Context Protocol) support.

## Features

- **Natural Language to SQL**: Convert natural language questions into SQL queries using AWS Bedrock Converse API with Amazon Nova Pro or Claude 3.5 Sonnet
- **MCP Protocol Support**: Full Model Context Protocol implementation for AI tool integration
- **FastAPI REST API**: Traditional REST API endpoints for direct integration
- **Terminal Interface**: Interactive and command-line interfaces for direct terminal usage
- **Security**: Read-only SQL execution with input validation and SQL injection protection
- **Schema Awareness**: Automatic database schema detection for better SQL generation
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
                    │   AWS Bedrock Converse    │
                    │ (Nova Pro / Claude 3.5)   │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     MySQL RDS            │
                    └───────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- MySQL database (local or AWS RDS)
- AWS account with Bedrock access
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mysql-nlp-mcp-server.git
   cd mysql-nlp-mcp-server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your credentials:
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
   ```bash
   aws configure
   # OR set environment variables:
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

5. **Test the setup**:
   ```bash
   python test_mcp_server.py
   ```

## Usage

### Option 1: Terminal Interface (Recommended for Direct Use)

#### Interactive Terminal Client
```bash
python terminal_mcp_client.py
```

**Commands:**
- `ask <question>` - Ask natural language questions
- `sql <query>` - Execute raw SQL queries  
- `schema` - Get database schema
- `generate <question>` - Generate SQL without executing
- `help` - Show all commands

#### Command Line Interface
```bash
# Quick commands
python mcp_cli.py ask "Show me all courses"
python mcp_cli.py sql "SELECT * FROM Courses LIMIT 5"
python mcp_cli.py schema
python mcp_cli.py generate "Find students from California"
```

### Option 2: MCP Server (For AI Integration)

```bash
python start_mcp_server.py
```

**MCP Tools Available:**
- `query_database` - Execute natural language queries
- `execute_sql` - Execute raw SQL SELECT queries
- `get_schema` - Get database schema information
- `generate_sql` - Generate SQL from natural language without execution

#### Integrating with Claude Desktop

To use your MCP server with Claude Desktop, follow these steps:

**Step 1: Install Claude Desktop**

Download and install from: https://claude.ai/download

**Step 2: Locate Configuration File**

Find your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Step 3: Add MCP Server Configuration**

Edit `claude_desktop_config.json` and add your server:

```json
{
  "mcpServers": {
    "mysql-nlp": {
      "command": "python",
      "args": [
        "C:/Users/YOUR_USERNAME/path/to/mcp-mysql/mcp_server.py"
      ],
      "env": {
        "DB_HOST": "your-database-host",
        "DB_PORT": "3306",
        "DB_NAME": "your-database-name",
        "DB_USER": "your-username",
        "DB_PASSWORD": "your-password",
        "AWS_REGION": "us-east-1",
        "BEDROCK_MODEL_ID": "amazon.nova-pro-v1:0"
      }
    }
  }
}
```

**Important Notes:**
- Use **absolute path** to your `mcp_server.py` file
- Use forward slashes (`/`) even on Windows
- Replace placeholder values with your actual credentials
- Alternatively, use `"cwd"` parameter to load from `.env` file:

```json
{
  "mcpServers": {
    "mysql-nlp": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:/Users/YOUR_USERNAME/path/to/mcp-mysql"
    }
  }
}
```

**Step 4: Restart Claude Desktop**

Completely quit and restart Claude Desktop for changes to take effect.

**Step 5: Use the Tools**

In Claude Desktop:
1. Look for the 🔨 (hammer) icon to see available tools
2. Ask Claude to use your database tools:
   - "Use query_database to show me all professors"
   - "Get the database schema using get_schema"
   - "Generate SQL to find all courses with more than 50 students"

**Example Conversation:**
```
You: Use the query_database tool to show me all professors

Claude: I'll query the database for all professors.
[Calls query_database tool]

Here are all the professors in your database:
1. Dr. John Doe - john.doe@university.edu (Hired: 2020-01-10)
2. Dr. Jane Williams - jane.williams@university.edu (Hired: 2019-09-05)
```

**Troubleshooting:**
- If tools don't appear, check the Developer Console in Claude Desktop
- Ensure Python is in your system PATH
- Verify all credentials are correct
- Check that the MCP server runs independently: `python start_mcp_server.py`

### Option 3: FastAPI Server (REST API)

```bash
python start_fastapi_server.py
```

**Access:** `http://localhost:8000/docs`

**API Endpoints:**
- `GET /` - API information
- `GET /test-db` - Test database connection
- `GET /schema` - Get database schema
- `POST /query` - Process natural language query
- `POST /sql` - Execute raw SQL query
- `POST /generate-sql` - Generate SQL from natural language

**Example Usage:**
```bash
# Natural language query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all users from California"}'

# Raw SQL query
curl -X POST "http://localhost:8000/sql" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users WHERE state = \"CA\""}'
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

## Project Structure

```
mysql-nlp-mcp-server/
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

## Development

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

## Testing

### Test Your Setup
```bash
# Test MCP server functionality
python test_mcp_server.py

# Test database connection
python test_rds_connection.py

# Test simple SQL query
python test_simple.py
```

### Example Queries

**Natural Language:**
```bash
# Interactive mode
python terminal_mcp_client.py
MCP> ask Show me all courses with more than 50 students

# Command line
python mcp_cli.py ask "Find all students from California"
```

**SQL Queries:**
```bash
# Interactive mode
MCP> sql SELECT * FROM Courses LIMIT 10

# Command line  
python mcp_cli.py sql "SELECT COUNT(*) FROM Students"
```


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

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test them
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/mysql-nlp-mcp-server.git
cd mysql-nlp-mcp-server

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_mcp_server.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

**Need help?**
1. 📖 Check the troubleshooting section above
2. 🔍 Review the API documentation at `/docs`
3. 🐛 Create an issue in the repository
4. 💬 Start a discussion for questions

**Found a bug?**
- Please create an issue with:
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (OS, Python version, etc.)

## Star This Repository

If this project helped you, please give it a star!
