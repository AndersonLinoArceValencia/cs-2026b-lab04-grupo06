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

---

## 6. Estructura de Carpetas - Laboratorio 05 (Diseño UML)

Para el Laboratorio 05, se añadirá la siguiente estructura enfocada en el diseño detallado:

```text
cs-2026b-lab04-grupo06/
├── docs/
│   └── design/                               # Directorio principal del Lab 05
│       ├── historia.md                       # E1: Historia y criterios de aceptación
│       ├── clases.puml                       # E1: Diagrama de clases (PlantUML)
│       ├── secuencia-consultar-tiempo.puml   # E2: Diagrama de secuencia (PlantUML)
│       ├── estados-viaje.mmd                 # E3: Máquina de estados (Mermaid)
│       ├── actividades-deteccion-desvio.puml # E4: Diagrama de actividades (PlantUML)
│       ├── paquetes.puml                     # E5: Diagrama de paquetes (PlantUML)
│       ├── round-trip.md                     # E6: Análisis de diferencias del código generado
│       ├── consistencia.md                   # E7: Análisis de falsos positivos detectados por IA
│       └── bitacora-ia.md                    # E7: Registro de prompts de diseño
└── src/
    └── monitoreo/                            # E6: Esqueleto de código Python generado
```

---

## 7. Distribución de Roles — Laboratorio 06 (Modelo C4 con Structurizr DSL)

Para el Laboratorio 06, se continúa el desarrollo arquitectónico de **RutaSIT Arequipa**, modelando el sistema completo bajo el enfoque de "Arquitectura como Código" con Structurizr DSL, integrando los artefactos de los Laboratorios 04 y 05:

### 🧑‍💻 Arce Valencia Anderson Lino (Arquitecto Líder & Modelador C4)
**Enfoque: Modelado estructural, jerarquía C4 y flujos dinámicos.**
* **E1:** Inventario de elementos C4 y Diagrama de Contexto (`docs/architecture/c4/inventario.md` y `workspace.dsl`).
* **E2:** Diagrama de Contenedores con tecnologías y protocolos en `workspace.dsl`.
* **E3:** Diagrama de Componentes de la API FastAPI en `workspace.dsl`.
* **E4:** Vista Dinámica del flujo crítico ("Consultar tiempo de llegada") y comparativa con secuencia UML (`comparacion.md`).
* Revisión técnica de modelos y soporte de validación con Structurizr CLI.

### 🕵️‍♂️ Carlos Ccamaqque Wilson Freddy (Evaluador, Auditor & Comunicador)
**Enfoque: Despliegue físico, auditoría de calidad, comunicación y entrega.**
* **E5:** Vista de Despliegue en entorno de Producción (VPS + Docker Compose) en `workspace.dsl`.
* **E6:** Exportación a C4-PlantUML / Mermaid, renderizado PNG y contexto manual (`contexto-manual.puml`).
* **E7:** Auditoría con checklist oficial de C4 (`revision-c4.md`), detección de falsos positivos con IA, redacción no técnica (`explicacion.md`) y bitácora de IA (`bitacora-ia.md`).
* **E8:** Portada README con vista Mermaid C4, atención de issue de revisión cruzada y creación del tag `v0.6-c4`.

---

## 8. Estructura de Carpetas — Laboratorio 06 (Modelo C4)

```text
cs-2026b-lab04-grupo06/
├── docs/
│   └── architecture/
│       └── c4/                               # Directorio de arquitectura C4 (Lab 06)
│           ├── inventario.md                 # E1: Mapeo de elementos C4 y su origen
│           ├── workspace.dsl                 # E1-E5: Modelo unificado en Structurizr DSL
│           ├── contexto-manual.puml          # E6: Vista de contexto escrita a mano en C4-PlantUML
│           ├── comparacion.md                # E4 y E6: Análisis comparativo (UML vs C4, DSL vs Manual)
│           ├── revision-c4.md                # E7: Auditoría con lista de revisión oficial de c4model.com
│           ├── explicacion.md                # E7: Resumen ejecutivo para público no técnico (<= 120 palabras)
│           ├── export/                       # E6: Diagramas exportados (.puml y .mmd) por Structurizr
│           └── img/                          # E6: Vistas exportadas y renderizadas a PNG
```
