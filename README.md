# data-analyst-mcp-app

A local agent platform for data analysis, powered by FastMCP and LLMs (Ollama, GPT-OSS).  
Provides tools for working with CSV and text files, and enables autonomous agent workflows via HTTP API and Streamlit UI.

## MCP Server-Client Setup

- **MCP Server:**  
  The main server file is [`server/fastmcp_server.py`](server/fastmcp_server.py).  
  Start this to expose data tools via FastMCP.

- **MCP Client:**  
  The main client file is [`app/ollama_mcp_client.py`](app/ollama_mcp_client.py).  
  Use this to interact with the MCP server and LLM agent.  
  Other files in `app/` and `server/tools/` are ancillary and not required for the core MCP setup.

## Features

- **FastMCP server**: Exposes tools for CSV/text file manipulation.
- **LLM integration**: Use Ollama or OpenAI-compatible models for agent workflows.
- **Tooling**: Read, append, edit text files; read, add rows, and compute insights on CSV files.

## Setup

1. **Python version**: Requires Python 3.12 (see `.python-version`).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Also install packages from `pyproject.toml` if needed:
   ```bash
   pip install rich
   ```
3. **Start MCP server**:
   ```bash
   python server/fastmcp_server.py
   ```
   MCP server runs at `http://127.0.0.1:8090`.

4. **Ollama setup** (for LLM agent features):
   - Install Ollama: https://ollama.com/download
   - Pull a model, e.g.:
     ```bash
     ollama pull llama3
     ollama pull gpt-oss:20b
     ```
   - Ensure Ollama is running locally.

5. **Run MCP Client**:
   ```bash
   python app/ollama_mcp_client.py
   ```

## Usage

- **MCP Tools**:
  - `csv_read(path, columns=None)`: Read CSV file, optionally filter columns.
  - `csv_add_row(path, row)`: Add a row to CSV file.
  - `csv_insight(path, column, operation)`: Compute sum, average, min, max, count for a column.
  - `text_read(path)`: Read entire text file.
  - `text_append(path, text)`: Append a line to text file.
  - `text_edit(path, line_number, new_text)`: Edit a specific line in text file.
  - `ping(name)`: Simple server ping.

- **Agent Workflows**:
  - Use the MCP client (`ollama_mcp_client.py`) to send queries.
  - Autonomous agent converts queries to tool calls using LLM.

## File Structure

- `server/fastmcp_server.py`: MCP server and tool registration.
- `server/tools/`: Tool implementations for CSV/text.
- `app/ollama_mcp_client.py`: Main MCP client and agent.
- `data/`: Example data files (`report.csv`, `notes.txt`).

## Example

- Query: "What is the average sales in data/report.csv?"
- Agent will select `csv_insight` tool and return the result.

## License

MIT

## Author

Abhishek Rai
