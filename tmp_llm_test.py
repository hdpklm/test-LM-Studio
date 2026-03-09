import httpx
import json
import asyncio

async def test_llm():
    messages = [
        {"role": "system", "content": "eres un asistente"},
        {"role": "user", "content": "necesito despertar a las 8:45"},
        {"role": "assistant", "content": "¡Entendido! Te despiertas a las 8:45. ¿Necesitas algo más?"},
        {"role": "user", "content": "necesito despertar a las 8:45"}
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "schedule_task_checkin",
                "description": "Agenda un recordatorio en X minutos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "minutes": {"type": "integer"}
                    },
                    "required": ["task", "minutes"]
                }
            }
        }
    ]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "messages": messages,
                    "tools": tools,
                    "temperature": 0.5,
                    "max_tokens": 1000
                },
                timeout=10.0
            )
            print(response.status_code)
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
