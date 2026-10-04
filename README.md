# RutaSIT Arequipa — Laboratorio 04: Fundamentos de arquitectura de software
Construcción de Software · EPIS-UNSA · 2026-B · Grupo 06

## Integrantes
| Nombre | Rol en el laboratorio |
|--------|-----------------------|
| Arce Valencia Anderson Lino | Arquitecto líder y diagramador: drivers (E1), diagrama Mermaid (E3), alternativa en PlantUML (E5) y vista de despliegue (E6) |
| Carlos Ccamaqque Wilson Freddy | Evaluador de trade-offs, redactor de ADR y verificador de IA: matriz de decisión (E2), ADR (E4), bitácora de IA (E7) y README (E8) |

## Caso
**Caso 6 — RutaSIT Arequipa.** Sistema de seguimiento en tiempo real de los buses del Sistema Integrado de Transporte de Arequipa. Los 300 buses envían su posición GPS cada 10 segundos; el pasajero ve en un mapa dónde está su bus y cuánto falta para que llegue a su paradero, y el centro de control recibe alertas cuando un bus se desvía de su ruta o hay congestión. El MVP debe salir en 1 mes, con 2 desarrolladores y un único VPS de bajo costo.

**Atributo de calidad crítico: rendimiento en tiempo real.** Con unas 30 tramas por segundo y 1500 pasajeros conectados en hora punta, el cambio de posición debe llegar a la pantalla en 15 s o menos (p95). Ver [QA-01 en drivers.md](docs/architecture/drivers.md).

## Arquitectura elegida
Monolito modular asíncrono (FastAPI + Redis + PostgreSQL/PostGIS), elegido con 4.45/5 en la [matriz de decisión](docs/architecture/matriz-decision.md).

```mermaid
flowchart TB
    %% Actores del Sistema
    BUS["🚌 Bus SIT (Dispositivo GPS Embarcado)<br/><i>300 unidades • 1 trama c/10s</i>"]
    PAS["📱 Pasajero SIT<br/><i>App Móvil PWA (Leaflet)</i>"]
    OPE["💻 Operador del SIT<br/><i>Centro de Control y Monitoreo</i>"]

    %% Sistema Central: Monolito Modular Asíncrono
    subgraph APP["RutaSIT Arequipa — Monolito Modular Asíncrono (Un solo despliegue en VPS)"]
        API["Capa de Entrada: API Gateway ASGI (FastAPI + Nginx Proxy)<br/><i>Terminación HTTPS, enrutamiento y WebSockets masivos</i>"]

        subgraph MODULOS["Módulos de Dominio (Fronteras y contratos explícitos)"]
            M1["Módulo de Ingesta GPS<br/><b>[RF-01]</b> <i>Validación ultrarrápida y buffer</i>"]
            M2["Módulo de ETA y Geocercas<br/><b>[RF-03, RF-04]</b> <i>Cálculo espacial y desvíos</i>"]
            M3["Módulo de Notificaciones y Tiempo Real<br/><b>[RF-02, RF-03]</b> <i>Broker WebSockets</i>"]
            M4["Módulo de Catálogo SIT<br/><b>[RF-06]</b> <i>Rutas, paraderos y tarifas</i>"]
            M5["Módulo de Supervisión de Flota<br/><b>[RF-05]</b> <i>Indicadores, frecuencias y panel</i>"]
        end

        INF["Capa de Infraestructura y Tareas en Segundo Plano<br/><i>Workers desacoplados, persistencia por lotes y adaptadores</i>"]
    end

    %% Capa de Almacenamiento y Estado
    REDIS[("⚡ Redis en Memoria<br/><i>Redis Streams (buffer) + Caché estado buses + Pub/Sub<br/>Persistencia AOF</i>")]
    DB[("🐘 PostgreSQL + PostGIS<br/><i>Esquemas: catálogo espacial, flota e histórico batch</i>")]

    %% Servicios Externos
    OSM["🗺️ Servidor OpenStreetMap / CDN Tiles<br/><i>(Cartografía abierta libre de costos comerciales)</i>"]
    PUSH["🔔 Servicio Web Push / Alertas<br/><i>(Notificaciones de desvío y congestión)</i>"]

    %% Relaciones de Actores con la API
    BUS -->|"HTTP POST /telemetry (~30 req/s)<br/>POST /telemetry/batch tras corte de señal"| API
    PAS -->|"HTTPS / Consulta de catálogo y rutas"| API
    PAS <-->|"WebSocket / Flujo continuo de buses y ETA (≤15s)"| API
    OPE -->|"HTTPS / Dashboard de supervisión y gestión"| API

    %% Flujo Interno en el Monolito
    API --> M1
    API --> M4
    API --> M5
    API <--> M3

    %% Conexiones con la Capa de Infraestructura y Almacenamiento
    M1 -->|"XADD trama instantánea (<1ms)"| REDIS
    INF -->|"Lee stream de telemetría"| REDIS
    INF -->|"Ejecuta cómputo geométrico (async worker)"| M2
    M2 -->|"Actualiza último estado y ETA"| REDIS
    REDIS -->|"Evento Pub/Sub difusión"| M3
    INF -->|"Escritura en lote consolidada c/5s"| DB
    M4 & M5 --> INF
    INF --> DB
    DB -.->|"Rehidrata último estado al arrancar"| REDIS
    INF -.->|"Despacho de alertas masivas"| PUSH

    %% Consumo externo de mapas
    PAS -.->|"Descarga capas y teselas de mapa"| OSM

    %% Definición de Estilos
    classDef usr fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    classDef api fill:#ECEFF1,stroke:#37474F,stroke-width:2px,color:#263238
    classDef mod fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef inf fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#E65100
    classDef store fill:#FFF3E0,stroke:#E65100,stroke-width:2px,color:#BF360C
    classDef ext fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,stroke-dasharray: 4 3,color:#4A148C

    class BUS,PAS,OPE usr
    class API api
    class M1,M2,M3,M4,M5 mod
    class INF inf
    class REDIS,DB store
    class OSM,PUSH ext
```

## Decisiones arquitectónicas
- [ADR-001: Estilo arquitectónico — monolito modular asíncrono con búfer en Redis](docs/architecture/adr/001-estilo-arquitectonico.md)
- [ADR-002: Base de datos geovial — PostgreSQL + PostGIS y Redis para el estado en vivo](docs/architecture/adr/002-base-de-datos-geovial.md)
- [ADR-003: Transmisión en tiempo real — WebSocket con Redis Pub/Sub](docs/architecture/adr/003-transmision-tiempo-real.md)

## Entregables
| Código | Archivo |
|:---:|---|
| E1 | [docs/architecture/drivers.md](docs/architecture/drivers.md) |
| E2 | [docs/architecture/matriz-decision.md](docs/architecture/matriz-decision.md), [demostración del abogado del diablo](docs/architecture/demostracion-abogado-del-diablo.md) y gráfico [diagramas/matriz.py](docs/architecture/diagramas/matriz.py) → [imagen](docs/architecture/diagramas/img/matriz-decision.png) |
| E3 | [diagramas/arquitectura.mmd](docs/architecture/diagramas/arquitectura.mmd) → [imagen](docs/architecture/diagramas/img/arquitectura.png) |
| E4 | [docs/architecture/adr/](docs/architecture/adr/) |
| E5 | [diagramas/alternativa.puml](docs/architecture/diagramas/alternativa.puml) → [imagen](docs/architecture/diagramas/img/alternativa.png) |
| E6 | [diagramas/despliegue.py](docs/architecture/diagramas/despliegue.py) → [imagen](docs/architecture/diagramas/img/despliegue.png) |
| E7 | [docs/architecture/bitacora-ia.md](docs/architecture/bitacora-ia.md) |
| E8 | Este README |
| Cuestionario | [docs/cuestionario.md](docs/cuestionario.md) |
| Reto opcional | [.github/workflows/diagramas.yml](.github/workflows/diagramas.yml): regenera los PNG y SVG de los `.mmd` con mermaid-cli en cada push a `main` |

**Sobre la vista de despliegue:** `despliegue.py` se ejecutó con la librería Diagrams y Graphviz (`python docs/architecture/diagramas/despliegue.py` desde la raíz). El archivo `despliegue.puml` es una vista complementaria del mismo despliegue hecha en PlantUML ([imagen](docs/architecture/diagramas/img/despliegue-plantuml.png)); no reemplaza al script.

**Reto opcional:** la GitHub Action [`diagramas.yml`](.github/workflows/diagramas.yml) se ejecuta en cada push a `main` que modifique un archivo `.mmd` (o a mano desde la pestaña *Actions*). Instala mermaid-cli, vuelve a renderizar `arquitectura.mmd` en `diagramas/img/` y, si la imagen cambió, la sube con un commit de `github-actions[bot]`.

## Reflexión sobre el uso de la IA
La IA nos ahorró mucho tiempo en lo mecánico: armar la estructura de los drivers, escribir la sintaxis de Mermaid, PlantUML y Diagrams, y proponer alternativas que no habíamos pensado, como la variante de Django con un ingestor aparte. Donde más nos sirvió fue como abogado del diablo, porque nos obligó a ver que nuestra opción favorita podía bloquear el event loop o perder el estado si Redis se caía.
También cometió errores, y no siempre se notaban. Primero sugirió microservicios con brokers pesados para un equipo de 2 personas, y en la crítica a la Alternativa A dio cifras alarmantes ("agota los workers", "100 % de I/O") que no resistieron un cálculo simple con la Ley de Little.
Aprendimos a tratar cada número que da la IA como una hipótesis: pasarlo a carga por segundo, compararlo con las restricciones de `drivers.md` y no copiarlo a un documento sin una fuente o un cálculo. La IA propone, pero las decisiones y su defensa son nuestras.
