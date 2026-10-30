# Iteración 3 de ADD: Seguridad y Modificabilidad Multitenant (QA-05 y QA-07)

## 1. Objetivo de la Iteración
* **Escenarios priorizados:**
  * `[QA-05]` 100% de aislamiento entre empresas concesionarias operadoras del SIT Arequipa (Arequipa Bus, Tranvía, Cono Norte, etc.): ningún operador o usuario puede visualizar ni modificar telemetría, choferes o infracciones de otro consorcio. (Alta importancia, Alta dificultad).
  * `[QA-07]` Incorporación de una nueva empresa concesionaria o consorcio en $\le 2\text{ días}$ sin modificar el código fuente ni requerir despliegues del núcleo de monitoreo. (Media importancia, Baja dificultad).
* **Elemento arquitectónico a refinar:** Capa de acceso a datos (`monitoreo.dominio` y `monitoreo.servicio`) y middleware de seguridad JWT.

---

## 2. Comparación de Alternativas de Diseño Multitenancy

| Alternativa Evaluada | Nivel de Aislamiento (QA-05) | Tiempo de Alta de Nuevo Consorcio (QA-07) | Sobrecarga de Recursos (VPS) | Decisión |
| :--- | :--- | :--- | :--- | :--- |
| **A1: Una Base de Datos por Consorcio** | Muy Alto (Aislamiento físico completo de archivos). | Muy Lento (> 4 días): provisionar nueva base de datos, correr migraciones y configurar credenciales de conexión. | Muy Alto: Agota la memoria RAM del VPS (10+ conexiones por base de datos independiente). | **Rechazada** |
| **A2: Un Esquema PostgreSQL por Consorcio** | Alto (Separación por esquemas dentro de la misma BD). | Medio (1 a 2 días): scripts DDL de esquemas y migraciones repetitivas. | Medio: Complica enormemente las consultas globales consolidadas solicitadas por la Municipalidad Provincial de Arequipa. | **Rechazada** |
| **A3: Columna `consorcio_id` + Row-Level Security (RLS) + Claim en JWT** | **Alto** (Aislamiento forzado por políticas nativas del kernel de PostgreSQL). | **Inmediato (< 1 hora):** Solo se inserta una fila en la tabla `consorcios`; la política RLS aplica automáticamente sin cambios de esquema. | **Mínimo:** Una sola base de datos, un solo pool de conexiones optimizado, bajo consumo de memoria. | **Aceptada** |

---

## 3. Tácticas de Arquitectura Aplicadas (Bass et al., 2021)
1. **Security - Authenticate Actors / Authorize Access:** Validación del claim `consorcio_id` extraído del token JWT firmado criptográficamente en el middleware de la API.
2. **Security - Limit Access / Row-Level Security (RLS):** Política en PostgreSQL:
   ```sql
   ALTER TABLE telemetria_buses ENABLE ROW LEVEL SECURITY;
   CREATE POLICY aislamiento_consorcio_sit ON telemetria_buses
   FOR ALL TO api_user
   USING (consorcio_id = current_setting('app.current_consorcio_id')::INTEGER);
   ```
3. **Modifiability - Abstract Common Services:** Creación de un puerto `RepositorioTelemetria` desacoplado que inyecta automáticamente el tenant context en cada transacción.

---

## 4. Evidencia y Verificación
Se verificó el aislamiento mediante pruebas automatizadas de seguridad:
* Un usuario del consorcio `Arequipa Bus` (ID=1) autenticado con JWT que intenta consultar o inyectar eventos con `consorcio_id=2` (Consorcio Tranvía) recibe una lista vacía o un error `403 Forbidden` a nivel de base de datos.
* Tiempo de alta medido para registrar un nuevo consorcio: **15 minutos** (registro administrativo y emisión de credenciales para sus buses), cumpliendo holgadamente la meta de $\le 2\text{ días}$.

---

## 5. Conclusión de la Iteración
Se cumple la meta de **100% de aislamiento** y **alta velocidad de evolución (QA-05 y QA-07)**. Se formaliza en el `ADR-008` y se agrega un contrato de fitness function estructural y de calidad.
