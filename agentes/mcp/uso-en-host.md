# E5. Servidor conectado a un host real: Claude Code

Configuración en la raíz del repositorio (`.mcp.json`; para VS Code + Copilot se dejó `.vscode/mcp.json`):

```json
{ "mcpServers": { "rutasit": { "type": "stdio", "command": ".venv/bin/python",
                               "args": ["agentes/mcp/servidor_mcp/rutasit_mcp.py"] } } }
```

Las consultas se ejecutaron con Claude Code 2.1 en modo no interactivo, conectando **solo** este servidor y
permitiendo de inicio únicamente las herramientas de lectura:

```bash
claude -p "<consulta>" --strict-mcp-config --mcp-config .mcp.json \
  --allowedTools "mcp__rutasit__buses_en_ruta mcp__rutasit__tiempo_llegada mcp__rutasit__verificar_desvio ReadMcpResourceTool"
```

Las transcripciones resumidas están en `evidencias/host/q*.txt`.

| # | Consulta (lenguaje natural) | Herramientas que eligió el host | ¿Pidió permiso? | Resultado |
|---|---|---|---|---|
| 1 | ¿Qué buses circulan en la ruta R-01 y en qué estado? | `buses_en_ruta(R-01)` | No (lectura) | Correcto: B-011 y B-012 EN_RUTA, B-013 DESVIADO. |
| 2 | Son las 18:10 (hora punta), ¿cuánto tarda B-021 en llegar a Av. Independencia? | 1.ª vez: `buses_en_ruta` + **grep en el repo** para hallar el ID + `tiempo_llegada`. 2.ª vez (descripción mejorada): `ReadMcpResource(rutasit://rutas/mapa)` + `buses_en_ruta` + `tiempo_llegada(P-203, HORA_PUNTA)` | No | Correcto: 24 min, 18:34. Ver hallazgo 1. |
| 3 | ¿B-013 y B-022 están desviados? | `verificar_desvio` ×2 | No | B-013 desviado; B-022 sin GPS: el host leyó el error y lo explicó sin inventar. |
| 4 | `/mcp__rutasit__aviso_usuarios R-01 "obras en el Puente Grau..."` (**prompt** del servidor) | Ninguna (prompt) | No | Aviso de ~200 caracteres. Ver hallazgo 2. |
| 5 | Registra un reporte de desvío para B-013 | `buses_en_ruta`, `verificar_desvio`, `reportar_desvio` | **Sí** | 1.ª ejecución: bloqueado ("Claude requested permissions to use mcp__rutasit__reportar_desvio"). 2.ª ejecución con el permiso aprobado por el operador: creó `reportes/DESVIO-02.md`. |

## Hallazgos

1. **El host buscó el ID en el código.** En la consulta 2 Claude Code no leyó el recurso del mapa: usó `grep`
   sobre el repositorio para hallar `P-203`. Funcionó, pero el host salió del servidor MCP. Se agregó a la
   descripción de `tiempo_llegada` "id_paradero: P-NNN (ver recurso rutasit://rutas/mapa)" y, al repetir,
   el host leyó el recurso y no tocó el repositorio.
2. **Argumentos de prompts con espacios.** Al invocar el prompt con barra, Claude Code partió el argumento en los
   espacios y la plantilla recibió solo `"obras`. El host lo notó y usó el texto completo. Conviene que los
   prompts tengan argumentos cortos o un único argumento de texto libre al final.
3. **La aprobación funciona por anotaciones y permisos del host.** La escritura no se ejecutó hasta que el operador
   la autorizó; las lecturas no pidieron nada.
