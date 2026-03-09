# Project Log - Ayudante

### 📝 Registro: [v1.0] - Inicialización del Workspace y Corrección de Alucinaciones
- **Problema**: El asistente estaba utilizando ejemplos literales del prompt ("8:45", "Hassan") como argumentos por defecto en las herramientas JSON, y además su arquitectura estaba ensuciando el `project_status.md` de la raíz del servidor principal.
- **Causa**: Limitación cognitiva fundamental de los modelos LLMs locales pequeños. Tienen extrema dificultad para entender plantillas abstractas y no distinguen entre un ejemplo instructivo y un comando real. 
- **Solución**: Se abstrajeron los ejemplos en `asistente_personal.md` cambiándolos a `XX:XX` y `Acción a realizar`, para provocar un fallo visual evidente en el modelo si intenta copiarlo y forzarlo a pensar en sus propios argumentos. Además se organizó su arquitectura separando su documentacion en `ayudante/project_status.md` y `ayudante/project_log.md`.

### 📝 Registro: [v1.1] - Corrección de Dependencias Faltantes (httpx, pydantic, websockets)
- **Problema**: El servidor de WebSockets en `api_websocket.py` arrojaba advertencias por falta de librería de soporte (`websockets`). Además, se utilizaban `pydantic` y `httpx` sin estar explícitamente en el `requirements.txt`.
- **Causa**: Omisión durante la implementación del ecosistema del Ayudante.
- **Solución**: Se añadieron las dependencias al `requirements.txt` de la raíz (compartido) y se actualizó la documentación del Ayudante.

### 📝 Registro: [v1.2] - Implementación de Botón Reset y Limpieza de Alertas
- **Problema**: El chat no podía reiniciarse sin borrar manualmente los archivos. Además, las notificaciones del navegador y los prefijos de sistema eran molestos.
- **Causa**: Falta de funcionalidad de gestión de estado de sesión.
- **Solución**: Se añadió un botón "Reset" en el frontend que envía un comando al backend para truncar `historial_global.jsonl` y vaciar `schedule.json`. Se eliminaron las notificaciones `Notification` de React y los prefijos de alerta del sistema en los mensajes automáticos.

### 📝 Registro: [v1.3] - Streaming de Respuestas y Badge de Estado (Thinking)
- **Problema**: Las respuestas del asistente tardaban demasiado en aparecer (bloqueo por procesamiento completo) y el usuario no sabía qué estaba haciendo el servidor (si pensaba o ejecutaba herramientas).
- **Causa**: Procesamiento síncrono en la comunicación WebSocket.
- **Solución**: Se implementó streaming SSE desde el LLM local manejado por `httpx.stream`. El backend ahora envía mensajes tipo `thinking` (con estados como "Consultando cerebro..." o "Agendando...") y `chat_chunk`. El frontend renderiza un badge animado de estado y muestra el texto palabra por palabra.

### 📝 Registro: [v1.3.4] - Blindaje Anti-JSON en Streaming
- **Problema**: A pesar del refactor en dos fases, el modelo seguía alucinando bloques JSON en la respuesta final.
- **Causa**: Las instrucciones del sistema en Phase 2 a veces triggereaban comportamientos técnicos en el LLM.
- **Solución**: 
    - Se añadieron `stop tokens` (` ```json ` y ` {"name" `) a la petición de Phase 2 para cortar la alucinación antes de que empiece.
    - Se implementó un filtro de chunks en tiempo real para descartar cualquier texto que contenga fragmentos de código JSON si el stop token falla.
    - Se refinó el prompt de Phase 2 para ser extremadamente estricto y humano.
### 📝 Registro: [v1.4.0] - Restauración de Notificaciones del Navegador
- **Problema**: Las notificaciones del sistema se habían desactivado inadvertidamente en la v1.2, impidiendo que el usuario viera los avisos del schedule fuera del chat.
- **Causa**: Error de interpretación sobre el alcance de la limpieza de "alerts".
- **Solución**: Se re-implementó la lógica de `Notification` en el frontend, añadiendo solicitud de permisos al cargar y disparadores automáticos en la recepción de mensajes del asistente y alertas de schedule.

### 📝 Registro: [v1.5.0] - Implementación de Seguimiento Proactivo y Timestamps
- **Problema**: El asistente era puramente reactivo y dependía de la iniciativa del usuario o del schedule rígido. Se necesitaba un control más dinámico sobre el estado del usuario.
- **Causa**: Limitación en el diseño inicial del loop de eventos del WebSocket.
- **Solución**: 
    - Se creó `background_monitor_loop` en el backend para vigilar la última interacción del usuario.
    - Lógica de escalado: El asistente pregunta cada 5m, 10m, 20m... hasta 4h si el usuario no responde.
    - Se añadieron Timestamps visibles en el frontend para cumplir con el requisito de control horario exacto.

