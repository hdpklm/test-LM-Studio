import api_websocket

text = """
```json
[
  {
    "type": "function",
    "function": {
      "name": "get_estimated_duration",
      "arguments": {"task": "Hasan"}
    }
  },
  {
    "type": "function",
    "function": {
      "name": "schedule_task_checkin",
      "arguments": {"task": "Hasan", "minutes": 30}
    }
  },
  {
    "type": "function",
    "function": {
      "name": "save_task_duration",
      "arguments": {"task": "Hasan", "minutes": 30}
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_estimated_duration",
      "arguments": {"task": "Hasan"}
    }
  }
]
```
"""

print(api_websocket.extract_fallback_tool_calls(text))
