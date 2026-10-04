# ADR-003: Enviar las posiciones y el ETA a los clientes por WebSocket con Redis Pub/Sub

- Estado: Aceptado
- Fecha: 2026-10-04
- Decisores: Arce Valencia Anderson Lino y Carlos Ccamaqque Wilson Freddy (Grupo 06)

## Contexto
El pasajero debe ver en el mapa los buses de su ruta moviéndose (RF-02) y el ETA hacia su paradero (RF-03); el operador ve el estado de toda la flota (RF-05). QA-01 exige que el cambio de posición llegue a la pantalla en 15 s o menos (p95), con 1500 pasajeros conectados en hora punta. Todo corre en un único VPS de bajo costo (R-03) y los pasajeros usan datos móviles, donde la conexión se corta y vuelve (R-04).

La pregunta es cómo llega la actualización desde el servidor hasta el navegador.

## Alternativas consideradas
1. **Polling HTTP.** El navegador pide la posición cada 5 s. Es lo más simple, pero 1500 pasajeros generan unas 300 peticiones/s, diez veces la carga de ingesta, y la mayoría devuelven datos que no han cambiado. Si se baja la frecuencia para ahorrar carga, la latencia se acerca al límite de 15 s.
2. **Server-Sent Events (SSE).** Canal unidireccional servidor → cliente sobre HTTP, con reconexión automática en el navegador (`EventSource`). Encaja con el flujo de datos, pero para cambiar de ruta o paradero el cliente tiene que cerrar y abrir otra conexión, y con HTTP/1.1 el navegador limita las conexiones simultáneas por dominio.
3. **WebSocket con difusión por Redis Pub/Sub.** Conexión bidireccional persistente: el cliente se suscribe a una ruta o paradero y cambia la suscripción por el mismo canal. FastAPI lo soporta de forma nativa.

## Decisión
Usaremos **WebSocket** (`wss://`, terminado en Nginx) para pasajeros y operadores. Cada cliente se suscribe a los canales que le interesan (por ejemplo, `ruta:A12` o `paradero:345`). Cuando el worker de ETA actualiza el estado de un bus, publica el cambio en **Redis Pub/Sub** y el módulo de Notificaciones lo reenvía solo a los sockets suscritos a ese canal.

El cliente PWA enviará un *heartbeat* cada 30 s, se reconectará con espera creciente al perder la red y, si no consigue abrir el WebSocket, caerá a **polling cada 15 s** como modo degradado.

## Consecuencias
- **Positivas:**
  - Solo viaja el dato que cambió y solo a quien le interesa, así que la latencia queda dominada por el ciclo de 10 s del GPS y no por la frecuencia del polling (QA-01).
  - La carga sobre el servidor no crece con la frecuencia de refresco de los pasajeros.
  - Redis Pub/Sub ya está en la arquitectura (ADR-001), así que no se agrega ningún componente nuevo. Si más adelante se levantan varios procesos de API, todos reciben los mismos eventos.
- **Negativas / riesgos:**
  - Cada pasajero mantiene un socket abierto: hay que subir el límite de descriptores de archivo del sistema (`ulimit -n`) y configurar Nginx para el *upgrade* y para no cerrar conexiones inactivas antes del *heartbeat*.
  - La reconexión, el *heartbeat* y el modo degradado son lógica que el equipo tiene que programar y probar; con polling no existiría.
  - Redis Pub/Sub no guarda mensajes: un cliente desconectado pierde los eventos de ese intervalo y, al volver, debe pedir el estado actual por HTTP antes de seguir escuchando.
