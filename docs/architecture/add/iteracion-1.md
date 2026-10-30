# Iteración 1 de ADD: Rendimiento en Tiempo Real (QA-01)

## 1. Objetivo de la Iteración
* **Escenario priorizado:** `[QA-01]` En hora punta, con 50,000 consultas concurrentes de tiempo estimado de llegada de buses (tasa media sostenida $\lambda = 30$ req/s y picos de 40 req/s), el percentil 95 ($p95$) del tiempo de respuesta debe ser $\le 150\text{ ms}$.
* **Clasificación en el Árbol de Utilidad:** (Alta importancia, Alta dificultad).
* **Elemento arquitectónico a refinar:** Módulo de consulta de llegada (`monitoreo.servicio`) y capa de persistencia/lectura.

---

## 2. Conceptos de Diseño Evaluados

| Concepto de Diseño | Atributos Favorecidos | Trade-offs y Riesgos | Costo y Complejidad | Decisión |
| :--- | :--- | :--- | :--- | :--- |
| **C1: Migración a Microservicios + Kubernetes** | Escalabilidad horizontal independiente de servicios. | Sobrecarga de red inter-servicio, latencia de serialización JSON/gRPC, complejidad DevOps inmanejable para 1 mes. | Alto ($$$, cluster k8s, meses de migración). | **Rechazado** |
| **C2: Escalar VPS a 8 workers (sin caché)** | Mayor concurrencia de hilos de atención en API. | No resuelve el cuello de botella de I/O de disco en PostgreSQL; duplicación innecesaria de costos de hosting. | Medio ($$, duplica costo de cómputo mensual). | **Rechazado** |
| **C3: Índice compuesto + Caché en memoria (TTL 10s)** | Reduce tiempo de CPU por consulta a 2 ms en aciertos; elimina contención en BD. | Consistencia eventual máxima de 10 segundos en la posición reportada al pasajero (aceptable según requerimientos SIT). | Bajo ($, LRU local / Redis ligero, 2 días dev). | **Aceptado** |

### Justificación del descarte del Concepto 1 (Microservicios)
La sugerencia inicial de la IA de dividir el monolito modular en microservicios sobre Kubernetes fue rechazada categóricamente con base en la evidencia: el volumen de 50,000 consultas en hora punta ($\approx 30\text{ req/s}$) no satura el ancho de banda del VPS, sino el tiempo de CPU/disco de la base de datos al recalcular tiempos parada por parada. Introducir Kubernetes aumenta la latencia por salto de red ($+5\text{ a }15\text{ ms}$) y viola la restricción de plazo de 1 mes del equipo.

---

## 3. Tácticas de Arquitectura Aplicadas (Bass et al., 2021)
1. **Maintain multiple copies of data (Caché):** Almacenar en memoria en caché LRU distribuida las estimaciones de llegada de cada línea por parada con un TTL de 10 segundos.
2. **Bound execution times (Índice):** Crear índices B-Tree compuestos en PostgreSQL sobre `(linea_id, parada_id, timestamp)` para que las consultas con *cache miss* tarden $< 20\text{ ms}$ en lugar de escanear millones de registros de telemetría.

---

## 4. Evidencia Cuantitativa (Simulación M/G/c)
Se modeló el subsistema de consultas como una cola $M/G/c$ (llegadas Poisson, $c=4$ workers concurrentes, tiempos de servicio calibrados con telemetría real de 1200 buses durante 120 segundos de simulación continua a $\lambda = 30\text{ req/s}$).

### Resultados comparativos:

| Configuración Evaluada | Tasa $\lambda$ | Workers ($c$) | Latencia $p50$ | Latencia $p95$ | Tiempo Medio | ¿Cumple QA-01 ($\le 150\text{ ms}$)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sin tácticas (Línea base)** | $30\text{ req/s}$ | 4 | $84.7\text{ ms}$ | **$183.5\text{ ms}$** | $94.5\text{ ms}$ | **NO (Falla SLA)** |
| **Escalar a 8 workers (C2)** | $30\text{ req/s}$ | 8 | $18.3\text{ ms}$ | $32.9\text{ ms}$ | $19.5\text{ ms}$ | Sí (pero costo $2\times$) |
| **Solo Índice en BD** | $30\text{ req/s}$ | 4 | $18.3\text{ ms}$ | $32.9\text{ ms}$ | $19.5\text{ ms}$ | Sí (al límite en picos) |
| **Índice + Caché ($85\%$ hit rate)** | $30\text{ req/s}$ | 4 | **$2.2\text{ ms}$** | **$21.3\text{ ms}$** | **$4.6\text{ ms}$** | **SÍ (Sobrecumple por $7\times$)** |

### Gráfico de Simulación:
![Rendimiento p95 y Sensibilidad de Caché](../fitness/simulacion_p95.png)

---

## 5. Análisis de Sensibilidad y Supuestos
* **Punto de sensibilidad:** La latencia $p95$ es altamente sensible a la tasa de aciertos de la caché (*hit rate*). Si el *hit rate* cae por debajo del $50\%$, el $p95$ sube a $31\text{ ms}$; sin embargo, gracias al índice compuesto, incluso con $0\%$ de aciertos el $p95$ se mantiene en $32.9\text{ ms}$, muy por debajo del límite de $150\text{ ms}$. Esto demuestra que el índice actúa como salvaguarda ante ráfagas frías de caché (*cache stampede*).
* **Supuestos del modelo:**
  1. La llegada de consultas de usuarios sigue una distribución de Poisson durante la hora punta.
  2. Los tiempos de cómputo en caché tienen baja varianza ($1\text{ a }3\text{ ms}$).
  3. El $80\%$ de las consultas de pasajeros se concentran en el $20\%$ de las paradas troncales más concurridas del SIT (principio de Pareto).

---

## 6. Conclusión de la Iteración
El escenario **QA-01 se cumple holgadamente**. Se formaliza la decisión en el `ADR-006` y se automatiza la verificación como fitness function en `tests/test_fitness.py`.
