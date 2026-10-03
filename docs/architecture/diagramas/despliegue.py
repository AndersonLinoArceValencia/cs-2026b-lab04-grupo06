"""
Script de vista de despliegue para RutaSIT Arequipa utilizando la librería Diagrams.
Representa la topología física de ejecución en un único VPS de bajo costo.

Para ejecutar este script se requiere:
    pip install diagrams
    sudo pacman -S graphviz (o equivalente según la distribución)

En caso de no contar con Graphviz en el entorno del sistema, la guía de laboratorio
establece en el Paso E6.4 la alternativa de utilizar la vista de despliegue con PlantUML
(disponible en docs/architecture/diagramas/despliegue.puml y renderizada en img/despliegue.png).
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
    "pad": "0.4"
}

with Diagram(
    "RutaSIT Arequipa - Vista de Despliegue en VPS",
    filename="docs/architecture/diagramas/img/despliegue",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat="png"
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
            cache = Redis("Redis 7.x\n(Streams + Caché Hash + Pub/Sub)")
            db = PostgreSQL("PostgreSQL 16 + PostGIS\n(Catálogo, Flota e Histórico)")

        with Cluster("Pila de Observabilidad"):
            prom = Prometheus("Prometheus\n(Métricas p95 / CPU)")
            mon = Grafana("Grafana\n(Dashboard Operador)")
            prom >> mon

    # 3. Servicios Externos
    osm = Internet("OpenStreetMap\n(CDN de mapas abierto)")
    push = Internet("Web Push\n(Notificaciones y alertas)")

    # 4. Flujos de red y conexiones etiquetadas con Edge(label=...)
    buses >> Edge(label="POST /telemetry (c/10s)") >> proxy
    pasajeros >> Edge(label="HTTPS / WSS (ETA ≤ 15s)") >> proxy
    operador >> Edge(label="HTTPS Admin") >> proxy

    proxy >> Edge(label="ASGI Reverse Proxy") >> app

    app >> Edge(label="XADD (<1ms)") >> cache
    cache >> Edge(label="consume stream") >> geo_worker
    geo_worker >> Edge(label="actualiza estado") >> cache
    cache >> Edge(label="batch read") >> batch_worker
    batch_worker >> Edge(label="COPY c/5s") >> db

    app >> Edge(label="catálogo / rutas") >> db
    cache >> Edge(label="Pub/Sub broadcast") >> app

    app >> Edge(label="métricas /metrics", style="dotted") >> prom
    pasajeros >> Edge(label="descarga mapas", style="dashed") >> osm
    app >> Edge(label="despacha alertas", style="dashed") >> push
