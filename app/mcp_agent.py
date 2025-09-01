import asyncio
from fastmcp import Client
import json
import ollama

import os

client = Client("http://127.0.0.1:8090/mcp")

# MCP server URL is configurable via env var or argument
def get_mcp_base_url():
    return os.environ.get("MCP_BASE_URL", "http://127.0.0.1:8090")

async def list_mcp_tools(base_url=None):
    async with client:
        tools = await client.list_tools()
        # tools -> list[mcp.types.Tool]
        tools_list = []
        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"Description: {tool.description}")
            if tool.inputSchema:
                print(f"Parameters: {tool.inputSchema}")
            # Access tags and other metadata
            if hasattr(tool, 'meta') and tool.meta:
                fastmcp_meta = tool.meta.get('_fastmcp', {})
                print(f"Tags: {fastmcp_meta.get('tags', [])}")
            # For prompt formatting
            tools_list.append({
                "name": tool.name,
                "args": list(tool.inputSchema.keys()) if tool.inputSchema else []
            })
        return {"tools": tools_list}

async def call_mcp_tool(tool_name: str, params: dict, base_url=None) -> dict:
    """Calls a tool on the MCP server via fastmcp.Client."""
    print(f"\n> Calling tool '{tool_name}' with params: {params}")
    async with client:
        await client.ping()
        try:
            result = await client.call_tool(tool_name, params)
            return result
        except Exception as e:
            print(f"---! Error calling MCP server: {e}")
            return {"error": str(e)}

def format_tools_list(tools_list):
    """Helper to format the tools list for prompts."""
    if not isinstance(tools_list, list):
        return "No tools available or error fetching tools."
    return "\n".join([f"{i+1}. {t['name']}({', '.join(t['args'])})" for i, t in enumerate(tools_list)])

async def autonomous_agent(query: str, llm_model="gpt-oss:20b", base_url=None):
    """Takes a user query, asks Ollama to decide which tool to use, and executes that tool."""
    base_url = base_url or get_mcp_base_url()
    tools_info = await list_mcp_tools(base_url)
    tools_list = tools_info.get("tools", tools_info)
    # Compose a system prompt using the actual tools from MCP
    system_prompt = (
        "You are an expert agent with access to the following tools:\n"
        + format_tools_list(tools_list)
        + "\n\nBased on the user's query, respond with a JSON object: {\"tool\": ..., \"params\": {...}}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    
    # print(f"> System Prompt:\n{system_prompt}\n")
    print(f"> messages:\n{messages}\n")

    # Ollama uses the system prompt (tool list + instructions) to select the tool
    response = ollama.chat(
        model=llm_model,
        messages=messages,
        options={"temperature": 0.0},
        format="json"
    )

    print("> Ollama response:",response.message.content)
    
    action_json_str = response['message']['content']
    print(f"> Ollama suggested action (JSON): {action_json_str}")
    # Try to extract JSON block if extra text is present
    try:
        action = json.loads(action_json_str)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', action_json_str, re.DOTALL)
        if match:
            action = json.loads(match.group(0))
        else:
            return {"error": "Failed to parse JSON from the model's response.", "raw_response": action_json_str}
    tool_name = action.get("tool")
    params = action.get("params", {})
    if not tool_name:
        return {"error": "Model did not specify a tool to use."}
    result = await call_mcp_tool(tool_name, params, base_url)
    return result
    

async def ask_llm_tools(llm_model="gpt-oss:20b", base_url=None):
    """Ask the LLM what tools are available, using the MCP server's tool list."""
    base_url = base_url or get_mcp_base_url()
    tools_info = await list_mcp_tools(base_url)
    tools_list = tools_info.get("tools", tools_info)
    system_prompt = (
        "You are an expert agent. Here are the available tools:\n"
        + format_tools_list(tools_list)
        + "\n\nList the available tools and their arguments in a readable format."
    )
    messages = [{"role": "system", "content": system_prompt}]
    response = ollama.chat(
        model=llm_model,
        messages=messages,
        options={"temperature": 0.0}
    )
    print("> LLM response about available tools:")
    print(response['message']['content'])
    return response['message']['content']

# --- Example Usage ---
if __name__ == "__main__":
    async def run_examples():
        await ask_llm_tools()

        print("\n" + "="*50 + "\n")

        # Example: A query that should use a tool
        user_query = "What is the total sum for the 'sales' column in the file 'data/report.csv'?"
        final_result = await autonomous_agent(user_query)
        print("\n--- Final Result ---")
        print(json.dumps(final_result, indent=2))

        print("\n" + "="*50 + "\n")

        # Example 2: A query that should use the text_append tool
        user_query_2 = "Add the line 'This is a new note.' to the file 'notes.txt'."
        final_result_2 = await autonomous_agent(user_query_2)
        print("\n--- Final Result ---")
        print(json.dumps(final_result_2, indent=2))

    asyncio.run(run_examples())