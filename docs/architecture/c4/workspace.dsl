workspace "RutaSIT Arequipa" "Modelo C4 del sistema de seguimiento y monitoreo en tiempo real del transporte urbano de Arequipa" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero del SIT" "Usuario del transporte público de Arequipa que consulta rutas, paraderos y tiempo de llegada de buses."
        operador = person "Operador del Centro de Control" "Personal técnico del SIT que supervisa el cumplimiento de frecuencias, estado de flota y desvíos."

        rutasit = softwareSystem "RutaSIT Arequipa" "Permite el monitoreo en tiempo real de 300 buses, cálculo de tiempos de llegada (ETA) y detección de desvíos en el Sistema Integrado de Transporte de Arequipa." {
            pwa = container "Aplicación Web Progresiva" "Interfaz móvil y web para pasajeros; consulta de rutas, paraderos y tiempo de llegada en vivo con Leaflet." "React + TypeScript + Leaflet" "Web Browser"
            panel = container "Panel Web de Operaciones" "Panel para supervisores del SIT; visualización de flota en mapa, frecuencias y gestión de contingencias." "React + Vite + TailwindCSS" "Web Browser"
            api = container "API Monolito Asíncrono" "Monolito modular que procesa telemetría GPS, expone endpoints REST y canaliza WebSockets de tiempo real." "Python 3.11+ / FastAPI (ASGI)"
            worker = container "Worker Espacial y Batch" "Proceso asíncrono para cálculo geométrico de geocercas, estimación de ETA y persistencia en lote." "Python / Background Worker"
            redis = container "Caché y Buffer en Memoria" "Buffer de telemetría (Streams), caché de última posición de buses (TTL) y Pub/Sub de eventos." "Redis 7.x" "Queue"
            db = container "Base de Datos Geoespacial" "Almacén relacional con extensión PostGIS para catálogo vial (rutas, paraderos) e histórico consolidado." "PostgreSQL 16 + PostGIS 3.4" "Database"
        }

        gps = softwareSystem "Dispositivos GPS Embarcados" "Equipos GPS instalados en 300 buses que emiten tramas de telemetría y geolocalización continua." "Externo"
        osm = softwareSystem "Servidor OpenStreetMap" "Proveedor de cartografía abierta y teselas geográficas para visualización de mapas." "Externo"
        push = softwareSystem "Servicio Web Push" "Plataforma de mensajería para despacho de alertas masivas e incidencias a pasajeros y operadores." "Externo"

        # Relaciones del Nivel 1 (Contexto del Sistema)
        pasajero -> rutasit "Consulta rutas, paraderos y tiempos estimados de llegada"
        operador -> rutasit "Supervisa ubicación de flota, cumplimiento de frecuencias y alertas de desvío"
        gps -> rutasit "Envía tramas continuas de telemetría y posición GPS de los buses"
        rutasit -> osm "Solicita mapas base y teselas para georreferenciación de unidades y paraderos"
        rutasit -> push "Solicita envío de notificaciones de contingencia y retrasos"
        pasajero -> osm "Descarga capas cartográficas y teselas de mapa para visualización"

        # Relaciones del Nivel 2 (Contenedores)
        pasajero -> rutasit.pwa "Consulta paraderos y visualiza buses en tiempo real" "HTTPS"
        operador -> rutasit.panel "Monitorea flota en tiempo real y gestiona desvíos" "HTTPS"

        rutasit.pwa -> rutasit.api "Consulta catálogo REST y recibe telemetría en vivo" "HTTPS / WSS"
        rutasit.panel -> rutasit.api "Solicita métricas de flota y recibe eventos de contingencia" "HTTPS / WSS"

        gps -> rutasit.api "Envía tramas de telemetría y coordenadas GPS cada 10 s (~30 req/s)" "HTTPS/JSON"
        rutasit.api -> rutasit.redis "Encola telemetría en buffer (Streams) y consulta última posición de buses" "Redis protocol"
        rutasit.api -> rutasit.db "Consulta información de rutas y paraderos" "SQL/TCP"

        rutasit.worker -> rutasit.redis "Consume telemetría (Streams) y publica alertas/ETA calculados (Pub/Sub)" "Redis protocol"
        rutasit.worker -> rutasit.db "Persiste histórico consolidado de telemetría por lotes cada 5 s" "SQL/TCP"
        rutasit.worker -> push "Despacha notificaciones de desvío y retrasos a pasajeros" "HTTPS/JSON"

        rutasit.pwa -> osm "Descarga teselas y capas cartográficas para el mapa" "HTTPS"
        rutasit.panel -> osm "Descarga teselas de mapa para visualización de flota" "HTTPS"
    }

    views {
        systemContext rutasit "Contexto" "Nivel 1: Contexto del sistema RutaSIT Arequipa y su entorno operativo." {
            include *
            autolayout lr
        }

        container rutasit "Contenedores" "Nivel 2: Diagrama de Contenedores del sistema RutaSIT Arequipa." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}
