workspace "RutaSIT Arequipa" "Modelo C4 del sistema de seguimiento y monitoreo en tiempo real del transporte urbano de Arequipa" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero del SIT" "Usuario del transporte público de Arequipa que consulta rutas, paraderos y tiempo de llegada de buses."
        operador = person "Operador del Centro de Control" "Personal técnico del SIT que supervisa el cumplimiento de frecuencias, estado de flota y desvíos."

        rutasit = softwareSystem "RutaSIT Arequipa" "Permite el monitoreo en tiempo real de 300 buses, cálculo de tiempos de llegada (ETA) y detección de desvíos en el Sistema Integrado de Transporte de Arequipa."

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
    }

    views {
        systemContext rutasit "Contexto" "Nivel 1: Contexto del sistema RutaSIT Arequipa y su entorno operativo." {
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
