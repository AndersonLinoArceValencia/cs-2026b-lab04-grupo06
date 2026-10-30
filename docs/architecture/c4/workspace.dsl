workspace "RutaSIT Arequipa" "Modelo C4 del sistema de seguimiento y monitoreo en tiempo real del transporte urbano de Arequipa (1200 buses, 50k consultas)" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero del SIT" "Usuario del transporte público de Arequipa que consulta rutas, paraderos y tiempo de llegada de buses en hora punta [QA-01]."
        operador = person "Operador de Consorcio / Centro de Control" "Personal técnico que supervisa flota, frecuencias y contingencias del consorcio asignado [QA-05]."

        rutasit = softwareSystem "RutaSIT Arequipa" "Monitoreo en tiempo real de 1200 buses, estimación de llegada (ETA) y detección de desvíos en el Sistema Integrado de Transporte de Arequipa." {
            pwa = container "Aplicación Web Progresiva" "Interfaz móvil y web para pasajeros; consulta paraderos y tiempo de llegada en vivo con Leaflet y caché offline IndexedDB [QA-01, QA-03]." "React + TypeScript + Leaflet" "Web Browser"
            panel = container "Panel Web de Operaciones" "Panel para supervisores del SIT; visualización de flota en mapa y gestión de flota por consorcio [QA-05]." "React + Vite + TailwindCSS" "Web Browser"
            api = container "API Monolito Asíncrono" "Monolito modular con 4 workers ASGI; procesa telemetría de 1200 buses [QA-02] y aísla consorcios con RLS [QA-05]." "Python 3.12 / FastAPI (ASGI)" {
                ingesta = component "Módulo Ingesta GPS" "Recepciona y valida telemetría de 1200 buses con Decorator Circuit Breaker [QA-02, QA-03]." "FastAPI APIRouter"
                eta = component "Módulo Estimación ETA y Caché" "Calcula tiempos estimados de llegada con motor Strategy e índices en BD; almacena en caché [QA-01, QA-08]." "Python Service (Spatial Engine)"
                notificaciones = component "Módulo Notificaciones" "Canaliza eventos por WebSockets hacia la PWA y panel de operaciones [QA-01]." "FastAPI WebSocket Manager"
                catalogo = component "Módulo Catálogo SIT" "Gestiona rutas troncales y alimentadoras, paraderos e información multitenant de consorcios [QA-05, QA-07]." "FastAPI APIRouter / SQL Repository"
                supervision = component "Módulo Supervisión de Flota" "Consolida indicadores operativos, puntualidad y velocidades con aislamiento RLS [QA-05]." "FastAPI APIRouter / Dashboard Service"
                resiliencia = component "Módulo Circuit Breaker y Outbox" "Decorator sobre adaptadores GPS que protege ante caídas de red y encola en outbox [QA-03]." "Python Resilience Decorator"
            }
            worker = container "Worker Espacial y Outbox" "Proceso asíncrono para drenaje de la cola outbox tras reconexión [QA-03] y cálculo batch de geocercas." "Python / Background Worker"
            redis = container "Caché de Estimaciones y Buffer" "Caché en memoria para tiempos de llegada con TTL de 10s [QA-01] y buffer temporal de telemetría." "Redis 7.x" "Queue"
            db = container "Base de Datos Geoespacial y Outbox" "PostgreSQL 16 con PostGIS, tabla outbox para resiliencia [QA-03] y políticas Row-Level Security por consorcio [QA-05]." "PostgreSQL 16 + PostGIS 3.4" "Database"
        }

        gps = softwareSystem "Dispositivos GPS Embarcados" "Equipos GPS en 1200 buses emitiendo telemetría cada 5 s (240 ev/s) [QA-02]." "Externo"
        osm = softwareSystem "Servidor OpenStreetMap" "Proveedor de cartografía abierta y teselas geográficas para visualización de mapas." "Externo"
        push = softwareSystem "Servicio Web Push" "Plataforma de mensajería para despacho de alertas masivas e incidencias a pasajeros y operadores." "Externo"

        # Relaciones del Nivel 1 (Contexto del Sistema)
        pasajero -> rutasit "Consulta rutas, paraderos y tiempos estimados de llegada [QA-01]"
        operador -> rutasit "Supervisa ubicación de flota y cumplimiento de su consorcio [QA-05]"
        gps -> rutasit "Envía telemetría de 1200 buses cada 5 s (~240 req/s) [QA-02]"
        rutasit -> osm "Solicita mapas base y teselas para georreferenciación"
        rutasit -> push "Solicita envío de notificaciones de contingencia y retrasos"
        pasajero -> osm "Descarga capas cartográficas y teselas de mapa para visualización"

        # Relaciones del Nivel 2 (Contenedores)
        pasajero -> rutasit.pwa "Consulta paraderos y visualiza buses en tiempo real [QA-01]" "HTTPS"
        operador -> rutasit.panel "Monitorea flota de su consorcio en tiempo real [QA-05]" "HTTPS"

        rutasit.pwa -> rutasit.api "Consulta catálogo REST y recibe telemetría en vivo [QA-01]" "HTTPS / WSS"
        rutasit.panel -> rutasit.api "Solicita métricas de flota con token JWT [QA-05]" "HTTPS / WSS"

        gps -> rutasit.api "Envía tramas de telemetría cada 5 s [QA-02]" "HTTPS/JSON"
        rutasit.api -> rutasit.redis "Lee y escribe estimaciones en caché (TTL 10s) [QA-01]" "Redis protocol"
        rutasit.api -> rutasit.db "Consulta datos con índice y persiste en outbox ante caídas [QA-01, QA-03, QA-05]" "SQL/TCP"

        rutasit.worker -> rutasit.db "Drena tabla outbox_telemetria hacia histórico [QA-03]" "SQL/TCP"
        rutasit.worker -> rutasit.redis "Consume eventos del buffer de telemetría" "Redis protocol"

        # Relaciones del Nivel 3 (Componentes)
        rutasit.pwa -> rutasit.api.catalogo "Consulta paraderos y trazado de rutas [QA-01]" "HTTPS/REST"
        rutasit.pwa -> rutasit.api.eta "Solicita cálculo de tiempo de llegada al paradero [QA-01]" "HTTPS/REST"
        rutasit.pwa -> rutasit.api.notificaciones "Suscribe a WebSocket de eventos de viaje" "WSS"

        rutasit.panel -> rutasit.api.supervision "Consulta dashboard operativo filtrado por consorcio_id [QA-05]" "HTTPS/REST"

        gps -> rutasit.api.ingesta "Envía tramas de telemetría cada 5 s [QA-02]" "HTTPS/JSON"
        rutasit.api.ingesta -> rutasit.api.resiliencia "Valida disponibilidad mediante Circuit Breaker [QA-03]"
        rutasit.api.resiliencia -> rutasit.db "Persiste tramas en outbox si el circuito está abierto [QA-03]" "SQL/TCP"
        rutasit.api.ingesta -> rutasit.redis "Encola tramas crudas en buffer de telemetría" "Redis Streams"

        rutasit.api.eta -> rutasit.api.catalogo "Consulta coordenadas de paraderos y rutas"
        rutasit.api.eta -> rutasit.redis "Consulta y almacena estimaciones de llegada [QA-01]" "Redis protocol"
        rutasit.api.eta -> rutasit.db "Consulta histórico con índice (linea_id, parada_id) [QA-01]" "SQL/TCP"

        rutasit.api.notificaciones -> rutasit.api.eta "Escucha cambios de estado y desvíos detectados"
        rutasit.api.notificaciones -> push "Despacha alertas críticas de retraso o desvío" "HTTPS/JSON"

        rutasit.api.supervision -> rutasit.api.catalogo "Consulta programación filtrada por consorcio [QA-05]"

        # Entorno de Despliegue en Producción
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Dispositivo del Pasajero" "" "Smartphone Android / iOS" {
                deploymentNode "Navegador Web / PWA Engine" "" "Chrome / Safari / Service Worker con IndexedDB [QA-03]" {
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
        systemContext rutasit "Contexto" "Nivel 1: Contexto del sistema RutaSIT Arequipa y trazabilidad a escenarios." {
            include *
            autolayout lr
        }

        container rutasit "Contenedores" "Nivel 2: Diagrama de Contenedores con trazabilidad [QA-01, QA-02, QA-03, QA-05]." {
            include *
            autolayout lr
        }

        component rutasit.api "Componentes" "Nivel 3: Diagrama de Componentes con Circuit Breaker, Outbox y Caché." {
            include *
            autolayout lr
        }

        deployment rutasit produccion "Despliegue" "Nivel 5: Vista de Despliegue en VPS único optimizado." {
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
