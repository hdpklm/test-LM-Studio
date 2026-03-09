import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import re

app = FastAPI()

# Rutas a archivos clave
AYUDANTE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORIAL_FILE = os.path.join(AYUDANTE_DIR, "historial_global.jsonl")
OBJETIVOS_FILE = os.path.join(AYUDANTE_DIR, "objetivos.json")

def append_to_history(role: str, content: str):
    """Guarda en historial_global.jsonl la interacción inmutable."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": content
    }
    with open(HISTORIAL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

async def trigger_monitor():
    """Llama al agente monitor tras cada interacción."""
    # Aquí iría la lógica del LM para el Monitor. Por ahora, mockeado:
    print(f"[MONITOR] Analizando comportamiento e interacciones recientes del historial.")
    # El monitor leerá 'decisiones_monitor.md', y si genera una versión:
    # Creará subcarpeta en 'versiones_syspro/YYYYMMDD_HHMMSS/'

import httpx
import uuid

SCHEDULE_FILE = os.path.join(AYUDANTE_DIR, "schedule.json")

def get_current_schedule():
    """Carga el schedule real desde schedule.json"""
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_schedule(schedule_data):
    """Guarda el schedule en disco"""
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, indent=4, ensure_ascii=False)

TASK_DURATIONS_FILE = os.path.join(AYUDANTE_DIR, "task_durations.json")

def get_task_durations():
    try:
        with open(TASK_DURATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_task_durations(data):
    with open(TASK_DURATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Herramientas nativas para pasar al LLM
ayudante_tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_task_checkin",
            "description": "Agenda un recordatorio en X minutos para preguntarle al usuario si ya termino una tarea.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Nombre o descripcion de la tarea (ej. 'Lavar la ropa')."
                    },
                    "minutes": {
                        "type": "integer",
                        "description": "Cantidad de minutos en los que chequear con el usuario."
                    }
                },
                "required": ["task", "minutes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_specific_time",
            "description": "Agenda un mensaje, alarma o propuesta para una hora exacta en el futuro.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Lo que le tienes que decir o proponer al usuario (ej. 'Hacer la cena')."
                    },
                    "time": {
                        "type": "string",
                        "description": "Hora exacta en formato HH:MM (ej. '18:00')."
                    }
                },
                "required": ["task", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_task_duration",
            "description": "Guarda el tiempo final real que le tomo al usuario completar una tarea, para no tener que adivinarlo en el futuro.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "El nombre de la tarea."
                    },
                    "minutes": {
                        "type": "integer",
                        "description": "Minutos totales que le tomo."
                    }
                },
                "required": ["task", "minutes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_estimated_duration",
            "description": "Consulta en la base de datos cuanto tiempo suele tardar el usuario en hacer una tarea especifica.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Nombre de la tarea a consultar."
                    }
                },
                "required": ["task"]
            }
        }
    }
]

from datetime import timedelta

def schedule_task_checkin_logic(task_desc: str, minutes: int):
    """Calcula la hora futura y asigna el checkin."""
    schedule = get_current_schedule()
    
    ahora_dt = datetime.now()
    futuro_dt = ahora_dt + timedelta(minutes=minutes)
    time_str = futuro_dt.strftime("%H:%M")
    
    nuevo_item = {
        "id": str(uuid.uuid4()),
        "time": time_str,
        "task": task_desc,
        "status": "pending",
        "type": "checkin"
    }
    schedule.append(nuevo_item)
    schedule.sort(key=lambda x: x["time"])
    save_schedule(schedule)
    return f"He programado un check-in de la tarea '{task_desc}' para las {time_str} ({minutes} minutos desde ahora)."

def schedule_specific_time_logic(task_desc: str, time_str: str):
    """Asigna una alarma a una hora especifica."""
    schedule = get_current_schedule()
    nuevo_item = {
        "id": str(uuid.uuid4()),
        "time": time_str.strip(),
        "task": task_desc.strip(),
        "status": "pending",
        "type": "alarm"
    }
    schedule.append(nuevo_item)
    schedule.sort(key=lambda x: x["time"])
    save_schedule(schedule)
    return f"He agendado '{task_desc}' a las {time_str} correctamente."

def save_task_duration_logic(task_desc: str, minutes: int):
    """Guarda en json lo que tardo la tarea."""
    durations = get_task_durations()
    # Podemos hacer un promedio si ya existe, o sobreescribir. Vamos a sobreescribir o guardar array.
    # Por simpleza, lo guardamos como el ultimo valor (o calculamos un promedio simple).
    if task_desc in durations:
        viejo_promedio = durations[task_desc]["avg_minutes"]
        cantidad = durations[task_desc]["count"]
        nuevo_promedio = ((viejo_promedio * cantidad) + minutes) / (cantidad + 1)
        durations[task_desc] = {
            "avg_minutes": round(nuevo_promedio),
            "count": cantidad + 1
        }
    else:
        durations[task_desc] = {
            "avg_minutes": minutes,
            "count": 1
        }
    save_task_durations(durations)
    return f"Tiempo de la tarea '{task_desc}' guardado: {minutes} minutos."

def get_estimated_duration_logic(task_desc: str):
    """Lee del json de tiempos."""
    durations = get_task_durations()
    # Buscar match exacto o substring
    for key, value in durations.items():
        if key.lower() in task_desc.lower() or task_desc.lower() in key.lower():
            mins = value["avg_minutes"]
            return f"El usuario suele tardar aproximadamente {mins} minutos en hacer '{key}'."
    return f"No tengo registros previos de la duracion de '{task_desc}'. Deberas preguntarle al usuario o hacer una estimacion aproximada tú mismo."

def extract_fallback_tool_calls(text: str):
    """Intercepta JSON tools generados en texto crudo por modelos locales sin soporte nativo."""
    import re
    tool_calls = []
    
    # Buscar bloques ```json ... ```
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        json_str = match.group(1).strip()
    else:
        # Intentar buscar algo que parezca un JSON array o un JSON object al inicio o fin
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
        else:
            return []
            
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            data = [data]
            
        for ix, item in enumerate(data):
            if "function" in item:
                fn_name = item["function"].get("name", "")
                func_args = item["function"].get("arguments", {})
                if isinstance(func_args, dict):
                    func_args = json.dumps(func_args)
                tool_calls.append({
                    "id": f"call_fallback_{ix}",
                    "type": "function",
                    "function": {"name": fn_name, "arguments": func_args}
                })
            elif "name" in item:
                fn_name = item.get("name", "")
                func_args = item.get("arguments", {})
                if isinstance(func_args, dict):
                    func_args = json.dumps(func_args)
                tool_calls.append({
                    "id": f"call_fallback_{ix}",
                    "type": "function",
                    "function": {"name": fn_name, "arguments": func_args}
                })
    except Exception as e:
        print(f"Fallback parse error: {e}")
        
    return tool_calls

async def agent_response(user_msg: str, websocket: WebSocket):
    """Obtiene la respuesta del Asistente Personal separando detección de tools de la respuesta final."""
    try:
        with open(OBJETIVOS_FILE, "r", encoding="utf-8") as f:
            objetivos = json.load(f)
    except Exception:
        objetivos = {}
        
    try:
        with open(os.path.join(AYUDANTE_DIR, "asistente_personal.md"), "r", encoding="utf-8") as f:
            sys_prompt = f.read()
    except Exception:
        sys_prompt = "Eres un asistente personal."
        
    ahora = datetime.now()
    fecha_hoy = ahora.strftime("%Y-%m-%d")
    hora_actual = ahora.strftime("%H:%M")
    
    sys_prompt += f"\n\n[SISTEMA - IMPORTANTE]\nFecha Actual: {fecha_hoy}\nHora Actual: {hora_actual}\n\nObjetivos Actuales del Usuario:\n{json.dumps(objetivos, indent=2, ensure_ascii=False)}"
    
    historial = []
    mock_text = "Asistente (Schedule Check): Tienes la meta"
    last_role = None
    
    try:
        if os.path.exists(HISTORIAL_FILE):
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    role = entry["role"]
                    content = entry["content"]
                    if mock_text in content: continue
                    if role == last_role:
                        historial[-1] = {"role": role, "content": content}
                    else:
                        historial.append({"role": role, "content": content})
                        last_role = role
    except Exception: pass
        
    historial = historial[-10:]
    if historial and historial[0]["role"] != "user":
        historial = historial[1:]
    
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(historial)

    # --- FASE 1: DETECCIÓN DE TOOLS (SILENCIOSA) ---
    await websocket.send_json({"type": "thinking", "status": "Preparando herramientas..."})
    
    tool_calls = []
    try:
        async with httpx.AsyncClient() as client:
            resp_tools = await client.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "messages": messages + [{"role": "user", "content": "[SISTEMA: Analiza si necesitas usar herramientas para responder. Si es así, genera el JSON. NO saludes ni hables con el usuario todavía.]"}],
                    "tools": ayudante_tools,
                    "temperature": 0.1, # Temperatura baja para detección precisa
                    "max_tokens": 500,
                    "stream": False
                },
                timeout=60.0
            )
            resp_tools.raise_for_status()
            data_tools = resp_tools.json()
            msg_tools = data_tools["choices"][0]["message"]
            
            # Extraer nativas
            if "tool_calls" in msg_tools and msg_tools["tool_calls"]:
                tool_calls = msg_tools["tool_calls"]
            else:
                # Extraer fallback
                tool_calls = extract_fallback_tool_calls(msg_tools.get("content", ""))
    except Exception as e:
        print(f"Tool detection error: {e}")

    # --- FASE 2: EJECUCIÓN Y RESPUESTA (STREAMING) ---
    if tool_calls:
        # Ejecutar herramientas
        resultados_tools = []
        for tc in tool_calls:
            try:
                func_obj = tc.get("function", {})
                fn_name = func_obj.get("name", "")
                args_raw = func_obj.get("arguments", {})
                args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                
                status_map = {
                    "schedule_task_checkin": "Agendando recordatorio...",
                    "schedule_specific_time": "Programando alarma...",
                    "save_task_duration": "Guardando progreso...",
                    "get_estimated_duration": "Consultando historial de tiempos..."
                }
                await websocket.send_json({"type": "thinking", "status": status_map.get(fn_name, f"Ejecutando {fn_name}...")})
                
                if fn_name == "schedule_task_checkin":
                    res = schedule_task_checkin_logic(args.get("task", "Tarea"), args.get("minutes", 30))
                elif fn_name == "schedule_specific_time":
                    res = schedule_specific_time_logic(args.get("task", "Alarma"), args.get("time", "12:00"))
                elif fn_name == "save_task_duration":
                    res = save_task_duration_logic(args.get("task", "Tarea"), args.get("minutes", 30))
                elif fn_name == "get_estimated_duration":
                    res = res = get_estimated_duration_logic(args.get("task", "Tarea"))
                else: res = f"Tool '{fn_name}' no encontrada."
                resultados_tools.append(f"Tool '{fn_name}' retornó: {res}")
            except Exception as e:
                resultados_tools.append(f"Error en tool: {str(e)}")

        # Preparar mensaje con resultados
        messages.append({
            "role": "system",
            "content": f"SISTEMA: Las herramientas seleccionadas se ejecutaron correctamente: {', '.join(resultados_tools)}. NO generes JSON, NO generes bloques de código. Simplemente confirma al usuario de forma amable y natural lo que has hecho."
        })
    else:
        # No hubo tools, solo responder al mensaje original
        pass

    # Streaming final
    await websocket.send_json({"type": "thinking", "status": "Redactando respuesta..."})
    full_response = ""

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                "http://localhost:1234/v1/chat/completions",
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "stream": True,
                    "stop": ["```json", "{\"name\""] # Detener alucinaciones de JSON
                },
                timeout=120.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "): continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]": break
                    
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta and delta["content"]:
                            content_piece = delta["content"]
                            
                            # Filtro extra por si acaso el stop-token falla o es parcial
                            if "```json" in full_response + content_piece:
                                continue
                                
                            full_response += content_piece
                            await websocket.send_json({"type": "chat_chunk", "data": content_piece})
                    except: continue
        except Exception as e:
            full_response = f"*(Error de conexión: {str(e)})*"
            await websocket.send_json({"type": "chat_chunk", "data": full_response})

    # Limpieza final post-procesada para el historial
    full_response = re.sub(r"```json.*?```", "", full_response, flags=re.DOTALL)
    full_response = re.sub(r"\{.*\"name\".*\}", "", full_response, flags=re.DOTALL)
    full_response = full_response.strip()

    return full_response

@app.websocket("/ayudante")
async def websocket_ayudante(websocket: WebSocket):
    await websocket.accept()
    print("[WebSocket] Cliente conectado a /ayudante.")
    
    # Variables de estado para el seguimiento proactivo
    last_user_interaction = datetime.now()
    current_checkin_interval = 5 # minutos iniciales
    
    try:
        # Tarea de fondo: verifica schedule y proactividad
        async def background_monitor_loop():
            nonlocal last_user_interaction, current_checkin_interval
            while True:
                ahora_dt = datetime.now()
                ahora_str = ahora_dt.strftime("%H:%M")
                
                # 1. Check de Schedule (Alertas pasivas)
                schedule = get_current_schedule()
                actualizado = False
                for item in schedule:
                    if item["status"] == "pending" and item["time"] == ahora_str:
                        item["status"] = "done"
                        actualizado = True
                        alerta = f"[{ahora_str}] Es hora de: {item['task']}"
                        append_to_history("assistant", alerta)
                        await websocket.send_json({"type": "chat_message", "data": alerta})
                
                if actualizado:
                    save_schedule(schedule)
                    await websocket.send_json({"type": "schedule_update", "data": schedule})
                    asyncio.create_task(trigger_monitor())

                # 2. Check de Proatividad (Seguimiento pesado)
                minutos_inactivo = (ahora_dt - last_user_interaction).total_seconds() / 60
                if minutos_inactivo >= current_checkin_interval:
                    print(f"[Proactivo] Check-in iniciado tras {minutos_inactivo:.1f} min de inactividad.")
                    
                    # Generar mensaje proactivo con el LLM
                    # Pasamos un prompt especial que indica la hora y pide control
                    proactive_prompt = f"[SISTEMA: CHECK-IN PROACTIVO - {ahora_str}]\nLlevas {int(minutos_inactivo)} minutos sin reportar. Pregunta al usuario si todo va bien con sus tareas o qué está haciendo. Sé breve y proactivo. Incluye la hora actual."
                    
                    # Usamos agent_response pero marcando que es proactivo si fuera necesario (aquí es igual)
                    res_proactiva = await agent_response(proactive_prompt, websocket)
                    
                    print(f"[Ayudante (Proactivo)]: {res_proactiva}")
                    append_to_history("assistant", res_proactiva)
                    
                    await websocket.send_json({"type": "chat_end"})
                    
                    # Escalar intervalo: 5 -> 10 -> 20 ... -> 240 (4h)
                    last_user_interaction = ahora_dt # Reseteamos el punto de inicio para el siguiente salto
                    current_checkin_interval = min(current_checkin_interval * 2, 240)
                    print(f"[Proactivo] Nuevo intervalo de espera: {current_checkin_interval} min.")

                # Check cada 30 segundos
                await asyncio.sleep(30)
                
        # Iniciar loop del monitor acoplado a la conexión
        bg_task = asyncio.create_task(background_monitor_loop())

        while True:
            # 1. Espera respuesta del frontend
            raw_data = await websocket.receive_text()
            
            # Reset de proactividad al recibir CUALQUIER mensaje del usuario
            last_user_interaction = datetime.now()
            current_checkin_interval = 5
            
            try:
                # Intentar parsear como JSON para comandos especiales
                payload = json.loads(raw_data)
                if payload.get("type") == "reset":
                    print("[WebSocket] Solicitud de RESET recibida.")
                    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
                        f.write("")
                    save_schedule([])
                    await websocket.send_json({"type": "reset_confirmed"})
                    continue
                else:
                    data = raw_data
            except json.JSONDecodeError:
                data = raw_data

            print(f"[Usuario]: {data}")
            append_to_history("user", data)
            
            # 2. Genera respuesta
            respuesta_limpia = await agent_response(data, websocket)
            
            print(f"[Ayudante]: {respuesta_limpia}")
            append_to_history("assistant", respuesta_limpia)
            
            await websocket.send_json({"type": "chat_end"})
            
            await websocket.send_json({
                "type": "schedule_update",
                "data": get_current_schedule()
            })
            
            asyncio.create_task(trigger_monitor())

    except WebSocketDisconnect:
        print("[WebSocket] Cliente desconectado.")
        bg_task.cancel()
    except Exception as e:
        print(f"[WebSocket] Error: {e}")

if __name__ == "__main__":
    import uvicorn
    # Se ejecuta en el puerto 8001 para no pisar el servidor `main.py` de test-LM-Studio
    uvicorn.run("api_websocket:app", host="0.0.0.0", port=8001, reload=True)
