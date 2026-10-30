# Cuestionario del Laboratorio 07 — RutaSIT Arequipa

1. **Patrón arquitectónico y patrón de diseño.** El monolito modular asíncrono del ADR-001 organiza despliegue y fronteras de módulos. Strategy organiza clases dentro del módulo de monitoreo: `IEstrategiaETA` permite cambiar la fórmula de llegada. Son decisiones de escala distinta.

2. **Strategy y abierto/cerrado.** `ServicioMonitoreoSIT` pide a `FabricaEstrategiasETA` un objeto `IEstrategiaETA` y llama `calcular_eta`. La prueba `test_open_closed_nueva_estrategia_sin_modificar_servicio` registra una nueva clase y consulta el ETA sin editar el servicio. Se añadió una implementación y una entrada en el registro.

3. **Adapter y Decorator.** `GPSOperadorBAdapter` traduce `query_location` (microgrados y cm/s) a `DatosTelemetria` (grados y km/h). `ReintentoGPSDecorator` conserva la interfaz `IProveedorGPS` y agrega intentos ante `TimeoutError`. El primero compatibiliza interfaces; el segundo amplía comportamiento.

4. **State y diagrama de estados.** `Viaje` guarda un `EstadoViajeState`; las subclases permiten solo transiciones del ciclo programado, en ruta, detenido, desviado y finalizado. La clase base eleva `TransicionInvalidaError` por defecto. Esto retira del método de consulta el bloque de condicionales sobre cadenas de estado.

5. **Pruebas de caracterización.** El fixture parametrizado ejecuta las mismas expectativas sobre `antes.servicio` y `servicio`: retorno, excepciones, eventos y reintentos. En E4, la prueba `test_decorator_reintentos_gps_sobre_adaptador` detectó que el adaptador aún reintentaba internamente (`assert 1 == 3`); se retiró ese bucle para que el decorador asumiera la responsabilidad. Hoy aprueban 28 ejecuciones compartidas.

6. **Patrón rechazado.** Se descartó Singleton porque un servicio global con proveedores mutables dificulta aislar las pruebas; también Command porque ETA es una lectura sin deshacer ni encolamiento. “Patternitis” es añadir clases y patrones sin un olor o beneficio verificable, elevando el costo de comprensión.

7. **Salida del LLM.** `MockLLMAdapter` simula texto que puede ser incorrecto. `GuardrailConsistenciaTelemetria` rechaza averías inventadas cuando el dato indica tráfico; `GuardrailLongitudYTono` bloquea textos de más de 250 caracteres y expresiones alarmistas. La prueba de alucinación y la de tono verifican ese límite, pero no garantizan detectar cualquier falsedad.

8. **Balance de métricas.** La consulta ETA baja de D (25) a A (3), y la suite actual aprueba 40 pruebas. El servicio sube de 124 a 152 SLOC; los siete módulos posteriores suman 526 SLOC. El refactor se justifica si se prevén más operadores, fórmulas y reglas de notificación; para una variante estable, la versión inicial sería más corta.
