# ADR-001: Adoptar un monolito modular asíncrono con búfer en Redis para el MVP de RutaSIT Arequipa

- Estado: Aceptado
- Fecha: 2026-10-04
- Decisores: Arce Valencia Anderson Lino y Carlos Ccamaqque Wilson Freddy (Grupo 06)

## Contexto
RutaSIT Arequipa muestra en un mapa la posición de los buses del SIT, calcula el tiempo estimado de llegada (ETA) a cada paradero y alerta desvíos de ruta (RF-01 a RF-06). El atributo crítico es el rendimiento en tiempo real (QA-01): 300 buses envían una trama GPS cada 10 s, lo que da unas 30 peticiones/s continuas, y el cambio debe verse en la pantalla del pasajero en 15 s o menos (p95), con unos 1500 pasajeros conectados en hora punta.

Las restricciones son fuertes: el MVP debe estar en producción en 1 mes (R-01), el equipo son 2 desarrolladores con experiencia en Python y SQL (R-02) y todo debe correr en un único VPS de bajo costo, de unos 12 USD/mes (R-03). Además, los buses pierden señal celular por momentos y luego reenvían lo acumulado (R-04, QA-02), y se deben poder agregar rutas sin detener el servicio (QA-03).

## Alternativas consideradas
Se compararon tres estilos con una matriz ponderada de 5 criterios (rendimiento 25 %, tiempo de entrega 25 %, costo en 1 VPS 20 %, simplicidad operativa 15 %, modificabilidad 15 %):

1. **Monolito en capas con Django y PostgreSQL (3,60 / 5).** Es el más rápido de arrancar para un equipo que conoce Django. La carga de ingesta (30 req/s) sí la soporta con pocos workers; su debilidad real es que no tiene empuje en tiempo real nativo: el mapa dependería de polling (1500 pasajeros cada 5 s ≈ 300 req/s adicionales) o de añadir Django Channels, y el cálculo de ETA quedaría dentro del ciclo de petición.
2. **Microservicios con FastAPI, RabbitMQ y una base por servicio (2,35 / 5).** Aísla bien la ingesta, pero 4 servicios, un broker y varias bases no caben con holgura en un solo VPS y exigen a 2 personas montar contratos, despliegues y trazas distribuidas en 4 semanas.
3. **Monolito modular asíncrono con FastAPI, Redis y PostgreSQL/PostGIS (4,45 / 5).** Un solo despliegue con módulos de dominio separados, WebSockets nativos (ASGI) y Redis como búfer y caché del último estado.

También se evaluó la variante "Django clásico + ingestor ligero" que propuso la crítica adversarial; se descartó porque mantiene dos marcos web y dos modelos de despliegue para el mismo equipo de 2 personas.

## Decisión
Usaremos un **monolito modular asíncrono** en Python con FastAPI, organizado en 5 módulos de dominio (Ingesta GPS, ETA y Geocercas, Notificaciones en tiempo real, Catálogo SIT y Supervisión de flota). Cada módulo expone solo una fachada pública (`service.py`) y nadie importa el interior de otro módulo.

Para cubrir los riesgos que salieron del análisis del abogado del diablo, aplicaremos estas tácticas desde el MVP:

- El endpoint de ingesta solo valida la trama y la agrega a un **Redis Stream** (`XADD`); no calcula nada en la petición.
- Un **proceso worker separado** consume el stream, hace los cálculos geométricos de ETA y desvíos y actualiza el último estado de cada bus en Redis, de modo que el cómputo pesado no bloquea el event loop de la API.
- Otro worker escribe el histórico en PostgreSQL **por lotes cada 5 s**.
- Habrá un endpoint `POST /telemetry/batch` para recibir de una vez las tramas acumuladas tras un corte de señal (QA-02).
- Redis tendrá **persistencia AOF** y, al arrancar, la aplicación **rehidrata** el último estado conocido desde PostgreSQL.
- `import-linter` en la CI vigilará que los módulos no se importen entre sí por fuera de su fachada.

Elegimos FastAPI en lugar de Django aunque el problema se planteó primero pensando en Django: los dos son Python, pero FastAPI trae WebSockets y `asyncio` sin capas adicionales, que es justo lo que pide QA-01.

## Consecuencias
- **Positivas:**
  - Un solo artefacto en Docker Compose; se despliega y depura en local sin infraestructura distribuida (R-01, R-02).
  - La ingesta responde en milisegundos porque solo escribe en memoria, y el empuje por WebSocket permite cumplir los 15 s de QA-01 sin polling masivo.
  - Las escrituras por lotes reducen la presión sobre el disco del VPS (R-03).
  - Si en el futuro la carga lo exige, el módulo de Ingesta o el de Notificaciones se puede extraer como servicio, porque ya tiene una frontera definida.
- **Negativas / riesgos:**
  - El VPS es un punto único de falla. QA-02 pide 99,5 % de disponibilidad, que equivale a unas 3,6 h de caída al mes; con un solo servidor solo se llega a esa cifra con reinicio automático de contenedores (`restart: unless-stopped`), monitoreo y copias de seguridad, no con redundancia.
  - Si alguien escribe código síncrono pesado en un endpoint, congela el event loop para todos los buses y pasajeros. Hay que revisarlo en los Pull Requests.
  - El equipo tiene que aprender a fondo `asyncio`, Redis Streams y PostGIS dentro del mismo mes, lo que resta tiempo de desarrollo.
  - Se pierde el panel de administración que Django trae incluido; habrá que construir un panel mínimo para el catálogo de rutas.
