import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:8090/mcp")

async def call_tool(name: str):
    async with client:
        # Ensure the client is connected
        await client.ping()

        # Call the "ping" tool with the provided name
        result = await client.call_tool("ping", {"name": name})
        print(result)

        tools = await client.list_tools()
        print("Available tools:", tools)    

        

asyncio.run(call_tool("Ford"))