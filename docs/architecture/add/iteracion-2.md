# Iteración 2 de ADD: Disponibilidad y Resiliencia Telemétrica (QA-03)

## 1. Objetivo de la Iteración
* **Escenario priorizado:** `[QA-03]` Ante caídas de la red celular (zonas sin cobertura 4G en Arequipa como Cayma Alto o Cono Norte) o fallas temporales del proveedor de telemetría GPS (timeouts del 8% y cortes de hasta 15 minutos), el sistema debe garantizar **0 eventos perdidos** y evitar la saturación de workers del servidor mediante fallo rápido.
* **Clasificación en el Árbol de Utilidad:** (Alta importancia, Media dificultad).
* **Mitigación ATAM:** Mitiga directamente el riesgo crítico **R2** detectado en la evaluación cruzada.
* **Elemento arquitectónico a refinar:** Puerto y adaptadores de ingesta GPS (`monitoreo.adaptadores` y `monitoreo.decoradores`).

---

## 2. Conceptos de Diseño Evaluados

| Concepto de Diseño | Atributos Favorecidos | Riesgos y Trade-offs | Decisión |
| :--- | :--- | :--- | :--- |
| **C1: Reintentos sincrónicos agresivos (3 intentos)** | Simple de codificar con biblioteca estándar. | Agotamiento masivo de sockets y workers de la API ante caídas de red; 277 eventos perdidos en simulación. | **Rechazado** |
| **C2: Circuit Breaker con cola en memoria Redis (Propuesta IA inicial)** | Falla rápido en < 1 ms y encola en memoria RAM. | **Falso positivo de la IA:** Si el nodo Redis se reinicia o se queda sin RAM, la cola se vacía y se pierden datos telemétricos históricos irreemplazables. | **Rechazado** |
| **C3: Circuit Breaker (Decorator) + Outbox persistente en PostgreSQL** | Falla rápido (Fast Fail) + garantía ACID de 0 pérdidas al almacenar tramas pendientes en disco en la tabla `outbox_telemetria`. | Requiere un proceso liviano en background (*daemon worker*) para drenar el outbox cuando el circuito pasa a SEMIABIERTO. | **Aceptado** |

---

## 3. Tácticas de Arquitectura Aplicadas (Bass et al., 2021)
1. **Fault Tolerance: Exception handling / Circuit Breaker:** Evita golpear continuamente un servicio externo inaccesible, abriendo el circuito tras 3 fallas consecutivas y pasando a `SEMIABIERTO` tras un período de enfriamiento.
2. **Resilience: Queue / Outbox Pattern:** Toda trama telemétrica generada en estado abierto se persiste de inmediato en una tabla outbox transaccional para su retransmisión asíncrona garantizada.
3. **Graceful Degradation:** La API responde de inmediato con confirmación de recepción diferida al dispositivo validador del bus, liberando el hilo en $< 5\text{ ms}$.

---

## 4. Evidencia Cuantitativa (Simulación Monte Carlo)
Se ejecutó una simulación Monte Carlo de una jornada telemétrica (1200 eventos con 8% de timeouts aleatorios y un apagón de red de 200 eventos consecutivos):

| Estrategia Evaluada | Eventos Totales | Eventos Perdidos | Llamadas en Caída | Encolados en Outbox | ¿Cumple QA-03 (0 perdidos)? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Reintentos Sincrónicos** | 1200 | **277** | **600** | 0 | **NO (Falla crítica)** |
| **Circuit Breaker sin Outbox** | 1200 | **278** | 22 | 0 | **NO (Pierde tramas)** |
| **Circuit Breaker + Outbox (C3)** | 1200 | **0** | **20** | **277** | **SÍ (100% Recuperados)** |

### Gráfico de Disponibilidad:
![Disponibilidad y Protección de Canal](../fitness/simulacion_disponibilidad.png)

---

## 5. Conclusión de la Iteración
El escenario **QA-03 se cumple con éxito estricto (0 pérdidas y 96.6% menos llamadas en caída)**. La decisión se formaliza en el `ADR-007` y se respalda con fitness functions en `tests/test_fitness.py`.
