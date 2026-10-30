# ADR-008: Aislamiento Multitenant de Consorcios con Row-Level Security y Claims JWT (QA-05 / QA-07)

- **Estado:** Aceptado
- **Fecha:** 2026-10-29
- **Decisores:** Anderson Lino Arce Valencia (Arquitecto Líder), Wilson Freddy Carlos Ccamaqque (Desarrollador)

## Contexto
El SIT Arequipa opera mediante múltiples empresas y consorcios concesionarios competidores (Arequipa Bus, Tranvía, Cono Norte, etc.). La regulación municipal prohíbe terminantemente la fuga de datos operativos entre empresas (`[QA-05]`), al tiempo que exige incorporar nuevos consorcios o ampliaciones de ruta en un plazo no mayor a 2 días (`[QA-07]`).

## Alternativas consideradas
1. **Base de Datos por Consorcio:** Rechazado por consumo desmedido de memoria RAM en el VPS y dificultad de ejecutar migraciones en paralelo.
2. **Esquema PostgreSQL por Consorcio:** Rechazado por complejidad para reportes globales consolidados de la Municipalidad Provincial de Arequipa.
3. **Columna `consorcio_id` + Row-Level Security (RLS) en PostgreSQL + Claims en JWT:** Aceptado.

## Decisión
1. Todo usuario u operador se autentica mediante JWT conteniendo el claim firmado `consorcio_id`.
2. Las tablas de telemetría, asignación de buses y choferes activan **Row-Level Security (RLS)** en PostgreSQL a nivel de motor de base de datos.
3. La configuración de conexión establece `SET LOCAL app.current_consorcio_id = :id` al inicio de cada transacción.

## Evidencia y Consecuencias
- **Evidencia:** Pruebas de seguridad automatizadas (`tests/test_fitness.py`) validaron que un consorcio no puede acceder bajo ninguna circunstancia a los buses ni métricas de otro.
- **Tiempo de onboarding:** Incorporar un nuevo consorcio toma menos de 15 minutos (insertar una fila en la tabla maestra de consorcios y generar credenciales), cumpliendo el límite de $\le 2\text{ días}$.
- **Consecuencias Positivas:** Aislamiento robusto a nivel de kernel de base de datos, arquitectura limpia sin overhead de infraestructura.
- **Consecuencias Negativas / Trade-off:** Requiere rigurosidad en las pruebas de configuración de RLS y mantenimiento de la directiva de sesión transaccional.
