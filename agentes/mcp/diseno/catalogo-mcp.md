# E1. Catálogo MCP del servidor `rutasit` (caso 6: RutaSIT Arequipa)

El servidor expone el monitoreo de buses del SIT a cualquier host MCP reutilizando el dominio existente
(`src/monitoreo/llegada.py`, `src/monitoreo/desvios.py`, `src/monitoreo/estrategias.py`). No duplica lógica:
cada herramienta valida la entrada, llama al dominio y da forma a la salida. Todos los datos son ficticios
(`servidor_mcp/datos_rutasit.py`).

## Qué se expone y con qué primitiva

| Capacidad | Primitiva | ¿Escribe? | Justificación |
|---|---|---|---|
| Buses de una ruta con estado, km y velocidad | Herramienta `buses_en_ruta(id_ruta)` | No | Consulta con un parámetro que el modelo elige; salida estructurada `BusesRuta`. |
| Tiempo de llegada de un bus a un paradero | Herramienta `tiempo_llegada(id_bus, id_paradero, hora_actual, estrategia)` | No | Cálculo con parámetros; reutiliza `estimar_hora_llegada` y `FabricaEstrategiasETA`. |
| ¿Está desviado un bus? | Herramienta `verificar_desvio(id_bus)` | No | Cálculo geométrico de `evaluar_desvio_ruta` (umbral 50 m). |
| Reportar un desvío al centro de control | Herramienta `reportar_desvio(id_bus, descripcion)` ★ | Sí, solo crea | Única escritura: crea `reportes/DESVIO-NN.md` con `open(..., "x")`; nunca edita ni borra. |
| Reglas del equipo | Recurso `rutasit://agents-md` | No | Contexto estable; lo decide el host. |
| Mapa de rutas y paraderos | Recurso `rutasit://rutas/mapa` (JSON) | No | Contexto estable: IDs de paraderos y km de cada ruta. |
| Decisiones de arquitectura | Recurso plantilla `rutasit://adr/{numero}` | No | ADR por número de 3 dígitos; rechaza rutas como `../../.env`. |
| Aviso a usuarios | Prompt `aviso_usuarios(id_ruta, motivo)` | No | Plantilla que el usuario invoca (comando con barra en el host). |
| Revisar un cambio | Prompt `revisar_cambio(diff)` | No | Plantilla del Lab 09. |

## Descripciones (escritas antes de programar)

- **buses_en_ruta**: buses de una ruta (`R-01`, `R-02`) con estado (`EN_RUTA`, `DETENIDO`, `DESVIADO`), km recorrido y velocidad. Error útil si la ruta no existe (lista las válidas).
- **tiempo_llegada**: minutos y hora de llegada. `id_paradero` con formato `P-NNN` (ver `rutasit://rutas/mapa`), `hora_actual` con formato `AAAA-MM-DDTHH:MM`, `estrategia` en `LINEAL`, `HORA_PUNTA` o `PARADAS_INTERMEDIAS`. Devuelve `EN_CAMINO`, `YA_PASO` o `SIN_GPS`.
- **verificar_desvio**: `desviado = true/false` respecto al trazado; falla con un mensaje claro si el bus no tiene GPS.
- **reportar_desvio**: crea un archivo nuevo; `descripcion` entre 10 y 500 caracteres (qué, dónde, desde qué hora). `maxLength` publicado en el esquema.

## Por qué la escritura no puede causar daño irreversible

1. Solo crea archivos: usa el modo `"x"` de `open`, que falla si el archivo existe, y calcula el siguiente número libre.
2. Escribe en una única carpeta fija (`agentes/mcp/reportes/`); el nombre lo arma el servidor, no el modelo.
3. Valida el bus contra el catálogo y limita la descripción a 500 caracteres (no sirve para volcar contexto).
4. Está anotada con `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, así el host pide aprobación humana.
5. Un reporte erróneo se corrige creando otro; nada existente se pierde.
