import os
import json
import asyncio
from openai import AsyncOpenAI

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"

class HistoryManager:
    """
    Manages non-destructive (append-only) history saving for chat sessions.
    Also queries the LLM in the background to generate search tags for messages.
    """
    def __init__(self, history_dir):
        self.history_dir = history_dir
        self.queue = asyncio.Queue()
        self.locks = {} # Mutex per history_id to ensure sequential writes
        self._task = None
        self.client = AsyncOpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)

    def start_worker(self):
        """Starts the background asyncio worker to process the queue."""
        if self._task is None:
            self._task = asyncio.create_task(self._worker())

    async def enqueue_message(self, history_id: str, role: str, content: str):
        """Adds a message to the background processing queue."""
        await self.queue.put((history_id, role, content))

    async def _worker(self):
        """Continuously processes messages from the queue."""
        while True:
            try:
                history_id, role, content = await self.queue.get()
                
                if history_id not in self.locks:
                    self.locks[history_id] = asyncio.Lock()
                
                async with self.locks[history_id]:
                    await self._process_and_save(history_id, role, content)
                
                self.queue.task_done()
            except Exception as e:
                print(f"[HistoryManager] Worker Error: {e}")

    async def _process_and_save(self, history_id: str, role: str, content: str):
        # 1. Ask LLM to generate tags
        tags = []
        # We don't generate tags for system messages to save resources
        if role != "system" and content.strip():
            tags = await self._generate_tags_for_message(content)
            
        # Ensure we don't duplicate .json if the frontend passed it as ID
        if history_id.endswith('.json'):
            history_id = history_id[:-5]
            
        # 2. Append to file using thread so it doesn't block the loop
        file_path = os.path.join(self.history_dir, f"{history_id}.json")
        await asyncio.to_thread(self._secure_append_to_history, file_path, role, content, tags)

    async def _generate_tags_for_message(self, content: str) -> list[str]:
        system_prompt = (
            "Extrae todas las palabras claves de este mensaje que afecten negativamente o positivamente a "
            "una búsqueda de este mensaje. Devuelve SOLO las palabras separadas por comas. "
            "NO devuelvas introducciones ni despedidas."
        )
        
        async def fetch_tags():
            try:
                resp = await self.client.chat.completions.create(
                    model="model-identifier",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content}
                    ],
                    temperature=0.8
                )
                return resp.choices[0].message.content
            except Exception:
                return ""

        # Pass the message 3 times in parallel
        results = await asyncio.gather(
            fetch_tags(),
            fetch_tags(),
            fetch_tags()
        )
        
        consensus_prompt = (
            "A continuación tienes 3 análisis de palabras claves de un mismo mensaje.\n"
            "Resultados:\n"
            f"1: {results[0]}\n"
            f"2: {results[1]}\n"
            f"3: {results[2]}\n\n"
            "Selecciona las palabras claves que realmente encajen y pertenezcan a este mensaje.\n"
            "Devuelve tu selección como un array estricto de JSON. Ej: [\"palabra 1\", \"palabra 2\"]. "
            "NADA MÁS."
        )
        
        try:
            consensus_resp = await self.client.chat.completions.create(
                model="model-identifier",
                messages=[
                    {"role": "system", "content": "Eres un consolidador de arrays JSON puro y sin markdown."},
                    {"role": "user", "content": consensus_prompt}
                ],
                temperature=0.1
            )
            raw_json = consensus_resp.choices[0].message.content.strip()
            
            import re
            match = re.search(r'\[(.*?)\]', raw_json, re.DOTALL)
            if match:
                return json.loads(f"[{match.group(1)}]")
            else:
                candidate = json.loads(raw_json)
                if isinstance(candidate, list):
                    return candidate
                return []
        except Exception as e:
            print(f"[HistoryManager] Consensus parsing error: {e}. Raw response: {raw_json if 'raw_json' in locals() else 'None'}")
            return []

    def _secure_append_to_history(self, file_path: str, role: str, content: str, tags: list[str]):
        """
        Appends the new message JSON to the end of the file by seeking to the last '}'
        and truncating, preserving SSD cycles by avoiding full file overwrites.
        """
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("{}")

        # 1. Read the JSON using standard load just to retrieve the highest index. 
        # Reading does NOT damage SSD, writing does.
        next_index = 0
        has_elements = False
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                keys = [int(k) for k in data.keys() if k.isdigit()]
                next_index = max(keys) + 1 if keys else 0
                has_elements = len(data) > 0
            except Exception:
                pass # Default to index 0

        # Construct the new JSON entry snippet
        new_entry = {
            role: content,
            "tags": tags
        }
        
        # We dummy-dump it as {"index": {...}} then slice out the outer brackets
        entry_json = json.dumps({str(next_index): new_entry}, ensure_ascii=False)
        entry_inner = entry_json.strip()[1:-1] # Removes the outer '{' and '}'
        
        prefix = ",\n" if has_elements else "\n"
        append_data = prefix + entry_inner + "\n}"

        # 2. Open in binary read-write to do binary backwards seeking, which allows
        # us to confidently find the last '}' and overwrite from that exact byte.
        with open(file_path, 'r+b') as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            
            last_bracket_pos = -1
            while pos > 0:
                pos -= 1
                f.seek(pos)
                char = f.read(1)
                if char == b'}':
                    last_bracket_pos = pos
                    break
            
            if last_bracket_pos != -1:
                f.seek(last_bracket_pos)
                f.truncate() # Remove the last }
                f.write(append_data.encode('utf-8')) # Append the new object + closing }
            else:
                # Fallback if file is corrupted
                f.seek(0)
                f.truncate()
                f.write(b"{\n")
                f.write(entry_inner.encode('utf-8'))
                f.write(b"\n}")
