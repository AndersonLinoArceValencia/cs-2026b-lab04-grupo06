"""
Script de vista de despliegue para RutaSIT Arequipa utilizando la librería Diagrams.
Representa la topología física de ejecución en un único VPS de bajo costo.

Requisitos:
    pip install diagrams
    Graphviz instalado en el sistema:
        Windows:  winget install graphviz   (luego reiniciar la terminal)
        Ubuntu:   sudo apt install graphviz
        macOS:    brew install graphviz

Ejecutar desde la raíz del repositorio:
    python docs/architecture/diagramas/despliegue.py

Genera docs/architecture/diagramas/img/despliegue.png y despliegue.svg.
La vista complementaria en PlantUML (despliegue.puml) se renderiza en img/despliegue-plantuml.png.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.generic.device import Mobile
from diagrams.onprem.network import Nginx, Internet
from diagrams.programming.framework import FastAPI
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.compute import Server

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline"
}

with Diagram(
    "RutaSIT Arequipa - Vista de Despliegue en VPS",
    filename="docs/architecture/diagramas/img/despliegue",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat=["png", "svg"]
) as diag:
    # 1. Dispositivos y Usuarios
    buses = Mobile("300 Buses SIT\n(GPS Embarcado)")
    pasajeros = Users("Pasajeros\n(PWA Móvil)")
    operador = Users("Operador SIT\n(Consola Web)")

    # 2. Servidor en la Nube (VPS de Producción)
    with Cluster("Servidor en la Nube (VPS Único: 2-4 vCPU, 4-8 GB RAM)"):
        proxy = Nginx("Nginx Proxy\n(HTTPS / WSS)")

        with Cluster("Monolito Modular Asíncrono (Python / ASGI)"):
            app = FastAPI("FastAPI Core\n(5 módulos de dominio)")
            geo_worker = Server("Worker Geoespacial\n(asyncio.to_thread / Multiprocess)")
            batch_worker = Server("Batch Writer\n(escritura en lote c/5s)")

        with Cluster("Almacenamiento y Estado en Memoria"):
            cache = Redis("Redis 7.x\n(Streams + Caché Hash + Pub/Sub, AOF)")
            db = PostgreSQL("PostgreSQL 16 + PostGIS\n(Catálogo, Flota e Histórico)")

        with Cluster("Pila de Observabilidad"):
            prom = Prometheus("Prometheus\n(Métricas p95 / CPU)")
            mon = Grafana("Grafana\n(Dashboard Operador)")
            prom >> mon

    # 3. Servicios Externos
    osm = Internet("OpenStreetMap\n(CDN de mapas abierto)")
    push = Internet("Web Push\n(Notificaciones y alertas)")

    # 4. Flujos de red y conexiones etiquetadas con Edge(label=...)
    buses >> Edge(label="POST /telemetry (c/10s)\n/telemetry/batch tras corte") >> proxy
    pasajeros >> Edge(label="HTTPS / WSS (ETA ≤ 15s)") >> proxy
    operador >> Edge(label="HTTPS Admin") >> proxy

    proxy >> Edge(label="ASGI Reverse Proxy") >> app

    app >> Edge(label="XADD (<1ms)") >> cache
    cache >> Edge(label="consume stream") >> geo_worker
    geo_worker >> Edge(label="actualiza estado") >> cache
    cache >> Edge(label="batch read") >> batch_worker
    batch_worker >> Edge(label="COPY c/5s") >> db

    app >> Edge(label="catálogo / rutas") >> db
    db >> Edge(label="rehidrata estado al arrancar", style="dashed") >> cache
    cache >> Edge(label="Pub/Sub broadcast") >> app

    app >> Edge(label="métricas /metrics", style="dotted") >> prom
    pasajeros >> Edge(label="descarga mapas", style="dashed") >> osm
    app >> Edge(label="despacha alertas", style="dashed") >> push
