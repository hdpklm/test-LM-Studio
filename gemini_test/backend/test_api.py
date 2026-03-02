import json
from openai import OpenAI

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"
client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)

tools = [
     {
        "type": "function",
        "function": {
            "name": "read_web_page",
            "description": "Reads the text content of a specific web page URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

messages = [
    {"role": "user", "content": "dime que contenido tiene esta pagina uruseiyatsura.com"}
]

try:
    print("Sending request...")
    completion = client.chat.completions.create(
        model="google/gemma-3-1b", # Using exactly the model from the logs
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = completion.choices[0].message
    print("response_message.content:", repr(response_message.content))
    print("response_message.tool_calls:", response_message.tool_calls)
    
except Exception as e:
    print('Error:', type(e).__name__, str(e))
