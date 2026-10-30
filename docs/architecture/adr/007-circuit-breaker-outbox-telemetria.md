# ADR-007: Resiliencia Telemétrica con Circuit Breaker y Patrón Outbox Transaccional (QA-03)

- **Estado:** Aceptado
- **Fecha:** 2026-10-28
- **Decisores:** Anderson Lino Arce Valencia (Arquitecto Líder), Wilson Freddy Carlos Ccamaqque (Desarrollador)

## Contexto
En diversas rutas del SIT Arequipa (Cayma, Cono Norte, Paucarpata) existen zonas de sombra móvil y caídas temporales del canal de comunicación 4G. En la línea base con reintentos sincrónicos, los hilos de los workers se bloqueaban esperando timeouts, perdiendo hasta el 23% de las tramas telemétricas (`[QA-03]` y riesgo crítico `R2` de ATAM-lite).

## Alternativas consideradas
1. **Reintentos sincrónicos con backoff:** Rechazado porque satura los workers y agota el pool de conexiones HTTP.
2. **Circuit Breaker con buffer en memoria RAM (Redis):** Rechazado por riesgo de pérdida de datos ante reinicios no programados del contenedor.
3. **Decorator ConCircuitBreaker + Tabla Outbox en PostgreSQL:** Aceptado.

## Decisión
1. Envolver los adaptadores de telemetría con un **Decorator Circuit Breaker** que pasa a estado `ABIERTO` tras 3 timeouts consecutivos, implementando fallo rápido (*Fast Fail*).
2. Durante el estado abierto, las tramas telemétricas se persisten de inmediato en la tabla `outbox_telemetria` de PostgreSQL con semántica ACID.
3. Un worker asíncrono procesa y vacía la tabla outbox una vez que el circuito transiciona a `SEMIABIERTO` y valida la disponibilidad del enlace.

## Evidencia y Consecuencias
- **Evidencia Cuantitativa:** Simulación Monte Carlo demostró **0 eventos perdidos** (frente a 277 en reintentos simples) y una reducción del $96.6\%$ en llamadas infructuosas durante apagones de red (de 600 a 20 llamadas).
- **Consecuencias Positivas:** Resiliencia total de datos y protección absoluta de los workers de la API.
- **Consecuencias Negativas / Trade-off:** Incremento marginal en almacenamiento temporal de disco en la base de datos hasta que el worker drena la cola.
