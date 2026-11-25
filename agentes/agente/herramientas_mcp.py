"""Adaptador (patrón Adapter, Lab 07): presenta las herramientas de un servidor MCP con la misma
interfaz que agente/herramientas.py. El núcleo del agente del Lab 10 no cambia ni una línea."""

import asyncio
import json
import threading
from mcp import Client, StdioServerParameters
from mcp.types import Implementation


class HerramientasMCP:
    def __init__(self, servidor: StdioServerParameters, exponer_recursos=True):
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, daemon=True).start()
        self._listo, self._cerrar = threading.Event(), None
        self._exponer_recursos = exponer_recursos
        asyncio.run_coroutine_threadsafe(self._conectar(servidor), self._loop)
        self._listo.wait(timeout=30)

    async def _conectar(self, servidor):
        self._cerrar = asyncio.Event()
        async with Client(
            servidor, client_info=Implementation(name="agente-lab10", version="1.1")
        ) as c:
            self._cliente = c
            self._tools = {
                t.name: t for t in (await c.list_tools()).tools
            }  # descubrimiento dinámico
            self._listo.set()
            await self._cerrar.wait()

    def _llamar(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=60)

    def catalogo(self) -> dict:
        cat = {}
        for n, t in self._tools.items():
            params = json.dumps(t.input_schema.get("properties", {}), ensure_ascii=False)
            cat[n] = f"{t.description.strip()} Parámetros: {params}"
        if self._exponer_recursos:  # decisión del HOST: los recursos los controla la aplicación
            cat["leer_recurso"] = (
                "Lee un recurso MCP por URI (por ejemplo rutasit://adr/001). Parámetros: uri"
            )
        return cat

    def herramientas_de_escritura(self) -> set:
        """Las anotaciones son PISTAS del servidor, no garantías.
        Úselas solo con servidores de confianza."""
        return {
            n
            for n, t in self._tools.items()
            if not (t.annotations and t.annotations.read_only_hint)
        }

    def leer_recurso(self, uri: str) -> str:
        r = self._llamar(self._cliente.read_resource(uri))
        return "\n".join(getattr(c, "text", "") for c in r.contents)

    def __getattr__(self, nombre):
        if nombre.startswith("_") or nombre not in self.__dict__.get("_tools", {}):
            raise AttributeError(nombre)

        def invocar(**args):
            r = self._llamar(self._cliente.call_tool(nombre, args))
            if r.structured_content is not None:
                cuerpo = json.dumps(r.structured_content, ensure_ascii=False)
            else:
                cuerpo = " ".join(getattr(c, "text", "") for c in r.content)
            return ("ERROR: " if r.is_error else "") + cuerpo

        return invocar

    def cerrar(self):
        self._loop.call_soon_threadsafe(self._cerrar.set)
