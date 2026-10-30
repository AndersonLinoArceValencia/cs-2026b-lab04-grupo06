# ADR-006: Caché en Memoria e Índices Compuestos para Consultas Masivas de Llegada (QA-01)

- **Estado:** Aceptado
- **Fecha:** 2026-10-27
- **Decisores:** Anderson Lino Arce Valencia (Arquitecto Líder), Wilson Freddy Carlos Ccamaqque (Desarrollador)

## Contexto
El escenario de crecimiento del Laboratorio 08 exige soportar 50,000 consultas de tiempo de llegada en hora punta para una flota de 1200 buses con un SLA estricto de latencia $p95 \le 150\text{ ms}$ (`[QA-01]`). La línea base sin optimización arrojaba un $p95$ de $183.5\text{ ms}$, violando el SLA.

## Alternativas consideradas
1. **Migración a Microservicios + Kubernetes:** Rechazada por complejidad operativa excesiva, latencia de red añadida y costo elevado para el plazo de entrega de 1 mes.
2. **Escalado vertical a 8 workers (sin caché):** Rechazada porque duplica el costo de cómputo y no elimina la contención de disco en la base de datos relacional.
3. **Índice compuesto en PostgreSQL + Caché LRU en memoria con TTL de 10s:** Aceptada.

## Decisión
Implementaremos:
1. Índice B-Tree compuesto en PostgreSQL sobre `(linea_id, parada_id, timestamp)`.
2. Capa de caché en memoria con TTL de 10 segundos para estimaciones de llegada de paradas troncales.
3. Se mantiene el monolito modular ejecutándose en 4 workers ASGI.

## Evidencia y Consecuencias
- **Evidencia Cuantitativa:** Simulación M/G/c a $\lambda = 30\text{ req/s}$ demostró un $p95$ de **$21.3\text{ ms}$** con caché ($85\%$ hit rate) y **$32.9\text{ ms}$** en el peor caso sin aciertos de caché, frente a los $183.5\text{ ms}$ iniciales.
- **Consecuencias Positivas:** Se cumple el SLA con holgura de $7\times$, sin incremento de costos de infraestructura.
- **Consecuencias Negativas / Trade-off:** Aceptamos una consistencia eventual máxima de 10 segundos en las estimaciones presentadas al pasajero, lo cual es admisible en el contexto del transporte público.
