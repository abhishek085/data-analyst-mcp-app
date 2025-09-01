from openai import OpenAI
if __name__ == "__main__":
 
    client = OpenAI(
        base_url="http://localhost:11434/v1",  # Local Ollama API
        api_key="ollama"                       # Dummy key
    )
    
    # response = client.chat.completions.create(
    #     model="gpt-oss:20b",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": "Explain what MXFP4 quantization is."}
    #     ]
    # )
    
    # print(response.choices[0].message.content)  
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather in a given city",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"]
                },
            },
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-oss:20b",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Whats the weather in Boston?"}],
        tools=tools
    )
    
    print(response.choices[0].message)