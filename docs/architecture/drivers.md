# Drivers arquitectónicos — RutaSIT Arequipa

## 1. Requisitos funcionales clave

| ID | Requisito | Actor | Prioridad |
| :--- | :--- | :--- | :--- |
| **RF-01** | Ingesta periódica de telemetría GPS (latitud, longitud, velocidad, rumbo, timestamp e identificador de bus) enviada cada 10 segundos por cada unidad de transporte. | Bus (GPS) | Alta |
| **RF-02** | Visualización en tiempo real sobre mapa interactivo de la ubicación y desplazamiento de los buses que operan en una ruta seleccionada. | Pasajero / Operador | Alta |
| **RF-03** | Estimación dinámica y visualización del tiempo estimado de llegada (ETA) de los próximos buses hacia el paradero consultado por el usuario. | Pasajero | Alta |
| **RF-04** | Detección automatizada de desvíos de ruta (desplazamiento mayor a 100 metros fuera del corredor oficial) y congestión vial, emitiendo alertas instantáneas. | Operador SIT / Sistema | Media |
| **RF-05** | Panel de supervisión de flota en tiempo real con monitoreo de frecuencias de paso, buses activos e indicadores de retraso. | Operador SIT | Alta |
| **RF-06** | Consulta del catálogo de rutas, paraderos autorizados, frecuencias programadas y tarifas vigentes del Sistema Integrado de Transporte. | Pasajero | Media |

---

## 2. Atributos de calidad (ordenados por prioridad)

1. **Rendimiento en tiempo real (Latencia de procesamiento y visualización):** Crítico para el transporte urbano; una flota de 300 buses genera un flujo continuo de telemetría que debe reflejarse en paraderos y pantallas de pasajeros en menos de 15 segundos para mantener la predictibilidad del servicio.
2. **Disponibilidad y Tolerancia a Fallos:** Esencial para asegurar la continuidad del servicio de monitoreo y consulta pública incluso frente a pérdidas temporales de señal celular en las unidades o caídas de conectividad móvil en la ciudad.
3. **Modificabilidad y Extensibilidad:** Fundamental para permitir agregar nuevas troncales o alimentadoras del SIT, alterar geometrías de paraderos o ajustar los algoritmos de ETA sin reconstruir el módulo de ingesta ni alterar la base de datos.
4. **Eficiencia de Costos y Recursos:** Imprescindible para garantizar que todo el sistema del MVP opere de forma fluida y estable dentro de los límites de un único servidor en la nube de bajo costo sin degradar el tiempo de respuesta.

---

## 3. Restricciones

| ID | Tipo | Restricción |
| :--- | :--- | :--- |
| **R-01** | Plazo | MVP listo y puesto en producción en un plazo estricto de **1 mes** (4 semanas calendario). |
| **R-02** | Equipo | Equipo reducido compuesto por **2 desarrolladores** (Anderson Arce Valencia y Freddy Carlos Ccamaqque) con dominio en Python (FastAPI/Django), JavaScript/TypeScript (React), SQL y bases de datos relacionales. |
| **R-03** | Presupuesto | Presupuesto sumamente ajustado; la infraestructura debe sustentarse en **un único VPS en la nube** de bajo costo (ej. 2-4 vCPU, 4-8 GB RAM, costo estimado $\le 12$ USD/mes) sin costos recurrentes por licencias de software propietario. |
| **R-04** | Tecnología y Conectividad | Los dispositivos embarcados transmiten datos sobre enlaces celulares 3G/4G sujetos a pérdida temporal de señal; la visualización cartográfica debe emplear herramientas de código abierto (OpenStreetMap y Leaflet) para evitar los costos comerciales de la API de Google Maps. |
| **R-05** | Normativa | Cumplimiento de la **Ley N.° 29733** (Ley de Protección de Datos Personales del Perú) para resguardo de perfiles y sesiones de operadores, así como alineamiento a las especificaciones de ruta de la Gerencia de Transportes de la Municipalidad Provincial de Arequipa (MPA). |

---

## 4. Escenarios de atributos de calidad

| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **QA-01** | **Rendimiento en tiempo real** *(Atributo crítico)* | 300 buses del SIT transmitiendo simultáneamente en operación. | Envío continuo de telemetría GPS a razón de 1 trama cada 10 s por unidad ($\approx 30$ peticiones/s continuas). | Hora punta matutina (07:00 a 08:30 a. m.), condiciones normales de tráfico y 1500 pasajeros consultando la app. | Módulo de Ingesta GPS y Módulo de Estimación de ETA. | El sistema recibe las tramas, actualiza el estado en caché en memoria (Redis), recalcula el ETA hacia los paraderos y emite la actualización a los clientes conectados vía WebSocket. | • p95 del tiempo de propagación entre emisión del bus y visualización en la interfaz web $\le 15$ s.<br>• Tasa de pérdida de tramas de telemetría $\le 0.1\%$.<br>• Utilización de CPU del servidor $\le 75\%$. |
| **QA-02** | **Disponibilidad y Resiliencia** | Dispositivo GPS embarcado en bus de ruta alimentadora. | Corte intermitente de la conexión celular móvil (3G/4G) durante un lapso de 5 minutos al atravesar zonas de sombra en Arequipa. | Operación regular en ruta con señal celular inestable. | Módulo de Ingesta GPS y protocolo de enlace del bus. | El hardware embarcado retiene las tramas en búfer local; al restablecer la cobertura, envía la ráfaga de 30 tramas acumuladas. El módulo ingiere el lote sin saturar el procesamiento concurrente ni retrasar a los demás buses. | • 0 tramas descartadas tras la reconexión.<br>• Procesamiento y reanudación del lote acumulado en $\le 3$ s.<br>• Disponibilidad del servicio central $\ge 99.5\%$. |
| **QA-03** | **Modificabilidad** | Administrador de operaciones del SIT / Desarrollador. | Solicitud de incorporación de una nueva ruta alimentadora del SIT con 20 nuevos paraderos y geocercas de desvío asociadas. | Entorno de mantenimiento/producción sin detener la operación de los buses en circulación. | Módulo de Catálogo de Rutas y capas espaciales (PostGIS). | Se registran las nuevas entidades espaciales y trazados mediante endpoints administrativos; el motor espacial las indexa sin reiniciar los servicios de ingesta ni desconectar a los usuarios. | • Tiempo de esfuerzo de configuración $\le 1.5$ días-persona.<br>• Tiempo de indisponibilidad del sistema $= 0$ minutos (zero-downtime). |
