# ADR-004: Definir el puerto INotificador en eta_geocercas y su adaptador en notificaciones

- Estado: Aceptado
- Fecha: 2026-10-10
- Decisores: Arce Valencia Anderson Lino y Carlos Ccamaqque Wilson Freddy (Grupo 06)

## Contexto
Al dibujar el diagrama de paquetes del Lab 05 (`docs/design/paquetes.puml`) apareció un posible ciclo entre los módulos del ADR-001. El módulo `eta_geocercas` necesita avisar un retraso o desvío (`notificarRetraso(viaje)`), y el módulo `notificaciones` necesita conocer `Viaje` para armar el mensaje. Si `eta_geocercas` importa a `notificaciones` y `notificaciones` importa a `eta_geocercas` (por el tipo `Viaje`), los dos forman en la práctica un solo módulo y se rompe la regla C4 y la vigilancia con `import-linter` del ADR-001.

## Alternativas consideradas
1. **Dependencia directa en ambos sentidos.** Es lo más rápido de escribir, pero crea el ciclo y obliga a desplegar y cambiar los dos módulos juntos.
2. **Mover `Viaje` y `EstadoViaje` a `compartido`.** Rompe el ciclo, pero convierte `compartido` en un cajón de entidades de negocio que todos tocan y vacía de contenido al módulo dueño del viaje.
3. **Inversión de dependencia con un puerto.** `INotificador` se define en `eta_geocercas` (quien lo necesita) y `notificaciones` aporta el adaptador `WebPushAdapter` que lo realiza.

## Decisión
Adoptamos la alternativa 3. `eta_geocercas` solo conoce la interfaz `INotificador`; `notificaciones` depende de `eta_geocercas` para implementarla. La flecha de dependencia queda `notificaciones ..> eta_geocercas` y no hay ciclos. Se mantiene la regla de ADR-001: cada módulo expone solo su fachada `service.py`, y el puerto se exporta desde ella.

## Consecuencias
- **Positivas:**
  - No hay ciclos entre paquetes; `import-linter` puede verificarlo en CI.
  - El módulo de notificaciones se puede reemplazar (Web Push, WhatsApp o correo) sin tocar `eta_geocercas`.
  - La prueba de `ServicioMonitoreoSIT` usa un notificador falso sin infraestructura.
- **Negativas / riesgos:**
  - Una interfaz más que mantener y un adaptador por canal.
  - `notificaciones` queda acoplado al tipo `Viaje` de `eta_geocercas`; si el contrato cambia, hay que actualizar el adaptador.
