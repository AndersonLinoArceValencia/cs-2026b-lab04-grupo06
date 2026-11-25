# ADR-011: Exposición del sistema mediante MCP

- **Estado:** Aceptado
- **Fecha:** 2026-11-25
- **Decisores:** Arce Valencia Anderson Lino, Carlos Ccamaqque Wilson Freddy y Choque Sánchez Alejandra Camila (Grupo 06)

## Contexto

El centro de control quiere consultar buses, tiempos de llegada y desvíos desde el asistente de su IDE, y el
agente del Lab 10 necesita esas mismas capacidades sin que se reescriban como herramientas propias. Sin un
protocolo común, cada host (Claude Code, VS Code con Copilot, el agente propio) necesitaría su adaptador.

## Decisión

Publicar un servidor MCP `rutasit` (`agentes/mcp/servidor_mcp/rutasit_mcp.py`) con el SDK oficial de Python
(`mcp` 2.x, especificación **2026-07-28**) y transporte **stdio**.

- **Se expone:** `buses_en_ruta`, `tiempo_llegada`, `verificar_desvio` (lectura) y `reportar_desvio` (única
  escritura, solo crea archivos); recursos `rutasit://agents-md`, `rutasit://rutas/mapa`, `rutasit://adr/{numero}`;
  prompts `aviso_usuarios` y `revisar_cambio`.
- **No se expone:** edición de código, ejecución de comandos, cambio de estado de viajes, notificaciones reales a
  pasajeros ni datos de GPS reales o placas.
- **Capas:** el servidor vive fuera de `src/` y solo importa funciones del dominio; `src/` no depende de `mcp`,
  así que los contratos FF-01 a FF-03 de `.importlinter` no cambian. Las dependencias del servidor están en
  `agentes/mcp/requirements.txt`, separadas de `calidad/dependencias_aprobadas.txt`.
- **Versión:** acepta clientes 2026-07-28 (`server/discover`, sin sesión) y 2025-11-25 (`initialize`), como se vio
  con MCP Inspector.
- **Seguridad:** anotaciones en todas las herramientas, `maxLength` en la escritura, errores con `ToolError`,
  recursos validados con `\d{3}`, aprobación humana de `reportar_desvio`, auditoría previa de servidores de terceros.

## Alternativas descartadas

1. **API REST directa:** cada host necesitaría un cliente y una descripción propia de los endpoints; no hay
   descubrimiento ni anotaciones para pedir aprobación.
2. **Function calling dentro del agente (Lab 10):** las herramientas quedarían atadas a un solo agente; Copilot o
   Claude Code no podrían usarlas (problema N × M).
3. **Streamable HTTP desde el inicio:** requiere autenticación (OAuth 2.1) y despliegue; se deja para cuando otro
   equipo consuma el servidor por red.

## Consecuencias

- (+) Un solo servidor sirve a Claude Code, VS Code, MCP Inspector y al agente del Lab 10 (patrón Adapter).
- (+) Pruebas de contrato sin LLM ni red (20 pruebas en `agentes/mcp/pruebas`).
- (−) El catálogo cuesta ≈ 935 tokens en cada llamada al modelo; hay que vigilarlo al agregar herramientas.
- (−) Las anotaciones son pistas del servidor: un host solo debe confiar en ellas si confía en el servidor.
