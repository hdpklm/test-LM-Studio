import requests
import json

url = "http://localhost:8000/api/chat"
payload = {
	"message": "Hola, ¿quién eres?",
	"history_id": None
}

try:
	response = requests.post(url, json=payload)
	print(f"Status: {response.status_code}")
	print(f"Response: {response.text}")
except Exception as e:
	print(f"Error: {e}")
