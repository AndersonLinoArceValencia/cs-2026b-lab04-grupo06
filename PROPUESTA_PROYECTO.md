# Plan de Trabajo y Fundamentos Arquitectónicos — Grupo 06

## 1. Información General del Proyecto
* **Asignatura:** Construcción de Software (EPIS - UNSA, 2026-B)
* **Docente:** Mg. Antonio Arroyo Paz
* **Práctica:** Laboratorio 04: Fundamentos de arquitectura de software
* **Repositorio:** `cs-2026b-lab04-grupo06`
* **Caso Seleccionado:** **Caso 6 — RutaSIT Arequipa** (Seguimiento en tiempo real de buses del Sistema Integrado de Transporte)

---

## 2. Equipo de Trabajo y Asignación de Roles

| Integrante | Rol Principal | Responsabilidades y Entregables |
| :--- | :--- | :--- |
| **Arce Valencia Anderson Lino** | **Arquitecto Líder & Diagramador (Diagram as Code con IA)** | • **E1:** Drivers arquitectónicos y escenarios de calidad (`drivers.md`).<br>• **E3:** Diagrama Mermaid de la alternativa elegida (`arquitectura.mmd`).<br>• **E5:** Diagrama PlantUML de la alternativa descartada (`alternativa.puml`).<br>• **E6:** Script de vista física de despliegue en Python Diagrams (`despliegue.py`).<br>• Revisión cruzada de Pull Requests en GitHub. |
| **Carlos Ccamaqque Wilson Freddy** | **Evaluador de Trade-offs, Redactor de ADR & Verificador de IA** | • **E2:** Comparativa de alternativas y matriz ponderada (`matriz-decision.md`).<br>• **E4:** Registros de Decisiones Arquitectónicas (`adr/001`, `adr/002`, `adr/003`).<br>• **E7:** Bitácora crítica de IA y detección de alucinaciones (`bitacora-ia.md`).<br>• **E8:** Portada del proyecto, integración final y reflexión (`README.md`).<br>• Creación y revisión cruzada de Pull Requests en GitHub. |

---

## 3. Justificación del Stack Tecnológico Estándar

El diseño responde a las restricciones estrictas del proyecto: **1 mes de plazo (MVP)**, **equipo de 2 personas**, **1 único servidor VPS de bajo costo** y **300 buses emitiendo GPS cada 10 s (30 req/s continuos)**.

```
┌─────────────────────────────────────────────────────────────┐
│                       STACK RŪTASIT                         │
├──────────────────────┬──────────────────────────────────────┤
│ Backend              │ Python 3.11+ con FastAPI (Asíncrono) │
│ Ingesta & Streaming  │ WebSockets / SSE + Redis Pub/Sub     │
│ Datos en Tiempo Real │ Redis (Caché en memoria con TTL)     │
│ Datos Geoespaciales  │ PostgreSQL 16 + PostGIS              │
│ Frontend Cliente     │ PWA (React / Vite + Leaflet / OSM)   │
│ Servidor & Proxy     │ 1 VPS Linux (Nginx Reverse Proxy)    │
│ Despliegue           │ Docker Compose                       │
└──────────────────────┴──────────────────────────────────────┘
```

### ¿Por qué este stack?
1. **Python con FastAPI:** Manejo asíncrono nativo (`asyncio`), soporte integrado de WebSockets de alto rendimiento, y validación automática de contratos GPS con Pydantic.
2. **Redis:** Actúa como buffer y almacén de "última posición conocida" de los 300 buses. Evita escribir en disco 30 veces por segundo en PostgreSQL, reduciendo el consumo de I/O en un VPS económico. Además, provee Pub/Sub instantáneo hacia los clientes web.
3. **PostgreSQL con PostGIS:** Permite almacenamiento relacional confiable de rutas, paraderos, paradas oficiales y consultas geográficas avanzadas (`ST_DWithin`, distancias a paraderos y polígonos de ruta).
4. **Leaflet + OpenStreetMap:** Evita costos de facturación por uso de Google Maps API, manteniendo el presupuesto en 0 para licencias de mapas.
5. **Arquitectura Base:** Monolito Modular Asíncrono. Un único artefacto desplegable en Docker, pero separado lógicamente en 4 módulos desacoplados:
   - `ingesta_gps`: Recepción de tramas GPS por HTTP (`/telemetry` y `/telemetry/batch` tras un corte de señal).
   - `catalogo_rutas`: Gestión de rutas, paraderos y frecuencias.
   - `estimacion_eta`: Cálculo dinámico de tiempos de llegada y detección de desvíos.
   - `notificaciones`: Distribución de eventos por WebSocket a pasajeros y operadores.

---

## 4. Estructura de Carpetas del Repositorio

```text
cs-2026b-lab04-grupo06/
├── PROPUESTA_PROYECTO.md                    # Documento base de arquitectura y roles
├── README.md                                # E8: Portada, integración y reflexión
├── .github/workflows/diagramas.yml          # Reto opcional: regenera los PNG de Mermaid en cada push
└── docs/
    ├── cuestionario.md                      # Sección IV: respuestas del cuestionario
    └── architecture/
        ├── drivers.md                       # E1: Drivers y escenarios de calidad
        ├── matriz-decision.md               # E2: 3 estilos y matriz ponderada
        ├── demostracion-abogado-del-diablo.md  # E2: crítica adversarial y respuesta del equipo
        ├── bitacora-ia.md                   # E7: Registro de prompts y verificaciones
        ├── adr/                             # E4: Architecture Decision Records
        │   ├── 000-plantilla.md
        │   ├── 001-estilo-arquitectonico.md
        │   ├── 002-base-de-datos-geovial.md
        │   └── 003-transmision-tiempo-real.md
        └── diagramas/
            ├── arquitectura.mmd             # E3: Diagrama Mermaid (Elegida)
            ├── alternativa.puml             # E5: Diagrama PlantUML (Descartada)
            ├── despliegue.py                # E6: Vista de despliegue (Diagrams + Graphviz)
            ├── despliegue.puml              # Vista de despliegue complementaria en PlantUML
            ├── matriz.py                    # E2: gráfico de la matriz ponderada (matplotlib)
            └── img/                         # Renders PNG/SVG
```

---

## 5. Distribución de Roles - Laboratorio 05 (Diseño UML)

Para el Laboratorio 05 (Diseño Detallado UML), mantendremos el enfoque basado en los perfiles de los integrantes, asignando los entregables en la carpeta `docs/design/` de la siguiente manera:

### 🧑‍💻 Arce Valencia Anderson Lino (Arquitecto Líder & Diagramador)
**Enfoque: Diseño estructural, comportamiento y codificación.**
* **E1:** Historia de usuario y diagrama de clases (`docs/design/historia.md` y `docs/design/clases.puml`).
* **E2:** Diagrama de secuencia del flujo crítico (`docs/design/secuencia-consultar-tiempo.puml`).
* **E3:** Máquina de estados de la entidad principal `Viaje` (`docs/design/estados-viaje.mmd`).
* **E6:** Round-trip con IA / Ingeniería inversa (`src/monitoreo/` y `docs/design/round-trip.md`).
* Revisión cruzada de Pull Requests.

### 🕵️‍♂️ Carlos Ccamaqque Wilson Freddy (Evaluador & Verificador de IA)
**Enfoque: Procesos de negocio, arquitectura de paquetes y QA.**
* **E4:** Diagrama de actividades de detección de desvío (`docs/design/actividades-deteccion-desvio.puml`).
* **E5:** Diagrama de paquetes (`docs/design/paquetes.puml`).
* **E7:** Revisión de consistencia de diagramas y bitácora de IA (`docs/design/consistencia.md` y `docs/design/bitacora-ia.md`).
* **E8:** Integración en README, revisión cruzada (PRs) y creación del tag `v0.5-diseno`.
