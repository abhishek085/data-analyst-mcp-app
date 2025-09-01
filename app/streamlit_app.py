import streamlit as st
import requests
import json
import ollama

# The base URL of your running MCP server
BASE_URL = "http://127.0.0.1:8090"

def call_mcp_tool(tool_name: str, params: dict) -> dict:
    # ... (Your existing function) ...
    endpoint = f"{BASE_URL}/call_tool"
    payload = {
        "tool_name": tool_name,
        "args": params
    }
    
    st.write(f"\n> Calling tool '{tool_name}' with params: {params}")
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"---! Error calling MCP server: {e}")
        return {"error": str(e)}

def autonomous_agent(query: str):
    # ... (Your existing function) ...
    messages = [
        {
            "role": "system",
            "content": """You are an expert agent that converts user queries into tool calls.
...
"""
        },
        {
            "role": "user",
            "content": query
        }
    ]

    st.write(f"> User Query: '{query}'")
    st.write("> Asking Ollama to choose a tool...")

    try:
        response = ollama.chat(
            model="llama3",
            messages=messages,
            options={"temperature": 0.0},
            format="json"
        )
        
        action_json_str = response['message']['content']
        st.write(f"> Ollama suggested action (JSON): {action_json_str}")

        action = json.loads(action_json_str)
        
        tool_name = action.get("tool")
        params = action.get("params", {})

        if not tool_name:
            return {"error": "Model did not specify a tool to use."}

        result = call_mcp_tool(tool_name, params)
        return result

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON from the model's response.", "raw_response": action_json_str}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# --- Streamlit Front-end Code ---
st.title("My Autonomous Agent App")

user_input = st.text_input("Enter your query:")

if st.button("Run Agent"):
    if user_input:
        with st.spinner("Running agent..."):
            result = autonomous_agent(user_input)
            
            # Display the result
            st.subheader("Result")
            st.json(result)
    else:
        st.warning("Please enter a query.")