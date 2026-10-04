# ADR-002: Usar PostgreSQL con PostGIS para los datos geoespaciales y Redis para el estado en vivo

- Estado: Aceptado
- Fecha: 2026-10-04
- Decisores: Arce Valencia Anderson Lino y Carlos Ccamaqque Wilson Freddy (Grupo 06)

## Contexto
RutaSIT Arequipa guarda dos tipos de datos con necesidades muy distintas:

- **Datos de catálogo y geometría**: rutas, paraderos, corredores oficiales y geocercas (RF-06). Cambian poco, pero se consultan con operaciones espaciales: distancia de un bus a un paradero para el ETA (RF-03) y si un bus está a más de 100 m de su corredor (RF-04).
- **Telemetría**: 300 buses × 1 trama cada 10 s = 30 tramas/s, unas 2,6 millones de filas por día (RF-01). El último estado de cada bus se lee constantemente para el mapa (RF-02) y el panel de flota (RF-05).

Los drivers que pesan aquí son QA-01 (propagación en 15 s o menos), QA-03 (agregar una ruta con 20 paraderos sin detener el sistema), R-02 (el equipo domina SQL y bases relacionales) y R-03 (todo en un VPS barato y sin licencias).

## Alternativas consideradas
1. **PostgreSQL 16 + PostGIS, con Redis para el estado caliente.** Consultas espaciales con índices GiST (`ST_DWithin`, `ST_Distance` sobre `geography`), transacciones y SQL que el equipo ya conoce.
2. **MongoDB con índices geoespaciales `2dsphere`.** Esquema flexible y consultas `$near`/`$geoWithin`; pero el equipo no tiene experiencia con él y las relaciones ruta–paradero–frecuencia–tarifa encajan mejor en tablas.
3. **PostgreSQL sin extensión espacial, calculando distancias en Python (Shapely).** Menos piezas que instalar, pero cada consulta "buses cerca de este paradero" obliga a traer muchos puntos a la aplicación y no aprovecha índices espaciales.

## Decisión
Usaremos **PostgreSQL 16 con la extensión PostGIS** como base de datos principal, con un esquema por módulo (`catalogo`, `flota`, `historico`). Las geometrías se guardan en SRID 4326 y las distancias en metros se calculan con el tipo `geography`.

El **último estado de cada bus vive en Redis** (un hash por bus); PostgreSQL no se consulta en cada actualización del mapa. El histórico de telemetría se inserta **por lotes cada 5 s** y la tabla se **particiona por día**, con una política de retención definida con la Gerencia de Transportes de la MPA (R-05).

## Consecuencias
- **Positivas:**
  - La regla de desvío de 100 m (RF-04) y la búsqueda de buses próximos a un paradero (RF-03) se resuelven en una sola consulta indexada.
  - Agregar una ruta nueva es insertar filas y geometrías, sin cambiar código ni reiniciar la ingesta (QA-03).
  - PostgreSQL y PostGIS son software libre (R-03), y el equipo trabaja con SQL desde el primer día (R-02).
  - Leer el estado en vivo desde Redis evita que 1500 pasajeros consultando el mapa golpeen la base de datos.
- **Negativas / riesgos:**
  - PostGIS tiene curva de aprendizaje (SRID, `geometry` frente a `geography`, índices GiST) que el equipo debe cubrir en la primera semana.
  - Hay dos fuentes de verdad para la posición de un bus: Redis tiene la última y PostgreSQL el histórico con hasta 5 s de retraso. Si Redis se reinicia sin AOF, se pierde el estado en vivo hasta rehidratarlo (ver ADR-001).
  - Con unos 2,6 millones de filas diarias, la tabla de histórico crece rápido; sin particiones y retención, el disco del VPS se llenaría en pocos meses.
