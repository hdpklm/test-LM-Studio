# Historial de Cambios del Proyecto

### 📝 Registro: [v1.0] - Inicialización y Descripción de PlanesDeTranajo
- **Problema**: Hacía falta crear los documentos base del proyecto (`project_status.md` y `project_log.md`) y registrar la descripción de la carpeta de agentes.
- **Causa**: Inicialización requerida por las reglas del sistema y petición del usuario de documentar el propósito de la carpeta `PlanesDeTranajo`.
- **Solución**: Se crearon los archivos de seguimiento. Se ha añadido la descripción indicando que `PlanesDeTranajo` almacenará descripciones sin código de roles para implementar ideas en los agentes de forma progresiva.

### 📝 Registro: [v1.1] - Documentación de carpeta SysPro
- **Problema**: Faltaba registrar la carpeta donde se almacenan los system prompts de los agentes.
- **Causa**: Petición del usuario para documentar la nueva carpeta `SysPro`.
- **Solución**: Se añadió la descripción de la carpeta `SysPro` a `project_status.md` indicando que guardará los prompts de sistema de cada agente.

### 📝 Registro: [v1.2] - Diseño del Agente de Viajes Completo
- **Problema**: El usuario solicitó investigar y diseñar el plan para crear un agente de planificación de viajes completo.
- **Causa**: Inicialización de un nuevo rol de agente (Agente de Viajes) para definir el uso de múltiples herramientas en cadena (vuelos, hoteles, puntos de interés).
- **Solución**: Se ha diseñado y redactado la propuesta en `PlanesDeTranajo/gemini.md` documentando el flujo lógico, módulos requeridos (vuelos, alojamiento, transporte, clima y actividades) y el modo de interactuar con el usuario. Se actualiza la versión a v1.2.

### 📝 Registro: [v1.3] - Normativa de nombres de archivo de agentes
- **Problema**: La especificación de los agentes no debe ir en `gemini.md` ya que este archivo se usa como comunicación/borrador global, sino que cada agente debe tener un nombre de archivo descriptivo (ej. `agente_viajes.md`).
- **Causa**: Corrección en las directrices del usuario: asignar a cada archivo un título resumido sobre el agente.
- **Solución**: Se reasignó el contenido a `PlanesDeTranajo/agente_viajes.md` y se actualizó `project_status.md`. Se actualiza la versión a v1.3.

### 📝 Registro: [v1.4] - Diseño del Agente Creador de Python
- **Problema**: Necesidad de establecer un rol especializado en la creación de proyectos Python sólidos que eviten la confusión arquitectónica de los "scripts monstruo".
- **Causa**: Petición de un agente que construya código bajo estrictas reglas de responsabilidad única, prohibiendo variables globales estado y modularizando las funciones por su dominio.
- **Solución**: Se creó `PlanesDeTranajo/agente_python_arquitecto.md` documentando las restricciones (funciones aisladas con entrada/salida puras, agrupación mediante archivos por dominio temático, y exclusión de globales mutables en favor de archivos `.env`). Se actualiza `project_status.md` a v1.4.

### 📝 Registro: [v1.5] - Versiones "mini" para accesibilidad
- **Problema**: El formato extenso y con mucho texto dificulta la lectura visual, especialmente para personas con dislexia.
- **Causa**: Limitación cognitiva / accesibilidad. El usuario solicitó resúmenes de no más de 20 palabras por idea.
- **Solución**: Se han generado copias resumidas `.mini.md` conservando los originales intactos. Se ha subido la versión de `project_status.md` a v1.5.

### 📝 Registro: [v1.6] - Estandarización de Workflow de Agentes y System Prompts
- **Problema**: Se requería asentar una metodología estricta para no olvidar generar las diferentes vistas de información y los ejecutables de los agentes.
- **Causa**: Petición explícita del usuario para registrar una regla permanente para todos los agentes a futuro.
- **Solución**: Se añadió la "REGLA GLOBAL GENÉRICA PARA AGENTES" a `project_status.md`, fijando el flujo obligatorio a 3 pasos: Archivo diseño normal, Archivo diseño mini, y System Prompt en SysPro. Se han generado seguidamente  los system prompts correspondientes a Viajes y Arquitecto Python basándose en sus `md` normales. Se sube a v1.6.

### 📝 Registro: [v1.7] - Corrección del Flujo de Agentes (Mini-First)
- **Problema**: El flujo documentado en v1.6 asumía que el agente generaba primero el archivo normal y no incluía pausas de revisión ni el proceso de modificación.
- **Causa**: Aclaración del usuario: el archivo de entrada/modificación principal es el `.mini.md`, y se requiere revisión humana antes de pasar al prompt de sistema.
- **Solución**: Se ha reescrito la regla global en `project_status.md` (v1.7). Ahora especifica que toda idea/modificación empieza en el `.mini.md` (revisado por el usuario), luego el agente expande al `.md` normal, espera revisión y, por último, genera el `SysPro/prompt_...md`.

### 📝 Registro: [v1.8] - Creación Web App Claude-like y Backend FastAPI
- **Problema**: Falta de una interfaz de usuario cómoda y robusta para conversar con LM-Studio, además de no tener capacidad para gestionar historial, archivos subidos (imágenes/audio) o interpretación de React.
- **Causa**: Petición del usuario para construir una aplicación React local en `react-web` con Drawers interactivos (izquierdo y derecho) similares a Claude.
- **Solución**: Refactor de `test-LM-Studio/main.py` de una consola interactiva a un servidor FastAPI. Creación inicial de la estructura Pnpm + Vite + React + Tailwind en la carpeta `react-web`.

# Backup

### [v1.8] main()` de test-LM-Studio/main.py (Bucle Interactivo Antiguo)
- **Función anterior**: `main()` ejecutaba un bucle `while True` en consola usando `input()`, procesando llamadas a herramientas secuencialmente y deteniéndose con 'quit'.
- **Razón del cambio**: Incompatible con una arquitectura web asíncrona donde el frontend (React) controla la entrada y salida, requiriéndose exponer la funcionalidad vía HTTP.
- **Nueva versión**: Rutas FastAPI (ej. `POST /api/chat`) reemplazarán la interacción por terminal.

### [v1.9] `system_prompt` de test-LM-Studio/main.py (Prompt de Tool Call forzado alucinante)
- **Lógica anterior**: Forzaba a devolver arrays JSON con la clave `url`, `title`, `desc`.
- **Razón del cambio**: Confundía al modelo, que devolvía ese JSON ignorando la consulta real del usuario (ej. crear código de interfaces).
- **Nueva versión**: Simple, se ha indicado al modelo que responda directamente al usuario si no necesita usar las tools y se ha retirado la estructura JSON forzada.

### 📝 Registro: [v1.9] - Login React, Fix 422 y Tests
- **Problema**: Request 422 al chatear, falta de página Login, y test scripts mal ubicados rompiendo la regla de tests.
- **Causa**: El `history_id` no era opcional en el backend FastAPI y el archivo `test_chat.py` estaba en la raíz temporaria en vez de la carpeta de test.
- **Solución**: Se ha corregido el modelo `ChatRequest` añadiendo `Optional[str]` a `history_id`. Se ha implementado `LoginPage.jsx` en React integrada con React Router en `/login`. Se ha movido `test_chat.py` a la carpeta restrictiva requerida `gemini_test/backend/`.

### 📝 Registro: [v1.10] - Fix Tool Calls (Evitar JSON alucinados)
- **Problema**: El asistente respondía con bloques JSON de búsqueda simulados en lugar de invocar herramientas o contestar a preguntas de programación.
- **Causa**: El `system_prompt` obligaba explícitamente a usar un formato JSON para resultados de búsqueda, sesgando fuertemente al LLM local a devolver siempre ese bloque.
- **Solución**: Se ha reemplazado el prompt en `main.py` por instrucciones claras que separan la conversación normal del uso estricto de herramientas, retirando la imposición de JSON.

