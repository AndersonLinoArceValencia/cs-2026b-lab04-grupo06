# Bitácora de Uso Crítico de Inteligencia Artificial (Lab 05 — Diseño UML)

**Curso:** Construcción de Software (EPIS - UNSA, 2026-B)  
**Grupo:** 06  
**Caso:** 6 — RutaSIT Arequipa  
**Integrantes:**
- Arce Valencia Anderson Lino (Arquitecto Líder & Diagramador)
- Carlos Ccamaqque Wilson Freddy (Evaluador & Verificador de IA)

---

## 1. Registro de Interacciones

| N.º | Fecha | Herramienta | Actividad / Prompt | Propuesta de la IA | Verificación del Equipo (Reglas C1–C5) | Decisión |
|:---:|:---:|:---:|---|---|---|:---:|
| **1** | 07/10/2026 | Gemini 3.1 Pro | **(E1 — Prompt IA 1)** Adaptación del prompt para generar diagrama de clases a partir de `historia.md` y ADR-001. | Generó `clases.puml` con 7 clases/entidades, enumeración `EstadoViaje`, y dos interfaces (`IProveedorGPS`, `IServicioMapas`). | Se revisó que cumpliera con el ADR-001 (arquitectura modular con puertos y adaptadores para no acoplarse a librerías externas de GPS ni mapas). Se verificó que todas las asociaciones tengan multiplicidad en ambos extremos (C5) y no almacenen datos sensibles. Se eliminaron comentarios para mantener el código limpio. | **Aceptada con ajustes** |

---

## 2. Anexo: Detalle del Prompt IA 1 Adaptado

### Interacción 1: Generación del Diagrama de Clases (E1)
* **Fecha:** 07/10/2026
* **Herramienta:** Gemini 3.1 Pro
* **Prompt Adaptado:**
  > "Actúa como diseñador de software orientado a objetos.  
  > Contexto: Módulo de Monitoreo de RutaSIT Arequipa dentro de un monolito modular (ADR-001: puertos y adaptadores para integraciones externas con GPS y servicios de mapas).  
  > Historia y criterios:  
  > [HU-01: Como pasajero del SIT quiero consultar el tiempo estimado de llegada (ETA) de un bus a mi paradero actual...]  
  > Tarea: Genera un diagrama de clases en PlantUML con atributos tipados, operaciones, multiplicidades en ambos extremos, una enumeración para el estado del viaje (`EstadoViaje`: `PROGRAMADO`, `EN_RUTA`, `DESVIADO`, `DETENIDO`, `FINALIZADO`) y dos interfaces (puertos) para el proveedor GPS (`IProveedorGPS`) y el servicio de mapas (`IServicioMapas`)."
* **Resultado:** Diagrama en PlantUML guardado en `docs/design/clases.puml` y renderizado en `docs/design/img/clases.png`.
* **Verificación:** Cumple con 6+ clases, tipado, multiplicidades en ambos extremos y consistencia de nombres con el dominio del SIT Arequipa.
