import sqlite3
import json
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP("Database MCP Server")

@mcp.tool()
def query_database(sql: str, params: Optional[list] = None) -> str:
    """Execute SQL query."""
    try:
        # Create connection inside function to avoid threading issues
        conn = sqlite3.connect("simple.db")
        cursor = conn.cursor()
        
        # Execute the user's query
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        # Handle different query types
        if sql.upper().strip().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            conn.close()
            return json.dumps({"data": results}, indent=2)
        else:
            # For INSERT, UPDATE, DELETE
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return json.dumps({"affected_rows": affected_rows}, indent=2)
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
