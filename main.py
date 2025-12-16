import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from googlesearch import search

# --- Configuration ---
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
    }
]

# --- Main Interaction Loop ---

def main():
    client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)
    
    print(f"Connected to LM-Studio at {LM_STUDIO_BASE_URL}")
    print("Type 'quit' to exit.")
    
    system_prompt = (
        "You are a helpful assistant. "
        "You have access to 'search_google_and_print' to find information and 'read_web_page' to read content from URLs. "
        "If the user requests JSON output, ensure the response is strictly valid JSON, without markdown formatting. "
        "Unless specified otherwise, use this format for search results:\n"
        "[\n"
        "  { \"url\": \"https://www.example.com/\", \"title\": \"example\", \"desc\": \"example description\" }\n"
        "]"
    )

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            completion = client.chat.completions.create(
                model="model-identifier",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = completion.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                # Log raw tool calls
                print(f"\n[RAW TOOL CALL] Model requested:\n{tool_calls}\n")
                
                messages.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    function_response = None
                    
                    if function_name == "search_google_and_print":
                        function_response = search_google_and_print(
                            query=function_args.get("query")
                        )
                    elif function_name == "read_web_page":
                        function_response = read_web_page(
                            url=function_args.get("url")
                        )
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response or ""
                    })
                
                # Get final answer
                second_response = client.chat.completions.create(
                    model="model-identifier",
                    messages=messages
                )
                print(f"\nAssistant: {second_response.choices[0].message.content}")
                messages.append(second_response.choices[0].message)
                
            else:
                print(f"\nAssistant: {response_message.content}")
                messages.append(response_message)
                
        except Exception as e:
            print(f"\nError: {e}")
            print("Make sure LM-Studio server is running and accessible.")

if __name__ == "__main__":
    main()
