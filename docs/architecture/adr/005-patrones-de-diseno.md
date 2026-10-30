# ADR-005: Patrones del módulo de monitoreo RutaSIT

- **Estado:** Propuesto para revisión del equipo (25/10/2026).
- **Decisores:** Arce Valencia Anderson Lino y Carlos Ccamaqque Wilson Freddy.
- **Contexto:** HU-01 consulta el tiempo de llegada a partir de GPS de dos operadores. El método inicial `consultar_tiempo_llegada` tenía complejidad D (25), mezclaba selección de algoritmo, formatos de SDK, estados, reintentos y notificaciones. La explicación de retrasos incorpora una salida simulada de IA que debe validarse antes de mostrarse.

## Decisión

Usar Strategy para las variantes de ETA; Adapter y fábricas registrables para GPS; State para las transiciones de `Viaje`; Observer para distribuir ETA y alertas; Decorator para reintentos GPS y caché; y Chain of Responsibility para dos validaciones de la explicación generada. El servicio depende de puertos y delega cada responsabilidad. Las pruebas de caracterización se ejecutan sobre `antes.servicio` y `servicio`.

## Alternativas descartadas

Singleton en el servicio o las fábricas introduciría estado global y dificultaría inyectar proveedores simulados por prueba. Command para la consulta ETA agregaría objetos sin que exista deshacer, cola o ejecución diferida. Ambas propuestas figuran en `docs/design/patrones/olores.md` como rechazadas.

## Consecuencias y verificación

La complejidad del método crítico pasó de D (25) a A (3); 28 ejecuciones de comportamiento compartido y 12 pruebas de patrones aprobaron en `48af9a7`. El archivo de servicio creció de 124 a 152 SLOC, y los siete módulos posteriores suman 526 SLOC. El equipo acepta ese costo para poder añadir algoritmos y operadores mediante registros sin reescribir el flujo principal. Estas pruebas no demuestran rendimiento ni comportamiento ante servicios reales; los proveedores externos y el LLM son simulados.
