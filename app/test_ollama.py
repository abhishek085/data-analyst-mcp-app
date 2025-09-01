from ollama import chat
from ollama import ChatResponse

if __name__ == "__main__":

    response: ChatResponse = chat(model='gpt-oss:20b', messages=[
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
    },
    ])
    print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)