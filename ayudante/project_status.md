# Estado del Proyecto: Ayudante (v1.4)

## Propósito
Ecosistema interactivo de asistencia personal regido por los objetivos (`objetivos.json`) del usuario. Contiene el servidor en tiempo real (`api_websocket.py`) y promueve auto-mejora por medio del Monitor y su memoria.

## Dependencias (requirements.txt)
- **`pydantic`**: Gestión de modelos de datos (utilizado en validación).
- **`httpx`**: Cliente HTTP asíncrono para comunicaciones con el LLM local.
- **`websockets`**: Librería de soporte para el servidor WebSocket de `uvicorn`.

## Arquitectura

### 🚨 REGLA GLOBAL GENÉRICA PARA AGENTES (Creación y Modificación)
Para crear o modificar cualquier agente, el flujo de trabajo es el siguiente paso a paso:
1. **Inicio por el "Mini"**: Todo comienza en `PlanesDeTranajo/[nombre_agente].mini.md`. Si hay una nueva idea, se crea este resumen hiper-comprimido primero. Si se quiere modificar un agente, el usuario modifica este archivo `.mini.md`.
2. **Expansión al "Normal"**: Basado en el archivo mini, el agente desarrolla y actualiza la versión completa y detallada en `PlanesDeTranajo/[nombre_agente].md`.
3. **Revisión del Usuario**: El agente se detiene aquí y espera que el usuario revise y apruebe el archivo normal extendido.
4. **Generación del "SysPro"**: Solo tras la confirmación explícita del usuario, el agente generará o actualizará el System Prompt final en `SysPro/prompt_[nombre_agente].md` basándose en el archivo normal.

### Archivos
- **`api_websocket.py`**: API en WebSocket que se encarga del servidor de notificaciones/chat y ejecuta las Herramientas (Tools).
- **`asistente_personal.md`**: Agente conversacional y gestionador de tiempo/rutinas. Llama a tools con JSON plano bloqueado.
- **`monitor_asistente.md`**: Agente metacognitivo que analiza y actualiza el prompt del asistente de acuerdo al historial global.
- **`decisiones_monitor.md`**: Rastreador de fallos y éxitos utilizados por el Monitor para evitar repeticiones.
- **`objetivos.json`**: Metas y rutinas dadas por el usuario.
- **`schedule.json`**: Temporizadores y alarmas activas (`schedule_task_checkin`, `schedule_specific_time`).
- **`task_durations.json`**: Tiempos históricos guardados de las tareas (`save_task_duration`, `get_estimated_duration`).
- **`historial_global.jsonl`**: Historial de chat en formato JSON Lines. Alternado estricto `user`/`assistant`.

### Funciones Principales (Herramientas) en `api_websocket.py`
- `schedule_task_checkin`: Agenda timer relativo.
- `schedule_specific_time`: Agenda alarma absoluta (hora exacta).
- `save_task_duration`: Registra cuantas horas/minutos tomó acabar una tarea.
- `get_estimated_duration`: Consulta el promedio de tiempo que toma completar la tarea.
- `extract_fallback_tool_calls`: Parseador extra regex que intercepta las alucinaciones JSON y Diccionarios Planos generados por el LLM en texto local.
- **Reset Functionality**: El servidor permite limpiar el historial y el schedule mediante un comando JSON tipo `reset`.
- **Streaming & Thinking Badge**: Soporte completo para respuestas en tiempo real y estados visuales ("Consultando cerebro...", "Agendando recordatorio...", etc.).
- **Detección de Tools en 2 Fases**: Arquitectura que separa la decisión de usar herramientas (interna) de la respuesta final al usuario (streaming), eliminando fugas de JSON técnico.
- **Notificaciones del Navegador**: El sistema solicita permisos y lanza alertas nativas para avisos del schedule y mensajes del asistente.

### Archivos de código (Detalle)
- **`api_websocket.py`**:
    - `agent_response`: Refactorizado a 2 fases (Detección silenciosa -> Respuesta final con streaming filtrado).
    - `thinking`: Mensaje con el estado actual del asistente.
    - `chat_chunk`: Fragmento de streaming del LLM (ahora con filtrado anti-JSON).
- **`AyudanteChat.jsx`**:
    - `showNotification`: Utilidad para lanzar notificaciones del sistema en mensajes y alertas de schedule.
    - `onmessage`: Maneja el flujo de streaming, badges y notificaciones.
