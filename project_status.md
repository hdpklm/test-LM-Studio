# Estado del Proyecto (v1.10)

## Main Project

### 🚨 REGLA GLOBAL GENÉRICA PARA AGENTES (Creación y Modificación)
Para crear o modificar cualquier agente, el flujo de trabajo es el siguiente paso a paso:
1. **Inicio por el "Mini"**: Todo comienza en `PlanesDeTranajo/[nombre_agente].mini.md`. Si hay una nueva idea, se crea este resumen hiper-comprimido primero. Si se quiere modificar un agente, el usuario modifica este archivo `.mini.md`.
2. **Expansión al "Normal"**: Basado en el archivo mini, el agente desarrolla y actualiza la versión completa y detallada en `PlanesDeTranajo/[nombre_agente].md`.
3. **Revisión del Usuario**: El agente se detiene aquí y espera que el usuario revise y apruebe el archivo normal extendido.
4. **Generación del "SysPro"**: Solo tras la confirmación explícita del usuario, el agente generará o actualizará el System Prompt final en `SysPro/prompt_[nombre_agente].md` basándose en el archivo normal.

### Sección de archivos de código

- **`test-LM-Studio/main.py`**
	- Descripción: Servidor FastAPI Backend para el chat (v1.10).
	- Endpoints:
		- `POST /api/chat`: Parámetros en body JSON. Devuelve: `JSON` con la respuesta del LLM y tool calls.
		- `GET /api/history`: Devuelve: `JSON` array con la lista de conversaciones.
		- `GET /api/history/{id}`: Devuelve: `JSON` de una conversación específica.
		- `POST /api/upload`: Parámetros `FormData` con archivo. Devuelve: `JSON` estado.
		- `GET /api/generated`: Devuelve: `JSON` lista de archivos de versiones.
		- `GET /api/download/{filename}`: Retorna enlace de descarga para el archivo en Frontend.
	- Funciones Principales (Herramientas):
		- `search_google_and_print(query)`: Parámetro: `query` (string). Devuelve: `string` (JSON). Hace la búsqueda en google.
		- `read_web_page(url)`: Parámetro: `url` (string). Devuelve: `string`. Extrae el contenido y lo convierte a texto.
		- `deep_thinking(prompt)`: Parámetro: `prompt` (string). Devuelve: `string`. Realiza pensamientos en profundidad agregando múltiples modelos/llamadas.

## Futuros Desarrollos / Agentes

### Sección de directorios
- **`test-LM-Studio/PlanesDeTranajo/`**
	- **Propósito**: Esta carpeta es para almacenar roles que tiene que ejecutar el agente. En ella residirá una descripción del agente en cada archivo, pero sin contener código. Su función es servir de espacio para anotar todas las ideas del usuario e irlas implementando poco a poco en el comportamiento de los agentes.
	- **`agente_viajes.md`**: Plan de diseño y conceptualización del Agente de Viajes Completo.
	- **`agente_viajes.mini.md`**: Versión corta y directa para accesibilidad visual (Agente de Viajes).
	- **`agente_python_arquitecto.md`**: Plan de diseño para el Agente Experto en Python enfocado en funciones puras y responsabilidad única.
	- **`agente_python_arquitecto.mini.md`**: Versión corta y directa (Agente Arquitecto Python).
- **`test-LM-Studio/SysPro/`**
	- **Propósito**: Esta carpeta almacena los system prompts que tiene que utilizar cada agente.
- **`test-LM-Studio/gemini_test/`**
	- **Propósito**: Directorio exclusivo para almacenar todos los archivos de prueba generados durante el desarrollo, organizados por sección (e.g. `backend`, `frontend`).
	- Archivos actuales: `backend/test_chat.py`.
