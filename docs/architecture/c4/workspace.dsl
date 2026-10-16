workspace "RutaSIT Arequipa" "Modelo C4 del sistema de seguimiento y monitoreo en tiempo real del transporte urbano de Arequipa" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero del SIT" "Usuario del transporte público de Arequipa que consulta rutas, paraderos y tiempo de llegada de buses."
        operador = person "Operador del Centro de Control" "Personal técnico del SIT que supervisa el cumplimiento de frecuencias, estado de flota y desvíos."

        rutasit = softwareSystem "RutaSIT Arequipa" "Permite el monitoreo en tiempo real de 300 buses, cálculo de tiempos de llegada (ETA) y detección de desvíos en el Sistema Integrado de Transporte de Arequipa." {
            pwa = container "Aplicación Web Progresiva" "Interfaz móvil y web para pasajeros; consulta de rutas, paraderos y tiempo de llegada en vivo con Leaflet." "React + TypeScript + Leaflet" "Web Browser"
            panel = container "Panel Web de Operaciones" "Panel para supervisores del SIT; visualización de flota en mapa, frecuencias y gestión de contingencias." "React + Vite + TailwindCSS" "Web Browser"
            api = container "API Monolito Asíncrono" "Monolito modular que procesa telemetría GPS, expone endpoints REST y canaliza WebSockets de tiempo real." "Python 3.11+ / FastAPI (ASGI)" {
                ingesta = component "Módulo Ingesta GPS" "Recepciona y valida tramas de telemetría de 300 buses; realiza triage rápido y encola en Redis Streams." "FastAPI APIRouter"
                eta = component "Módulo Estimación ETA y Geocercas" "Calcula tiempos estimados de arribo, verifica proximidad a paraderos y detecta desvíos de ruta." "Python Service (Spatial Engine)"
                notificaciones = component "Módulo Notificaciones y Tiempo Real" "Canaliza eventos por WebSockets hacia la PWA y panel de operaciones, e invoca alertas push." "FastAPI WebSocket Manager"
                catalogo = component "Módulo Catálogo SIT" "Gestiona información de rutas troncales/alimentadoras, paraderos oficiales y frecuencias programadas." "FastAPI APIRouter / SQL Repository"
                supervision = component "Módulo Supervisión de Flota" "Consolida indicadores operativos, puntualidad, velocidades y monitoreo en vivo para operadores." "FastAPI APIRouter / Dashboard Service"
            }
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

        # Relaciones del Nivel 3 (Componentes de la API)
        rutasit.pwa -> rutasit.api.catalogo "Consulta rutas y paraderos disponibles" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.eta "Solicita cálculo de tiempo de llegada al paradero" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.notificaciones "Recibe flujo continuo de posiciones y eventos de bus" "WSS"

        rutasit.panel -> rutasit.api.supervision "Consulta indicadores y estado operativo de la flota" "HTTPS/JSON"
        rutasit.panel -> rutasit.api.notificaciones "Recibe alertas de desvío y contingencias operativas" "WSS"

        gps -> rutasit.api.ingesta "Envía tramas de telemetría cada 10 s" "HTTPS/JSON"

        rutasit.api.ingesta -> rutasit.redis "Encola tramas crudas en buffer de telemetría" "Redis Streams (XADD)"
        rutasit.api.eta -> rutasit.api.ingesta "Lee tramas de telemetría validadas (IProveedorGPS)"
        rutasit.api.eta -> rutasit.api.catalogo "Consulta trazado de rutas y coordenadas de paraderos"
        rutasit.api.eta -> rutasit.redis "Almacena última posición y ETA calculado" "Redis protocol"

        rutasit.api.notificaciones -> rutasit.api.eta "Escucha cambios de estado y desvíos detectados"
        rutasit.api.notificaciones -> rutasit.redis "Consume eventos del canal Pub/Sub" "Redis protocol"
        rutasit.api.notificaciones -> push "Despacha alertas críticas de retraso o desvío" "HTTPS/JSON"

        rutasit.api.supervision -> rutasit.api.eta "Consulta estado de viajes en curso (solo lectura)"
        rutasit.api.supervision -> rutasit.api.catalogo "Consulta programación y frecuencias oficiales (solo lectura)"

        rutasit.api.catalogo -> rutasit.db "Consulta y persiste geometrías de paraderos y rutas" "SQL/TCP (PostGIS)"

        # Entorno de Despliegue en Producción (MVP)
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Dispositivo del Pasajero" "" "Smartphone Android / iOS" {
                deploymentNode "Navegador Web / PWA Engine" "" "Chrome / Safari / Service Worker" {
                    containerInstance rutasit.pwa
                }
            }

            deploymentNode "Estación del Centro de Control" "" "PC / Laptop de Operaciones" {
                deploymentNode "Navegador Web" "" "Google Chrome / Firefox" {
                    containerInstance rutasit.panel
                }
            }

            deploymentNode "Servidor VPS en la Nube" "" "Ubuntu 24.04 LTS, 4 vCPU, 8 GB RAM (≤ $12 USD/mes)" {
                deploymentNode "Docker Compose" "" "Docker Engine 27.x" {
                    containerInstance rutasit.api
                    containerInstance rutasit.worker
                    containerInstance rutasit.redis
                    containerInstance rutasit.db
                }
            }
        }
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

        component rutasit.api "Componentes" "Nivel 3: Diagrama de Componentes del contenedor API Monolito Asíncrono." {
            include *
            autolayout lr
        }

        dynamic rutasit.api "ConsultarTiempoLlegada" "Dinámico: consulta de tiempo estimado de llegada (ETA) de un bus a un paradero." {
            rutasit.pwa -> rutasit.api.catalogo "1. Consulta paraderos y rutas disponibles"
            rutasit.pwa -> rutasit.api.eta "2. Solicita cálculo de tiempo de llegada al paradero"
            rutasit.api.eta -> rutasit.api.catalogo "3. Consulta trazado de rutas y coordenadas de paraderos"
            rutasit.api.eta -> rutasit.api.ingesta "4. Lee tramas de telemetría validadas (IProveedorGPS)"
            rutasit.api.eta -> rutasit.redis "5. Almacena última posición y ETA calculado"
            rutasit.api.notificaciones -> rutasit.api.eta "6. Escucha cambios de estado y desvíos detectados"
            rutasit.api.notificaciones -> push "7. Despacha alertas críticas de retraso o desvío"
            rutasit.pwa -> rutasit.api.notificaciones "8. Recibe flujo continuo de posiciones y eventos de bus"
            autolayout lr
        }

        deployment rutasit produccion "Despliegue" "Nivel 5: Vista de Despliegue en entorno de Producción (MVP en 1 VPS)." {
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
