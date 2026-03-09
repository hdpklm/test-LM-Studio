# Project Log - Ayudante

### 📝 Registro: [v1.0] - Inicialización del Workspace y Corrección de Alucinaciones
- **Problema**: El asistente estaba utilizando ejemplos literales del prompt ("8:45", "Hassan") como argumentos por defecto en las herramientas JSON, y además su arquitectura estaba ensuciando el `project_status.md` de la raíz del servidor principal.
- **Causa**: Limitación cognitiva fundamental de los modelos LLMs locales pequeños. Tienen extrema dificultad para entender plantillas abstractas y no distinguen entre un ejemplo instructivo y un comando real. 
- **Solución**: Se abstrajeron los ejemplos en `asistente_personal.md` cambiándolos a `XX:XX` y `Acción a realizar`, para provocar un fallo visual evidente en el modelo si intenta copiarlo y forzarlo a pensar en sus propios argumentos. Además se organizó su arquitectura separando su documentacion en `ayudante/project_status.md` y `ayudante/project_log.md`.
