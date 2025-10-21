# app/shared_utils.py
"""
Shared utilities for MySQL NLP operations
"""

import json
import boto3
import mysql.connector
from mysql.connector import Error
from botocore.exceptions import ClientError
from typing import Dict, Any
from datetime import date, datetime, time
import decimal
from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, AWS_REGION, BEDROCK_MODEL_ID

def serialize_mysql_data(data):
    """Convert MySQL data types to JSON-serializable formats"""
    if isinstance(data, dict):
        return {key: serialize_mysql_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_mysql_data(item) for item in data]
    elif isinstance(data, (date, datetime)):
        return data.isoformat()
    elif isinstance(data, time):
        return data.isoformat()
    elif isinstance(data, decimal.Decimal):
        return float(data)
    elif isinstance(data, bytes):
        return data.decode('utf-8')
    else:
        return data

def get_db_connection():
    """Get MySQL database connection"""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            autocommit=True
        )
    except Error as e:
        raise Exception(f"Database connection error: {str(e)}")

def execute_sql_query(sql_query: str) -> Dict[str, Any]:
    """Execute SQL query and return results"""
    # Security check - only allow SELECT queries
    sql_upper = sql_query.upper().strip()
    if not sql_upper.startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed for security")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Serialize the data to handle MySQL data types
        serialized_rows = serialize_mysql_data(rows)
        
        return {
            "columns": columns,
            "rows": serialized_rows,
            "row_count": len(serialized_rows)
        }
    finally:
        cursor.close()
        conn.close()

def get_database_schema() -> Dict[str, Any]:
    """Get database schema information"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            # Get table structure
            cursor.execute(f"DESCRIBE `{table}`")
            columns = cursor.fetchall()
            
            # Get sample data (first 3 rows)
            cursor.execute(f"SELECT * FROM `{table}` LIMIT 3")
            sample_data = cursor.fetchall()
            
            schema[table] = {
                "columns": serialize_mysql_data(columns),
                "sample_data": serialize_mysql_data(sample_data)
            }
        
        return schema
    finally:
        cursor.close()
        conn.close()

def generate_sql_from_nl(question: str, schema_info: str = None) -> str:
    """Generate SQL query from natural language using AWS Bedrock"""
    try:
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=AWS_REGION
        )
        
        # Prepare the prompt
        prompt = f"""You are an expert SQL query generator for MySQL databases.

Question: {question}

Database Schema:
{schema_info if schema_info else "No schema information provided"}

Instructions:
1. Generate a valid MySQL SELECT query only
2. Use proper table and column names from the schema
3. Include appropriate WHERE clauses, JOINs, and aggregations as needed
4. Return ONLY the SQL query, no explanations or markdown formatting
5. Ensure the query is safe and read-only

SQL Query:"""

        # Use Converse API for Claude models
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0.1
            }
        )

        # Extract SQL from Converse API response
        sql_query = ""
        
        if "output" in response and "message" in response["output"]:
            content = response["output"]["message"].get("content", [])
            if content and len(content) > 0:
                sql_query = content[0].get("text", "").strip()
        
        # Check if we got a valid SQL query
        if not sql_query:
            raise Exception("No SQL query generated from Bedrock response")
        
        # Clean up the SQL query (remove markdown formatting if present)
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        
        # Final validation - ensure we have a non-empty SQL query
        if not sql_query:
            raise Exception("Generated SQL query is empty")
        
        return sql_query

    except ClientError as e:
        raise Exception(f"AWS Bedrock error: {e}")
    except Exception as e:
        raise Exception(f"Failed to generate SQL query: {e}")
