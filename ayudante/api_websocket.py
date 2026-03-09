import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

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

async def agent_response(user_msg: str):
    """Obtiene la respuesta del Asistente Personal usando el LLM."""
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
    
    # Leer el historial para darle contexto continuo al agente,
    # IGNORANDO el mensaje mock antiguo para romper el loop
    # y OBLIGANDO a que los roles se alternen (user -> assistant -> user)
    # para evitar errores 400 Bad Request en LM Studio (strict roles)
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
                    
                    if mock_text in content:
                        continue
                        
                    # Filtro de roles alternos: si el rol es igual al anterior, ignoramos el mensaje viejo
                    # o lo concatenamos. Lo más fácil para LLMs chat is ignorar el anterior o solo tomar
                    # un historial estricto. Vamos a asegurar que nunca entren 2 roles iguales.
                    if role == last_role:
                        # Reemplaza el anterior por el nuevo (última intención del usuario)
                        historial[-1] = {"role": role, "content": content}
                    else:
                        historial.append({"role": role, "content": content})
                        last_role = role
    except Exception:
        pass
        
    # Limitar el historial a los últimos 10 mensajes para no saturar el prompt
    historial = historial[-10:]
    
    # Los LLMs locales requieren que el primer mensaje tras el system prompt sea del "user"
    if historial and historial[0]["role"] != "user":
        historial = historial[1:]
    
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(historial)

    try:
        async with httpx.AsyncClient() as client:
            # 1ª Petición: Pasando las herramientas disponibles
            response = await client.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "messages": messages,
                    "tools": ayudante_tools,
                    "temperature": 0.5,
                    "max_tokens": 1000
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            response_msg = data["choices"][0]["message"]
            
            # Obtener tool_calls nativos o por fallback (texto crudo)
            tool_calls = []
            if "tool_calls" in response_msg and response_msg["tool_calls"]:
                tool_calls = response_msg["tool_calls"]
            else:
                content_text = response_msg.get("content", "")
                tool_calls = extract_fallback_tool_calls(content_text)
            
            # Si el modelo decidió llamar a una herramienta (ej. add_alarm)
            if tool_calls:
                # Anexar la decisión del asistente al historial de la conversación actual
                # Forzamos un mensaje fake de assistant con tool_calls si usamos fallback  
                fake_msg = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": tool_calls
                }
                if "tool_calls" in response_msg and response_msg["tool_calls"]:
                    messages.append(response_msg)
                else:
                    messages.append(fake_msg)
                
                print(f"[DEBUG] Executing Tool Calls: {tool_calls}")
                
                resultados_tools = []
                for tc in tool_calls:
                    try:
                        func_obj = tc.get("function", {})
                        fn_name = func_obj.get("name", "")
                        
                        args_raw = func_obj.get("arguments", {})
                        if isinstance(args_raw, str):
                            args = json.loads(args_raw)
                        else:
                            args = args_raw
                    except Exception as e:
                        print(f"[DEBUG] Error parseando argumentos del tool {tc}: {e}")
                        args = {}
                    
                    if fn_name == "schedule_task_checkin":
                        task_desc = args.get("task", "Tarea")
                        mins = args.get("minutes", 30)
                        resultado_tool = schedule_task_checkin_logic(task_desc, mins)
                    elif fn_name == "schedule_specific_time":
                        task_desc = args.get("task", "Alarma")
                        time_str = args.get("time", "12:00")
                        resultado_tool = schedule_specific_time_logic(task_desc, time_str)
                    elif fn_name == "save_task_duration":
                        task_desc = args.get("task", "Tarea")
                        mins = args.get("minutes", 30)
                        resultado_tool = save_task_duration_logic(task_desc, mins)
                    elif fn_name == "get_estimated_duration":
                        task_desc = args.get("task", "Tarea")
                        resultado_tool = get_estimated_duration_logic(task_desc)
                    else:
                        resultado_tool = f"Tool '{fn_name}' no encontrada."
                        
                    resultados_tools.append(f"Tool '{fn_name}' retornó: {resultado_tool}")
                    
                # Para no romper el alternado estricto (User/Assistant) de Jinja en modelos locales,
                # enviamos los resultados de todas las herramientas agrupados en un solo mensaje del "user".
                texto_resultados = "\n".join(resultados_tools)
                messages.append({
                    "role": "user",
                    "content": f"[SYSTEM: Resultado de las herramientas ejecutadas internamente:\n{texto_resultados}]\nBasado en esto, finaliza tu respuesta al usuario."
                })
                
                # 2ª Petición: Que el LLM lea el resultado de la herramienta y devuelva el texto final
                response_final = await client.post(
                    "http://localhost:1234/v1/chat/completions",
                    json={
                        "messages": messages,
                        "temperature": 0.5,
                        "max_tokens": 1000
                    },
                    timeout=120.0
                )
                response_final.raise_for_status()
                data_final = response_final.json()
                return data_final["choices"][0]["message"]["content"]
                
            else:
                # Retorna texto normal sin usar tools
                return response_msg.get("content", "")

    except httpx.HTTPStatusError as exc:
        err_msg = exc.response.text
        print(f"[LLM Error Detalle]: {err_msg}")
        return f"*(Error de conexión con el LLM local en el puerto 1234: HTTPStatusError {exc.response.status_code}. Detalle: {err_msg})*"
    except Exception as e:
        return f"*(Error de conexión con el LLM local en el puerto 1234: {str(e)}. Asegúrate de que LM Studio o el servidor OpenAI-compatible esté corriendo)*"

@app.websocket("/ayudante")
async def websocket_ayudante(websocket: WebSocket):
    await websocket.accept()
    print("[WebSocket] Cliente conectado a /ayudante.")
    
    # Enviar estado inicial del schedule
    await websocket.send_json({
        "type": "schedule_update",
        "data": get_current_schedule()
    })
    
    try:
        # Tarea de fondo: verifica cada minuto la hora actual contra el schedule
        async def check_schedule_loop():
            while True:
                ahora = datetime.now().strftime("%H:%M")
                schedule = get_current_schedule()
                actualizado = False
                
                for item in schedule:
                    if item["status"] == "pending" and item["time"] == ahora:
                        item["status"] = "done"
                        actualizado = True
                        
                        # Avisar al usuario por el chat
                        alerta = f"Es hora de: {item['task']}"
                        append_to_history("assistant", alerta)
                        await websocket.send_json({
                            "type": "chat_message",
                            "data": alerta
                        })
                
                if actualizado:
                    save_schedule(schedule)
                    await websocket.send_json({
                        "type": "schedule_update",
                        "data": schedule
                    })
                    # Despertar al Monitor!
                    asyncio.create_task(trigger_monitor())
                
                # Check cada 30 segundos
                await asyncio.sleep(30)
                
        # Iniciar loop del reloj acoplado a la conexión
        bg_task = asyncio.create_task(check_schedule_loop())

        while True:
            # 1. Espera respuesta del frontend
            raw_data = await websocket.receive_text()
            try:
                # Intentar parsear como JSON para comandos especiales (ej. reset)
                payload = json.loads(raw_data)
                if payload.get("type") == "reset":
                    print("[WebSocket] Solicitud de RESET recibida.")
                    # 1. Truncar historial
                    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
                        f.write("")
                    # 2. Resetear schedule
                    save_schedule([])
                    # 3. Notificar éxito
                    await websocket.send_json({"type": "reset_confirmed"})
                    continue
                else:
                    # Si es JSON pero no es reset, lo tratamos como texto normal por ahora
                    data = raw_data
            except json.JSONDecodeError:
                # Es un mensaje de texto normal
                data = raw_data

            print(f"[Usuario]: {data}")
            append_to_history("user", data)
            
            # 2. Genera respuesta bruta del LLM
            respuesta_limpia = await agent_response(data)
            
            print(f"[Ayudante]: {respuesta_limpia}")
            append_to_history("assistant", respuesta_limpia)
            
            # Envía iteración al frontend
            await websocket.send_json({
                "type": "chat_message",
                "data": respuesta_limpia
            })
            
            # Actualiza el schedule lateral de UI por si hay nuevas alarmas creadas
            await websocket.send_json({
                "type": "schedule_update",
                "data": get_current_schedule()
            })
            
            # 4. Despierta al Monitor Asistente
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
