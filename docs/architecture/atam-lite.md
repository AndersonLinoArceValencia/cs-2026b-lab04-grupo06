# Evaluación de Arquitectura ATAM-Lite: RutaSIT Arequipa

Este documento consolida la evaluación arquitectónica mediante el método **ATAM-lite** (*Architecture Tradeoff Analysis Method*) para el sistema de monitoreo en tiempo real **RutaSIT Arequipa** (1200 buses, 50,000 consultas concurrentes en hora punta), integrando la evaluación cruzada recibida, la matriz de riesgos y las decisiones de mitigación.

---

## 1. Resumen de Hallazgos Arquitectónicos

| ID | Tipo de Hallazgo | Descripción Técnica | Atributos Relacionados | Estado / Mitigación |
| :---: | :---: | :--- | :--- | :--- |
| **S1** | **Punto de Sensibilidad** | La latencia $p95$ en paradas troncales depende directamente del *hit rate* de la caché en memoria cuando $\lambda > 30\text{ req/s}$. | Rendimiento (QA-01) | Sensibilidad controlada: aún con $0\%$ hit rate, el índice garantiza $p95 \le 33\text{ ms}$. |
| **S2** | **Punto de Sensibilidad** | El retardo en la ingesta de telemetría de 1200 buses depende del tiempo de inserción en la cola de eventos. | Rendimiento e Ingesta (QA-02) | Buffer en memoria + escritura asíncrona en batches de 50 eventos. |
| **T1** | **Trade-off** | **Rendimiento vs. Consistencia de Datos:** El uso de caché con TTL de 10s reduce la carga de BD en un $85\%$, pero introduce hasta 10s de eventual consistencia en la posición visualizada. | Rendimiento vs. Consistencia | Aceptado: 10s es irrelevante para el usuario esperando en parada. |
| **T2** | **Trade-off** | **Disponibilidad vs. Complejidad:** La adopción de Circuit Breaker + Outbox previene la saturación de hilos ante caídas de GPS, a cambio de una tarea worker de reconciliación en segundo plano. | Disponibilidad vs. Modificabilidad | Aceptado: la resiliencia operativa del SIT es prioritaria. |
| **R1** | **Riesgo** | **Stampede / Thundering Herd:** Si el servicio de caché se reinicia en plena hora punta, las 50,000 consultas concurrentes golpean la base de datos simultáneamente. | Rendimiento y Disponibilidad | Probabilidad Media, Impacto Alto. Mitigación: Mutex de refresco anticipado (XFetch) e índices B-Tree. |
| **R2** | **Riesgo** | **Saturación por Reintentos Sincrónicos:** Ante pérdida de conectividad móvil en zonas altas de Arequipa (Cayma, Cono Norte), reintentar llamadas HTTP sincrónicas bloquearía todos los workers de la API. | Disponibilidad y Fiabilidad | Probabilidad Alta, Impacto Alto. Mitigación: Circuit Breaker + Outbox persistente (Iteración 2). |
| **NR1**| **No Riesgo** | **Aislamiento del Modelo de IA:** El aislamiento del componente de IA mediante el patrón Facade/Proxy (ADR-005) garantiza que fallas o latencia del modelo predictivo nunca bloquean la telemetría central. | Disponibilidad y Modificabilidad | Validado con pruebas unitarias (`tests/test_patrones.py`). |

---

## 2. Evaluación Cruzada Recibida (Issue de Grupo Evaluador)

A continuación se registra el reporte de revisión cruzada recibido en GitHub Issues por parte del equipo evaluador (**Grupo 05 - CitaSalud**):

> ### Issue #42: Evaluación ATAM-Lite sobre la arquitectura de RutaSIT Arequipa
> **Evaluador:** Grupo 05 (CitaSalud Arequipa)  
> **Fecha:** 27 de Octubre de 2026  
> 
> Estimado equipo del Grupo 06 (RutaSIT Arequipa):  
> Tras examinar su Árbol de Utilidad y la Iteración 1 de ADD, reportamos los siguientes hallazgos:
> 
> 1. **Punto de Sensibilidad S-01:** Observamos que su simulación asume un $85\%$ de aciertos de caché. ¿Qué ocurre si un evento de tráfico imprevisto (ej. paro de transportes en el Centro Histórico) invalida masivamente las rutas?
> 2. **Trade-off T-01:** Discuten el balance entre latencia y consistencia (10s de desfase). Consideramos que para buses de tránsito rápido, 10s puede inducir a error si el bus pasa de largo.
> 3. **Riesgo Crítico R-01 (Probabilidad Media, Impacto Alto):** Si la memoria Redis/LRU falla, el *cache stampede* podría llevar la base de datos a un bloqueo de conexiones (*connection pool starvation*).
> 4. **Riesgo R-02 (Probabilidad Alta, Impacto Alto):** En las zonas periféricas de Arequipa con fallas 4G recurrentes, la ingesta de los 1200 buses podría perder paquetes de posición si no hay buffering persistente.
> 5. **No Riesgo NR-01:** Concordamos en que el diseño desacoplado de las alertas y adaptadores de GPS (ADR-005) aísla adecuadamente los subsistemas.

---

## 3. Respuesta Oficial y Mitigaciones con Evidencia

| Hallazgo del Issue | Posición del Equipo | Justificación Técnica y Evidencia Respaldatoria |
| :--- | :---: | :--- |
| **S-01: Caída de aciertos en eventos de tráfico** | **Aceptado** | Gracias al índice compuesto `(linea_id, parada_id)`, nuestra simulación M/G/c demostró que incluso con un $0\%$ de aciertos de caché, el $p95$ es de solo **$32.9\text{ ms}$**, lo cual permanece holgadamente por debajo del umbral de **$150\text{ ms}$**. No existe riesgo de degradación crítica. |
| **T-01: Desfase de 10s en buses rápidos** | **Refutado con datos de dominio** | En el SIT Arequipa, la velocidad promedio en hora punta es de $18\text{ km/h}$ ($5\text{ m/s}$). En 10 segundos, el bus avanza como máximo 50 metros, distancia menor que la longitud visual de aproximación a una parada. Por tanto, el trade-off es completamente aceptable para el usuario. |
| **R-01: Cache Stampede sobre base de datos** | **Aceptado y Mitigado** | Se adoptó la técnica de bloqueo probabilístico (*probabilistic early expiration*) y se fijó un tamaño máximo de pool de conexiones en SQLAlchemy/PostgreSQL con límite de timeout de 2 segundos. |
| **R-02: Pérdida de paquetes en zonas sin señal** | **Aceptado y Mitigado** | Abordado directamente en la **Iteración 2 de ADD**: se implementa el patrón **Decorator con Circuit Breaker** en el cliente del validador del bus y una **tabla Outbox** local que almacena las tramas hasta que se restablece el enlace de datos. |

---

## 4. Matriz de Riesgos y Priorización

```
  Impacto
    ▲
Alto│            [R1: Stampede]     [R2: Pérdida señal GPS]
    │                                (Mitigado en Iteración 2)
Med.│            [T1: Consistencia]  [S1: Sensibilidad Caché]
    │
Bajo│ [NR1: IA]
    └────────────────────────────────────────────────────────►
         Baja           Media               Alta     Probabilidad
```

* **Zona Crítica (Alta probabilidad / Alto impacto):** `R2 (Pérdida de señal GPS)` se mitiga mediante la combinación de **Circuit Breaker + Outbox transaccional** documentada en `docs/architecture/add/iteracion-2.md` y `ADR-007`.
