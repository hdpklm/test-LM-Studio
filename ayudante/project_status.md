# Estado del Proyecto: Ayudante (v1.0)

## Propósito
Ecosistema interactivo de asistencia personal regido por los objetivos (`objetivos.json`) del usuario. Contiene el servidor en tiempo real (`api_websocket.py`) y promueve auto-mejora por medio del Monitor y su memoria.

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
