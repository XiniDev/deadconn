import sqlite3
import os
from fastmcp import FastMCP
from src.security import mask_pii

mcp = FastMCP("DeadConn")

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "company_vault.db")
    return sqlite3.connect(db_path)

def is_valid_table(table_name: str) -> bool:
    """Checks if the table name exists in the database to prevent SQL injection."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except:
        return False

def get_allowed_columns(table_name: str) -> list[str]:
    """Retrieves a list of valid column names for a given table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return columns
    except:
        return []


@mcp.tool()
def search_records(table_name: str, search_column: str, search_value: str) -> str:
    """
    Safely retrieves records with dual-layer validation (Table + Column).
    Automatically maps column names to values and applies PII masking.
    """
    if not is_valid_table(table_name):
        return f"Error: Access Denied. '{table_name}' is not a recognized or authorized table."

    allowed_cols = get_allowed_columns(table_name)
    if search_column not in allowed_cols:
        return f"Error: Column '{search_column}' does not exist in '{table_name}'."

    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        query = f"SELECT * FROM {table_name} WHERE {search_column} LIKE ?"
        cursor.execute(query, (f"%{search_value}%",))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            row_dict = dict(result)
            items = [f"{key}: {mask_pii(str(val))}" for key, val in row_dict.items()]
            return " | ".join(items)
        
        return "No record found."
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def list_tables() -> str:
    """Lists all available tables in the legacy vault so the AI knows what to query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return f"Available Tables: {', '.join(tables)}"

@mcp.tool()
def list_columns(table_name: str) -> str:
    """Lists all column names for a specific table so the AI knows what it can search by."""
    if not is_valid_table(table_name):
        return "Error: Invalid table."
    cols = get_allowed_columns(table_name)
    return f"Columns in {table_name}: {', '.join(cols)}"


if __name__ == "__main__":
    mcp.run()
