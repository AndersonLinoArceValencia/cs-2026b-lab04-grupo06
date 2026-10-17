# Inventario de Elementos de Arquitectura — Modelo C4 (RutaSIT Arequipa)

Este documento registra el inventario completo de elementos que componen el modelo C4 del sistema **RutaSIT Arequipa**, estableciendo su trazabilidad rigurosa con los artefactos de diseño y arquitectura construidos en los **Laboratorios 04 y 05**.

---

## Tabla de Mapeo de Elementos y su Origen

| Elemento | Tipo C4 | Descripción en el Dominio | Origen en Lab 04 / Lab 05 |
| :--- | :--- | :--- | :--- |
| **Pasajero del SIT** | Persona | Usuario del transporte público de Arequipa que consulta rutas, paraderos y tiempo de llegada de buses. | `drivers.md` (RF-02), `historia.md` (HU-01), `clases.puml` |
| **Operador del Centro de Control** | Persona | Personal técnico del SIT que supervisa el cumplimiento de frecuencias, estado de flota y desvíos. | `drivers.md` (RF-05), `arquitectura.mmd`, `PROPUESTA_PROYECTO.md` |
| **Conductor del Bus** | Persona (no modelada) | Conductor que opera la unidad de transporte; se omite del DSL porque no interactúa con el sistema (el GPS embarcado emite la telemetría). | `drivers.md`, `bitacora-ia.md` |
| **RutaSIT Arequipa** | Sistema de software | Sistema central de seguimiento y monitoreo en tiempo real para 300 buses del SIT de Arequipa. | `PROPUESTA_PROYECTO.md`, `drivers.md`, `matriz-decision.md` |
| **Dispositivos GPS Embarcados** | Sistema externo | Dispositivos GPS instalados en 300 buses que emiten tramas de telemetría HTTP cada 10 s (~30 req/s). | `drivers.md` (RF-01, QA-01), `ADR-003`, `arquitectura.mmd` |
| **Servidor OpenStreetMap / CDN Tiles** | Sistema externo | Proveedor de cartografía abierta y teselas de mapa para visualización sin costos de licenciamiento. | `ADR-002`, `drivers.md` (R-04), `arquitectura.mmd` |
| **Servicio Web Push / Alertas** | Sistema externo | Servicio de mensajería para despacho de notificaciones push de incidencias y desvíos a usuarios. | `arquitectura.mmd`, `drivers.md` (RF-04), `ADR-003` |
| **PWA Pasajeros** | Contenedor | Aplicación Web Progresiva ligera con Leaflet.js para consulta de paraderos y ETA en tiempo real. | `ADR-001`, `despliegue.py`, `PROPUESTA_PROYECTO.md` |
| **Panel Web de Operaciones** | Contenedor | Aplicación web para visualización geográfica de flota, alarmas de desvío e indicadores operativos. | `arquitectura.mmd`, `despliegue.py`, `PROPUESTA_PROYECTO.md` |
| **API Monolito Asíncrono** | Contenedor | Backend central en Python FastAPI (ASGI) que expone endpoints REST y WebSockets de telemetría. | `ADR-001`, `ADR-003`, `despliegue.py`, `clases.puml` |
| **Worker Espacial y Batch** | Contenedor | Proceso worker en segundo plano para cálculo geométrico intensivo y consolidación de datos históricos. | `ADR-001`, `demostracion-abogado-del-diablo.md`, `despliegue.py` |
| **Caché y Buffer en Memoria (Redis)** | Contenedor | Redis Streams (buffer de telemetría), caché de última posición (TTL) y Pub/Sub de eventos en vivo. | `ADR-001`, `ADR-003`, `despliegue.py` |
| **Base de Datos Geoespacial (PostgreSQL + PostGIS)** | Contenedor | Almacén relacional espacial con esquemas para catálogo vial (rutas, paraderos) e histórico consolidado. | `ADR-001`, `ADR-002`, `despliegue.py` |
| **Módulo Ingesta GPS** | Componente | Submódulo dentro de la API encargado de recibir, validar tramas GPS y encolarlas en Redis Streams. | `arquitectura.mmd` (M1), `PROPUESTA_PROYECTO.md` |
| **Módulo Estimación ETA y Geocercas** | Componente | Submódulo que calcula el tiempo estimado de arribo a paraderos y detecta desvíos de ruta. | `arquitectura.mmd` (M2), `clases.puml`, `secuencia-consultar-tiempo.puml` |
| **Módulo Tiempo Real y Notificaciones** | Componente | Submódulo que gestiona conexiones WebSockets masivas y publica actualizaciones hacia los clientes. | `arquitectura.mmd` (M3), `ADR-003`, `PROPUESTA_PROYECTO.md` |
| **Módulo Catálogo SIT** | Componente | Submódulo de administración y consulta de paraderos, rutas troncales/alimentadoras y horarios. | `arquitectura.mmd` (M4), `clases.puml`, `PROPUESTA_PROYECTO.md` |
| **Módulo Supervisión de Flota** | Componente | Submódulo que genera métricas de puntualidad, velocidad y control de frecuencias para operadores. | `arquitectura.mmd` (M5), `PROPUESTA_PROYECTO.md` |
| **Flujo "Consultar tiempo de llegada"** | Vista dinámica | Secuencia de interacciones paso a paso para la consulta de ETA por parte del pasajero ante un paradero. | `historia.md` (HU-01), `secuencia-consultar-tiempo.puml` |
| **Entorno Producción (VPS 1)** | Vista de despliegue | Un único VPS Linux (Ubuntu 24.04, 2-4 vCPU, 4-8 GB RAM, $\le \$12$/mes) gestionado con Docker Compose. | `drivers.md` (R-03), `despliegue.py`, `ADR-001` |
