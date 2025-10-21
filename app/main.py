from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Dict, Any
from pydantic import BaseModel
from .shared_utils import execute_sql_query, get_database_schema, generate_sql_from_nl

# Pydantic models for request validation
class QueryRequest(BaseModel):
    query: str

class SQLRequest(BaseModel):
    sql: str

class GenerateSQLRequest(BaseModel):
    question: str

app = FastAPI(
    title="MySQL NLP API",
    description="Natural Language Processing API for MySQL databases using AWS Bedrock",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All database and Bedrock operations are now handled by shared_utils


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MySQL NLP API",
        "version": "1.0.0",
        "description": "Natural Language Processing API for MySQL databases using AWS Bedrock",
        "endpoints": {
            "/test-db": "Test database connection",
            "/query": "Process natural language query",
            "/schema": "Get database schema",
            "/sql": "Execute raw SQL query",
            "/generate-sql": "Generate SQL from natural language"
        }
    }

@app.get("/test-db")
async def test_db_connection():
    """Simple endpoint to check DB connectivity."""
    try:
        from .shared_utils import get_db_connection
        conn = get_db_connection()
        conn.close()
        return {"status": "success", "message": "Connected to MySQL database!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/schema")
async def get_schema():
    """Get database schema information"""
    try:
        schema = get_database_schema()
        return {"status": "success", "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting schema: {str(e)}")

@app.post("/query")
async def process_nl_query(request: QueryRequest):
    """
    Accepts a natural language query,
    converts it to SQL via Bedrock,
    executes it on MySQL, and returns results.
    """
    try:
        # Get schema for better SQL generation
        schema = get_database_schema()
        schema_str = json.dumps(schema, indent=2)
        
        # Generate SQL from natural language
        sql_query = generate_sql_from_nl(request.query, schema_str)
        
        # Execute the generated SQL
        result = execute_sql_query(sql_query)
        
        return {
            "status": "success",
            "nl_query": request.query,
            "generated_sql": sql_query,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/sql")
async def execute_sql(request: SQLRequest):
    """
    Execute a raw SQL SELECT query on the database.
    """
    try:
        result = execute_sql_query(request.sql)
        return {
            "status": "success",
            "sql_query": request.sql,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL execution error: {str(e)}")

@app.post("/generate-sql")
async def generate_sql_only(request: GenerateSQLRequest):
    """
    Generate SQL query from natural language without executing it.
    """
    try:
        # Get schema for better SQL generation
        schema = get_database_schema()
        schema_str = json.dumps(schema, indent=2)
        
        # Generate SQL from natural language
        sql_query = generate_sql_from_nl(request.question, schema_str)
        
        return {
            "status": "success",
            "question": request.question,
            "generated_sql": sql_query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")
