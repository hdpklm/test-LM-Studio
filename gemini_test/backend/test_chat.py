import requests
import json
import time

url = "http://localhost:8000/api/chat"
headers = {'Content-Type': 'application/json'}

def test_prompt(prompt_text):
    print(f"\n--- Testing Prompt: '{prompt_text}' ---")
    payload = {
        "message": prompt_text,
        "history_id": None
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        try:
            print(f"Response data: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except Exception:
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    print("Testing chat API with different prompts to verify tool calling fix.")
    test_prompt("creame una pagina en react de login")
    time.sleep(2)
    test_prompt("Busca en Google las últimas noticias sobre React")
    time.sleep(2)
    test_prompt("busca por internet que contenido tiene la pagina uruseiyatrusa.com")
