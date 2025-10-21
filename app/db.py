# app/db.py
import mysql.connector
from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def execute_sql(sql):
    """Execute read-only SQL query and return results"""
    if any(word in sql.lower() for word in ["insert","update","delete","drop","alter","truncate","create"]):
        raise ValueError("Only read-only SELECT queries are allowed")
    
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        return {"columns": columns, "rows": rows}
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_schema():
    """Return schema of all tables"""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SHOW TABLES;")
        tables = [t[0] for t in cur.fetchall()]
        schema = {}
        for t in tables:
            cur.execute(f"DESCRIBE {t};")
            schema[t] = [{"Field": row[0], "Type": row[1]} for row in cur.fetchall()]
        return schema
    except Exception as e:
        raise Exception(f"Schema retrieval error: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
