from fastmcp import FastMCP

# --- Import your actual tool functions ---
# These functions are expected to be in a 'tools' folder
# with files 'csv_tools.py' and 'text_tools.py'.
from tools.csv_tools import read_csv, add_row, compute_insight
from tools.text_tools import read_text, append_text, edit_text


# --- MCP Server Definition ---

# Create a new FastMCP server instance
mcp = FastMCP("LocalDataAgent")

# Define tools by wrapping your functions with the @mcp.tool() decorator
#introduce the tools to the MCP server
@mcp.tool()
def ping(name: str )-> str:
    """A simple ping tool to check server responsiveness."""
    return f"pong,{name}!"

# CSV Tools
@mcp.tool()
def csv_read(path: str, columns=None):
    """Reads data from a CSV file."""
    # This now calls your imported read_csv function
    return read_csv(path, columns)

@mcp.tool()
def csv_add_row(path: str, row: dict):
    """Adds a new row to a CSV file."""
    # This now calls your imported add_row function
    return add_row(path, row)

@mcp.tool()
def csv_insight(path: str, column: str, operation: str):
    """Computes an insight on a CSV column (e.g., sum, average)."""
    # This tool orchestrates calls to your other imported functions
    rows_data = read_csv(path)
    # It's good practice to check for errors from the first tool call
    if rows_data.get("error"):
        return rows_data
    
    # Assuming your read_csv returns a dictionary like {"data": [...]}
    rows = rows_data.get("data", [])
    return compute_insight(rows, column, operation)

# Text Tools
@mcp.tool()
def text_read(path: str):
    """Reads the entire content of a text file."""
    # This now calls your imported read_text function
    return read_text(path)

@mcp.tool()
def text_append(path: str, text: str):
    """Appends text to the end of a file."""
    # This now calls your imported append_text function
    return append_text(path, text)

@mcp.tool()
def text_edit(path: str, line_number: int, new_text: str):
    """Replaces the content of a specific line in a text file."""
    # This now calls your imported edit_text function
    return edit_text(path, line_number, new_text)


# Entry point to run the server
if __name__ == "__main__":
    print("Starting LocalDataAgent MCP server on http://127.0.0.1:8090")
    print("Press CTRL+C to stop.")
    # The run() method starts the server. Using the http transport makes it accessible via HTTP requests.
    mcp.run(transport="http", host="127.0.0.1", port=8090)
