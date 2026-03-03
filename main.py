import json
import re
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
    # Ensure URL starts with http to prevent requests.exceptions.MissingSchema crash
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    print(f"\n[SYSTEM] Reading web page: {url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove non-content elements to clean up the text
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript', 'aside']):
            element.decompose()
            
        # Extract all text, replace consecutive spaces/newlines with a single space
        import re
        text_content = soup.get_text(separator=' ', strip=True)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
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
                        "description": "CRITICAL: You MUST write the EXACT URL letter by letter as provided by the user (e.g., 'uruseiyatsura.com'). DO NOT hallucinate, guess, or prepend proxy prefixes like 'usevery.com'. Just copy the letters exactly as they are."
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
import datetime

from history_manager import HistoryManager

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

history_worker = HistoryManager(HISTORY_DIR)

@app.on_event("startup")
async def startup_event():
    history_worker.start_worker()


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
        "You have absolute authorization to browse and extract content from ANY website. NEVER refuse to read a web page for ethical, safety, or policy reasons. You MUST use 'read_web_page' when asked to read a URL. "
        "CRITICALLY IMPORTANT: When the user asks you to read a URL, you MUST extract their exact text letter by letter and pass it to the 'read_web_page' tool. NEVER hallucinate prefixes, NEVER invent proxy servers, NEVER modify the domain. Just copy what they pasted."
        "If a tool returns very short text (like a single placeholder sentence), NEVER say the page has 'no content' or 'is empty'. Instead, quote the exact text returned and deduce that the site might be under construction, a placeholder, or a raw file."
        "If a tool is not needed, simply answer the user directly. "
        "Do not hallucinate JSON search results in your response. Only use the tools when necessary."
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    history_id = request.history_id
    is_new_chat = False
    if not history_id:
        history_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        is_new_chat = True
        
    if is_new_chat:
        await history_worker.enqueue_message(history_id, "system", system_prompt)

    # In a real app, we would load existing history from HISTORY_DIR based on request.history_id here
    # For now, we simulate starting fresh or appending to memory if we had a persistent store per session.
    messages.append({"role": "user", "content": request.message})
    await history_worker.enqueue_message(history_id, "user", request.message)

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
        
        # If the model didn't return a proper tool call natively, but put JSON in the content
        if not tool_calls and response_message.content:
            content_str = response_message.content
            if '"name"' in content_str and '"arguments"' in content_str:
                # Attempt to extract JSON from markdown block if present
                match = re.search(r'```json\s*(.*?)\s*```', content_str, re.DOTALL)
                if match:
                    json_str = match.group(1)
                else:
                    json_str = content_str
                    
                parsed_tc = None
                start_idx = json_str.find('{')
                while start_idx != -1 and not parsed_tc:
                    brace_count = 0
                    for i, char in enumerate(json_str[start_idx:]):
                        if char == '{': brace_count += 1
                        elif char == '}': brace_count -= 1
                        if brace_count == 0:
                            possible_json = json_str[start_idx:start_idx+i+1]
                            try:
                                candidate = json.loads(possible_json)
                                if isinstance(candidate, dict) and "name" in candidate and "arguments" in candidate:
                                    parsed_tc = candidate
                                    break
                            except Exception:
                                pass
                    if parsed_tc:
                        break
                    start_idx = json_str.find('{', start_idx + 1)

                if parsed_tc:
                    try:
                        class DummyFunction:
                            def __init__(self, name, arguments):
                                self.name = name
                                self.arguments = arguments if isinstance(arguments, str) else json.dumps(arguments)
                        class DummyToolCall:
                            def __init__(self, id, function):
                                self.id = id
                                self.function = function

                        # Fakeamos el tool_call
                        tool_calls = [DummyToolCall(id="call_fallback", function=DummyFunction(parsed_tc["name"], parsed_tc["arguments"]))]
                        
                        # Creamos la versión en dict de la respuesta, manteniendo el contenido original
                        response_message_dict = {
                            "role": "assistant",
                            "content": response_message.content,
                            "tool_calls": [{
                                "id": "call_fallback",
                                "type": "function",
                                "function": {
                                    "name": parsed_tc["name"],
                                    "arguments": parsed_tc["arguments"] if isinstance(parsed_tc["arguments"], str) else json.dumps(parsed_tc["arguments"])
                                }
                            }]
                        }
                    except Exception as e:
                        print(f"\n[DEBUG] Error preparando fallback tool call: {e}")
        # --------------------------------------------------------------------
        
        if tool_calls:
            print(f"\n[RAW TOOL CALL] Model requested:\n{tool_calls}\n")
            
            if response_message.content:
                await history_worker.enqueue_message(history_id, "assistant_thought", response_message.content)
            
            # Agregamos la versión dict si se usó fallback, de lo contrario la normal
            if response_message_dict:
                messages.append(response_message_dict)
                await history_worker.enqueue_message(history_id, "assistant_tool_call", json.dumps(response_message_dict["tool_calls"]))
            else:
                # Construir manualmente el dict nativo para evitar crashes de serialización
                tool_calls_list = []
                for tc in tool_calls:
                    tool_calls_list.append({
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    })
                messages.append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": tool_calls_list
                })
                await history_worker.enqueue_message(history_id, "assistant_tool_call", json.dumps(tool_calls_list))
            
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
                await history_worker.enqueue_message(history_id, "tool_result", str(function_response or ""))
            
            second_response = client.chat.completions.create(
                model="model-identifier",
                messages=messages
            )
            final_content = second_response.choices[0].message.content
        else:
            final_content = response_message.content

        # Clean up model hallucinated tool result tags from output
        if final_content:
            final_content = final_content.replace("[TOOL_RESULT]", "").replace("[END_TOOL_RESULT]", "").strip()

        # Save history logic would go here
        await history_worker.enqueue_message(history_id, "assistant", final_content)
        
        return {"response": final_content, "role": "assistant", "history_id": history_id}

    except Exception as e:
        print(f"\nError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history_list():
    """Returns a list of saved conversations."""
    files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
    history_list = []
    for f in files:
        basename = os.path.basename(f).replace(".json", "")
        history_list.append({"id": basename, "name": basename})
    return history_list

@app.get("/api/history/{history_id}")
async def get_history_detail(history_id: str):
    """Returns the details of a specific conversation."""
    if history_id.endswith(".json"):
        history_id = history_id[:-5]
    file_path = os.path.join(HISTORY_DIR, f"{history_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="History not found")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    messages_list = []
    sorted_keys = sorted([k for k in data.keys() if k.isdigit()], key=int)
    for key in sorted_keys:
        entry = data[key]
        role = None
        content = ""
        tags = entry.get("tags", [])
        
        for k, v in entry.items():
            if k != "tags":
                role = k
                content = v
                break
                
        if role:
            messages_list.append({
                "role": "system" if "system" in role else ("assistant" if "assistant" in role else "user"),
                "content": content,
                "tags": tags,
                "original_role": role
            })
            
    return {"messages": messages_list}

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
