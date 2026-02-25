# Agente de Viajes Completo (Diseño y Análisis)

## 🎯 Objetivo Principal
Actuar como un planificador de viajes experto y completamente autónomo. El agente debe ser capaz de investigar, comparar, cotizar y estructurar itinerarios completos adaptados a las fechas, presupuesto y gustos del usuario final.

## 🛠️ Herramientas Necesarias (Integraciones de API a Futuro)
Para que el agente pueda tomar decisiones viables e informadas de manera dinámica, requerirá tener acceso a herramientas concretas en su código de backend:

1. **Búsqueda de Vuelos:**
	- **Módulo**: `buscar_vuelos(origen, destino, inicio, fin, presupuesto, pax)`
	- **APIs Posibles**: Amadeus, Skyscanner API, Google Flights API.
	- *Misión*: Localizar rutas con mejor relación calidad/precio, controlar escalas y costos de equipaje.

2. **Búsqueda de Alojamiento:**
	- **Módulo**: `buscar_hoteles(ubicacion, check_in, check_out, huespedes, presupuesto)`
	- **APIs Posibles**: Booking.com API, Expedia, Airbnb API.
	- *Misión*: Identificar el alojamiento central con respecto a los puntos de interés que elegirá más adelante.

3. **Transporte Local y Traslados:**
	- **Módulo**: `buscar_transporte(punto_a, punto_b, modo)`
	- **APIs Posibles**: Google Maps Routes API, Rome2Rio, Uber.
	- *Misión*: Estimar costos y tiempos de manera realista del punto A al punto B.

4. **Clima y Predicciones:**
	- **Módulo**: `obtener_clima(ubicacion, fechas)`
	- **APIs Posibles**: OpenWeatherMap API o WeatherAPI.
	- *Misión*: Modificar o sugerir actividades basadas en clima (ej. sugerir museos si indica lluvia torrencial).

5. **Atracciones, Sitios y Restaurantes:**
	- **Módulo**: `buscar_actividades(ubicacion, intereses)`
	- **APIs Posibles**: Google Places API, TripAdvisor, Foursquare.
	- *Misión*: Recomendar sitios basados en perfil de usuario (ej: familiar, parejas, mochileros).

## 🧠 Flujo de Trabajo del Agente (Pipeline)

1. **Recolección de Preferencias (Profiling Interactivo):**
	- El agente le hace un pequeño cuestionario al usuario.
	- ¿Destino o clima general?
	- ¿Suelto de dinero o ajustado?
	- ¿Viaje cultural, exótico, descanso, fiesta?

2. **Cotización y Verificación Logística:**
	- Ejecuta llamada paralela de vuelo + alojamiento básico para evaluar viabilidad financiera.
	- Presenta escenario inicial al usuario ("He visto que el pasaje y el hotel base salen a $X en total de tu presupuesto, ¿estás de acuerdo?").

3. **Arquitectura del Itinerario Diario (Enrutamiento Lógico):**
	- Selecciona un hotel estratégico y de ahí distribuye las actividades aglutinando por proximidad.
	- Se asegura de que no planifique dos puntos a 2 horas de distancia en la misma mañana.
	- Calcula las comidas cerca de los sitios de esa ruta.

4. **Cierre y Entrega Final:**
	- Tabla cronológica Markdown que incluye horarios aproximados.
	- Estimación de costes hiper detallada.
	- El agente queda a la espera de ajustes del tipo *"no me gusta el restaurante del martes, cámbialo por sushi"*.

## 🔑 Concepto para Prompts (`SysPro`)
Este concepto alimentará un próximo prompt base.
**Regla Dorada**: El agente tiene STRICTAMENTE PROHIBIDO alucinar precios y datos de los transportes y hoteles. Todo presupuesto generado tiene que venir sacado empíricamente a través de la llamadas de las funciones implementadas o, en su defecto, avisará al usuario que realiza *"Estimaciones aproximadas estándar"*.
