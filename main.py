import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from googlesearch import search

# --- Configuration LM-Studio ---
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"

# --- Tools Definitions ---

def search_google_and_print(query):
    """
    Searches Google for the given query, prints a message to the console,
    and returns the top search results.
    """
    print(f"\n[SYSTEM] Printing message to console: Searching for '{query}'...")
    
    try:
        results = []
        # num_results=3, advanced=True returns objects with titles/descriptions
        search_generator = search(query, num_results=3, advanced=True)
        
        for result in search_generator:
            results.append({
                "title": result.title,
                "description": result.description,
                "url": result.url
            })
            if len(results) >= 3:
                break
        
        # Log the tool output for visibility
        output_json = json.dumps(results, indent=2)
        print(f"\n[TOOL OUTPUT] search_google_and_print:\n{output_json}\n")
        return json.dumps(results)
    except Exception as e:
        error_msg = json.dumps({"error": str(e)})
        print(f"\n[TOOL OUTPUT] search_google_and_print error:\n{error_msg}\n")
        return error_msg

def read_web_page(url):
    """
    Reads the content of a web page and returns the text.
    """
    print(f"\n[SYSTEM] Reading web page: {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from paragraphs to avoid getting menu items/scripts
        paragraphs = soup.find_all('p')
        text_content = "\n".join([p.get_text() for p in paragraphs])
        
        # Limit content length to avoid context window explosion
        max_chars = 4000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "... [Content Truncated]"
            
        if not text_content.strip():
            text_content = "No readable text found on page."

        # Log the tool output for visibility
        print(f"\n[TOOL OUTPUT] read_web_page (first 500 chars):\n{text_content[:500]}...\n")
        return text_content
    except Exception as e:
        error_msg = str(e)
        print(f"\n[TOOL OUTPUT] read_web_page error:\n{error_msg}\n")
        return f"Error reading page: {error_msg}"

def deep_thinking(prompt):
    """
    Generates 5 different thoughts about a prompt and then combines them to find the best synthesis.
    """
    client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)
    thoughts = []
    print(f"\n[SYSTEM] Deep Thinking: Generating 5 thoughts for '{prompt[:50]}...'")
    
    for i in range(5):
        print(f"  > Generating thought {i+1}/5...")
        try:
            response = client.chat.completions.create(
                model="model-identifier",
                messages=[{"role": "user", "content": f"Piensa de forma creativa y profunda sobre esto: {prompt}"}],
                temperature=0.7
            )
            thoughts.append(response.choices[0].message.content)
        except Exception as e:
            print(f"  > Error in thought {i+1}: {e}")
            thoughts.append(f"Error generating thought {i+1}: {e}")

    print(f"  > Aggregating best ideas...")
    aggregation_prompt = (
        f"A continuación se presentan 5 perspectivas o pensamientos diferentes sobre el prompt: '{prompt}'.\n\n"
        "--- PENSAMIENTOS ---\n"
        + "\n\n".join([f"Pensamiento {i+1}:\n{t}" for i, t in enumerate(thoughts)]) +
        "\n\n--- TAREA ---\n"
        "Analiza estos pensamientos y extrae las mejores ideas, o crea una síntesis superior que combine lo mejor de todos ellos. "
        "Tu respuesta debe ser el resultado final de este pensamiento profundo."
    )

    try:
        final_response = client.chat.completions.create(
            model="model-identifier",
            messages=[{"role": "user", "content": aggregation_prompt}]
        )
        result = final_response.choices[0].message.content
        print(f"\n[TOOL OUTPUT] deep_thinking result successful.\n")
        return result
    except Exception as e:
        error_msg = f"Error aggregating thoughts: {e}"
        print(f"\n[TOOL OUTPUT] deep_thinking error: {error_msg}\n")
        return error_msg

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_google_and_print",
            "description": "Searches Google for a query. Use this to find current information or URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_web_page",
            "description": "Reads the text content of a specific web page URL. Use this to get details from a search result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to read."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deep_thinking",
            "description": "Performs deep thinking by generating multiple perspectives and combining them. Use this for complex problems, creative tasks, or when a high-quality synthesis is needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The topic or prompt to think deeply about."
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]

# --- FastAPI Server and Endpoints ---
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import glob

app = FastAPI(title="LM-Studio Custom Chat API", version="1.8")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
HISTORY_DIR = "history-chat"
GENERATED_DIR = "generated-files"
UPLOAD_DIR = "history-chat/uploads" # For simplicity, putting uploads inside history

os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    message: str
    history_id: Optional[str] = None  # Optional: continue existing conversation

class ChatMessage(BaseModel):
    role: str
    content: str


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handles user chat messages, maintains history, and processes tool calls.
    """
    print(f"\n[DEBUG] Incoming chat request: {request.dict()}")
    client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)
    
    system_prompt = (
        "You are a helpful AI assistant. "
        "You have access to tools. If you need to search for information, use the 'search_google_and_print' tool. "
        "If you need to read a URL, use 'read_web_page'. "
        "If a tool is not needed, simply answer the user directly. "
        "Do not hallucinate JSON search results in your response. Only use the tools when necessary."
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    # In a real app, we would load existing history from HISTORY_DIR based on request.history_id here
    # For now, we simulate starting fresh or appending to memory if we had a persistent store per session.
    messages.append({"role": "user", "content": request.message})

    try:
        completion = client.chat.completions.create(
            model="model-identifier",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls
        
        # --- Fallback Parser para modelos que escupen Tool Calls en texto ---
        response_message_dict = None
        if not tool_calls and response_message.content:
            content_str = response_message.content
            if '"name"' in content_str and '"arguments"' in content_str:
                import json
                parsed_tc = None
                start_idx = content_str.find('{')
                while start_idx != -1 and not parsed_tc:
                    brace_count = 0
                    for i, char in enumerate(content_str[start_idx:]):
                        if char == '{': brace_count += 1
                        elif char == '}': brace_count -= 1
                        if brace_count == 0:
                            json_str = content_str[start_idx:start_idx+i+1]
                            try:
                                candidate = json.loads(json_str)
                                if isinstance(candidate, dict) and "name" in candidate and "arguments" in candidate:
                                    parsed_tc = candidate
                                    break
                            except Exception:
                                pass
                    if parsed_tc:
                        break
                    start_idx = content_str.find('{', start_idx + 1)

                if parsed_tc:
                    try:
                        class DummyFunction:
                            def __init__(self, name, arguments):
                                self.name = name
                                self.arguments = json.dumps(arguments) if isinstance(arguments, dict) else str(arguments)
                        class DummyToolCall:
                            def __init__(self, id, function):
                                self.id = id
                                self.function = function

                        # Fakeamos el tool_call
                        tool_calls = [DummyToolCall(id="call_fallback", function=DummyFunction(parsed_tc["name"], parsed_tc["arguments"]))]
                        
                        # Creamos la versión en dict de la respuesta vacía con herramientas
                        response_message_dict = {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [{
                                "id": "call_fallback",
                                "type": "function",
                                "function": {
                                    "name": parsed_tc["name"],
                                    "arguments": json.dumps(parsed_tc["arguments"]) if isinstance(parsed_tc["arguments"], dict) else str(parsed_tc["arguments"])
                                }
                            }]
                        }
                    except Exception as e:
                        print(f"\n[DEBUG] Error preparando fallback tool call: {e}")
        # --------------------------------------------------------------------
        
        if tool_calls:
            print(f"\n[RAW TOOL CALL] Model requested:\n{tool_calls}\n")
            # Agregamos la versión dict si se usó fallback, de lo contrario la normal
            if response_message_dict:
                messages.append(response_message_dict)
            else:
                messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_response = None
                
                if function_name == "search_google_and_print":
                    function_response = search_google_and_print(query=function_args.get("query"))
                elif function_name == "read_web_page":
                    function_response = read_web_page(url=function_args.get("url"))
                elif function_name == "deep_thinking":
                    function_response = deep_thinking(prompt=function_args.get("prompt"))
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response or ""
                })
            
            second_response = client.chat.completions.create(
                model="model-identifier",
                messages=messages
            )
            final_content = second_response.choices[0].message.content
        else:
            final_content = response_message.content

        # Save history logic would go here
        
        return {"response": final_content, "role": "assistant"}

    except Exception as e:
        print(f"\nError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history_list():
    """Returns a list of saved conversations."""
    files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
    history_list = []
    for f in files:
        history_list.append({"id": os.path.basename(f), "name": os.path.basename(f).replace(".json", "")})
    return history_list

@app.get("/api/history/{history_id}")
async def get_history_detail(history_id: str):
    """Returns the details of a specific conversation."""
    file_path = os.path.join(HISTORY_DIR, f"{history_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="History not found")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles file uploads."""
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'", "path": file_location}

@app.get("/api/generated")
async def list_generated_files():
    """Lists files generated by the LLM (for the right drawer)."""
    files = glob.glob(os.path.join(GENERATED_DIR, "*.*"))
    # In a full version, we'd parse versions. For now, just return names.
    gen_list = []
    for f in files:
        gen_list.append({"filename": os.path.basename(f), "path": f})
    return gen_list

@app.get("/api/download/{filename}")
async def download_generated_file(filename: str):
    """Provides a download link for generated files."""
    file_path = os.path.join(GENERATED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

if __name__ == "__main__":
    import uvicorn
    # To run: python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
