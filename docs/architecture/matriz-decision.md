# Matriz de decisión — RutaSIT Arequipa

## Alternativas

- **A. Monolito Tradicional en Capas (Django + PostgreSQL):** Organización en capas secuenciales estándar (Presentación, Lógica de Dominio y Acceso a Datos con ORM). Todas las peticiones HTTP de telemetría GPS (30 req/s), cálculo de tiempos y consultas de usuarios pasan sincrónicamente por el pipeline web tradicional hacia una única base de datos relacional.
- **B. Microservicios Distribuidos (FastAPI/Go + RabbitMQ + Múltiples BD):** Descomposición del sistema en 4 servicios independientes (Ingesta GPS, Estimación de ETA y Geocercas, Catálogo SIT y Notificaciones WebSocket). Cada servicio posee su propia persistencia y se comunican a través de un broker de mensajería asíncrono (RabbitMQ).
- **C. Monolito Modular Asíncrono con Eventos en Memoria (FastAPI + Redis + PostgreSQL/PostGIS):** Un único artefacto desplegable estructurado internamente en módulos desacoplados con límites de dominio explícitos. Utiliza un runtime ASGI asíncrono con FastAPI y Redis en memoria para ingesta de alta frecuencia y difusión WebSocket, respaldado por PostgreSQL con extensión PostGIS para consultas espaciales y persistencia transaccional.

---

## Criterios y pesos (deben sumar 100 %)

| Criterio | Peso | Justificación (driver relacionado) |
| :--- | :---: | :--- |
| **Rendimiento en tiempo real** | 25 % | **QA-01:** Atributo crítico. Ingesta continua de 300 buses cada 10 s ($\approx 30$ req/s) y recálculo dinámico de ETA propagado a usuarios en $\le 15$ s sin cuellos de botella por contención de hilos. |
| **Tiempo de entrega (MVP en 1 mes)** | 25 % | **R-01:** Plazo estricto de 4 semanas. Penaliza arquitecturas con alta sobrecarga de configuración inicial, contratos interservicio complejos o múltiples tuberías de CI/CD. |
| **Costo operativo y viabilidad en 1 VPS** | 20 % | **R-03:** Presupuesto sumamente bajo. Toda la solución en producción debe caber de forma estable en un único servidor modesto (2-4 vCPU, 4-8 GB RAM, $\le 12$ USD/mes) sin requerir orquestadores pesados. |
| **Simplicidad operativa y experiencia del equipo** | 15 % | **R-02:** Equipo de solo 2 desarrolladores con base en Python y SQL. Se requiere facilidad de depuración local, despliegues simples y ausencia de sobrecarga DevOps distribuida. |
| **Modificabilidad y extensibilidad** | 15 % | **QA-03:** Capacidad de incorporar nuevas rutas del SIT, modificar algoritmos de estimación de llegada y alertas de desvío sin acoplamiento cruzado de código ni paradas de servicio. |

---

## Matriz (puntaje 1 = muy malo … 5 = excelente)

| Criterio (peso) | A (Monolito en capas) | B (Microservicios) | C (Monolito modular asíncrono) |
| :--- | :---: | :---: | :---: |
| **Rendimiento en tiempo real (25 %)** | 2 | 4 | **5** |
| **Tiempo de entrega (25 %)** | 4 | 1 | **4** |
| **Costo y viabilidad en 1 VPS (20 %)** | 4 | 1 | **5** |
| **Simplicidad operativa (15 %)** | 5 | 1 | **4** |
| **Modificabilidad (15 %)** | 2 | 5 | **4** |
| **Total ponderado** | **3.35** | **2.35** | **4.45** |

### Cálculo detallado del puntaje ponderado:
$$\text{Total Ponderado} = \sum (\text{peso} \times \text{puntaje})$$

* **Alternativa A (Capas):** $(0.25 \times 2) + (0.25 \times 4) + (0.20 \times 4) + (0.15 \times 5) + (0.15 \times 2) = 0.50 + 1.00 + 0.80 + 0.75 + 0.30 = \mathbf{3.35}$
* **Alternativa B (Microservicios):** $(0.25 \times 4) + (0.25 \times 1) + (0.20 \times 1) + (0.15 \times 1) + (0.15 \times 5) = 1.00 + 0.25 + 0.20 + 0.15 + 0.75 = \mathbf{2.35}$
* **Alternativa C (Monolito Modular Asíncrono):** $(0.25 \times 5) + (0.25 \times 4) + (0.20 \times 5) + (0.15 \times 4) + (0.15 \times 4) = 1.25 + 1.00 + 1.00 + 0.60 + 0.60 = \mathbf{4.45}$

---

## Conclusión

Elegimos el **Monolito Modular Asíncrono con Eventos en Memoria (Alternativa C)** con un puntaje sobresaliente de **4.45/5.00**.

### Justificación de la elección:
1. **Cumplimiento del rendimiento crítico (QA-01):** El paradigma asíncrono con ASGI (FastAPI) y Redis Pub/Sub maneja concurrentemente las 30 tramas/s de telemetría y miles de conexiones WebSocket abiertas hacia pasajeros en una sola instancia, con tiempos de respuesta en milisegundos.
2. **Factibilidad en 1 mes y 2 desarrolladores (R-01, R-02):** Evita la dispersión de esfuerzos en múltiples repositorios, gestión de redes virtuales y sincronización distribuida de datos que exige la opción de microservicios.
3. **Optimización de recursos en 1 solo VPS (R-03):** La combinación de una aplicación modular en Python + Redis + PostgreSQL/PostGIS consume menos de 1.5 GB de RAM bajo régimen de producción, operando con holgura en el servidor de bajo costo.

Para mayores detalles sobre la decisión arquitectónica formal, sus implicancias técnicas y tácticas de mitigación, ver [ADR-001](adr/001-estilo-arquitectonico.md). Asimismo, para consultar el análisis adversarial y las alternativas tácticas surgidas de la crítica profunda, ver [Demostración como Abogado del Diablo](demostracion-abogado-del-diablo.md).
