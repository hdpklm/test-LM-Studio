import api_websocket

text = """
```json
{
  "name": "schedule_task_checkin",
  "arguments": {
    "task": "Recordarle a Hassan que vaya a dormir",
    "minutes": 1
  }
}
```
"""

print(api_websocket.extract_fallback_tool_calls(text))
