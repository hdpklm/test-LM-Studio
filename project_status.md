# Estado del Proyecto

## Main Project

### Sección de archivos de código

- **`test-LM-Studio/main.py`**
	- `search_google_and_print(query)`: Parámetro: `query` (string). Devuelve: `string` (JSON). Hace la búsqueda en google.
	- `read_web_page(url)`: Parámetro: `url` (string). Devuelve: `string`. Extrae el contenido y lo convierte a texto.
	- `main()`: Parámetros: ninguno. Devuelve: `None`. Bucle principal interactivo con LLM (LM-Studio).

## Futuros Desarrollos / Agentes

### Sección de directorios
- **`test-LM-Studio/PlanesDeTranajo/`**
	- **Propósito**: Esta carpeta es para almacenar roles que tiene que ejecutar el agente. En ella residirá una descripción del agente en cada archivo, pero sin contener código. Su función es servir de espacio para anotar todas las ideas del usuario e irlas implementando poco a poco en el comportamiento de los agentes.
- **`test-LM-Studio/SysPro/`**
	- **Propósito**: Esta carpeta almacena los system prompts que tiene que utilizar cada agente.
