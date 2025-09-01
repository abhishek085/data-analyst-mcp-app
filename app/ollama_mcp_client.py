# ollama_mcp_client.py

import asyncio
import json
from fastmcp import Client as MCPClient
from ollama import Client as OllamaClient
from ollama._types import ChatResponse

# === MCP connection ===
MCP_URL = "http://127.0.0.1:8090/mcp"

mcp_client = MCPClient(MCP_URL)
ollama_client = OllamaClient()

# === Friendly file mapping ===
FILE_MAPPING = {
    "notes file": "/Users/abhishekrai/code/data-analyst-mcp-app/data/notes.txt",
    "report file": "/Users/abhishekrai/code/data-analyst-mcp-app/data/report.csv",
}

def normalize_tool_args(args):
    """
    Normalize tool arguments:
    - Map friendly file names to actual paths.
    - Parse JSON strings if needed.
    - Ensure 'path' is present for tools that require it.
    """
    # If args is not a dict, wrap it
    if not isinstance(args, dict):
        args = {"path": str(args)}
    # If path is a JSON string, parse it
    if "path" in args and isinstance(args["path"], str):
        try:
            maybe_dict = json.loads(args["path"])
            if isinstance(maybe_dict, dict) and "file_path" in maybe_dict:
                args["path"] = maybe_dict["file_path"]
        except Exception:
            pass
    # Map friendly file names
    for k, v in args.items():
        if isinstance(v, str) and v.lower() in FILE_MAPPING:
            args[k] = FILE_MAPPING[v.lower()]
    # Ensure 'path' is present and not empty for tools that require it
    if "path" not in args or not args["path"]:
        raise ValueError("Tool call missing required 'path' argument after normalization.")
    return args

async def wrap_mcp_tool(tool_spec):
    """
    Wrap an MCP tool spec into a callable function
    that gpt-oss can invoke.
    """
    async def _call(**kwargs):
        async with mcp_client:
            # ensure connected
            await mcp_client.ping()
            # Normalize arguments
            kwargs = normalize_tool_args(kwargs)
            result = await mcp_client.call_tool(tool_spec.name, kwargs)
            return str(result)

    _call.__name__ = tool_spec.name
    _call.__doc__ = tool_spec.description or "MCP tool"
    return _call


async def load_tools_from_mcp():
    """Fetch all available tools from MCP and wrap them for Ollama's gpt-oss."""
    async with mcp_client:
        await mcp_client.ping()
        tools = await mcp_client.list_tools()

    wrapped = []
    for t in tools:
        wrapped.append(await wrap_mcp_tool(t))
    return wrapped


async def main(user_query):
    # Load MCP tools
    tools = await load_tools_from_mcp()
    print("> Tools loaded from MCP:", [t.__name__ for t in tools])

    # Start conversation with Ollama
    messages = [
        {
            "role": "system",
            "content": (
                "You have access to MCP tools such as text_read, csv_read, etc. "
                "When the user asks about files like 'notes file' or 'report file', "
                "use the friendly name (e.g., 'notes file') as the path argument. "
                "Do not use raw file paths; the system will map friendly names to actual paths. "
                "Do not ask the user for file paths."
            ),
        },
        {"role": "user", "content": user_query},
    ]
    model = "gpt-oss:20b"

    while True:
        response: ChatResponse = ollama_client.chat(
            model=model,
            messages=messages,
            tools=tools,  # pass in MCP-backed tools
        )

        # If the model produced text output
        if response.message.content:
            print("\nAssistant:", response.message.content, "\n")

        # Add to conversation
        messages.append(response.message)

        # Handle tool calls
        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                fn = next((f for f in tools if f.__name__ == tool_call.function.name), None)
                if fn:
                    try:
                        args = normalize_tool_args(tool_call.function.arguments)
                    except Exception as e:
                        print(f"→ Tool call argument error: {e}")
                        messages.append({
                            "role": "tool",
                            "tool_name": tool_call.function.name,
                            "content": f"Error: {e}",
                        })
                        continue
                    print(f"→ Calling tool: {tool_call.function.name} with {args}")
                    result = await fn(**args)
                    print(f"← Tool result: {result}\n")

                    messages.append({
                        "role": "tool",
                        "tool_name": tool_call.function.name,
                        "content": result,
                    })
        else:
            break  # no more tool calls → stop


if __name__ == "__main__":
    user_query = "Summarize the data/report.csv file."
    asyncio.run(main(user_query))
