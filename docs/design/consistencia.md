# E7: Revisión de consistencia de los diagramas (reglas C1–C5)

Se aplicó el **Prompt IA 3 (auditor de consistencia)**, ejecutado con Claude el 10/10/2026, sobre los cinco diagramas de `docs/design/`: `clases.puml`, `secuencia-consultar-tiempo.puml`, `estados-viaje.mmd`, `actividades-deteccion-desvio.puml` y `paquetes.puml`. La IA solo reportó hallazgos; el equipo verificó cada uno contra los archivos.

## Hallazgos de la IA y verificación del equipo

| N.º | Regla | Elemento | Hallazgo de la IA | Verificación del equipo | Resultado |
|:---:|:---:|---|---|---|:---:|
| 1 | C2 | `estados-viaje.mmd`, transición inicial | `iniciarPlanificacion()` no es una operación de `Viaje`. | Correcto: la operación no existía en el diagrama de clases. Se reemplazó por `programar()` y se agregó a `Viaje` en `clases.puml` y en `dominio.py`. | ✅ Corregido |
| 2 | C1 | Secuencia, mensaje `Viaje -> IServicioMapas : calcularETA` | No existe una relación `Viaje`–`IServicioMapas` en el diagrama de clases; solo `ServicioMonitoreoSIT ..> IServicioMapas`. | Correcto: la operación existe en el puerto, pero la dependencia estaba mal ubicada. Se agregó `Viaje ..> IServicioMapas` y se quitó la del servicio. | ✅ Corregido |
| 3 | C1 | Secuencia, mensaje `Viaje ->> ServicioMonitoreoSIT : procesarAlertaDesvio` | El mensaje lo envía `Viaje`, pero en el código lo invoca el propio servicio. | Correcto: se rediseñó. Ahora el servicio llama a `procesarAlertaDesvio` sobre sí mismo y emite `->> INotificador : notificarRetraso(viaje)` (asíncrono). | ✅ Corregido |
| 4 | C1 | Secuencia, mensaje `Pasajero -> UI : consultarETA` | `consultarETA` figuraba en `Pasajero`, pero la secuencia lo envía a la app. | Correcto: se creó la clase `AppPasajero` con `consultarETA` y `mostrarResultado`, y `Pasajero` quedó solo con datos. | ✅ Corregido |
| 5 | C1 | Secuencia, `obtenerCoordenadaActual` | `IProveedorGPS` está en el diagrama de clases pero ninguna secuencia lo usa. | Correcto: se agregó la llamada del servicio al puerto y `Bus.actualizarUbicacion`. | ✅ Corregido |
| 6 | C3 | `Ruta *-- Paradero` | La composición es incorrecta si un paradero lo comparten varias rutas. | Correcto: un paradero (p. ej. "Plaza de Armas") pertenece a varias rutas del SIT. Se cambió a agregación `Ruta "1" o-- "2..*" Paradero`. | ✅ Corregido |
| 7 | C3 | `Viaje "1" --> "1" EstadoViaje` | La multiplicidad `1` del lado de la enumeración limita a un viaje por estado. | **Falso positivo.** El `1` junto a la enumeración significa que cada viaje tiene exactamente un estado; no limita a un viaje por estado. Se explicitó `"0..*" --> "1"` solo para evitar la confusión, sin cambiar el modelo. | ❎ Falso positivo |
| 8 | C4 | `notificaciones ..> eta_geocercas` y `eta_geocercas ..> notificaciones` | Hay un ciclo entre los dos paquetes. | Correcto respecto al primer borrador de `paquetes.puml`, que dibujaba `eta_geocercas ..> notificaciones`. Se resolvió con el puerto `INotificador` definido en `eta_geocercas` y adaptador en `notificaciones`, y se registró en [ADR-004](../architecture/adr/004-puerto-notificador-sin-ciclos.md). | ✅ Corregido |
| 9 | C4 | `supervision ..> eta_geocercas` | `supervision` depende de `eta_geocercas` y esta de `supervision`. | **Falso positivo.** Se leyó al revés la flecha `SUP ..> ETA`: `supervision` depende de `eta_geocercas` (solo lectura) y `eta_geocercas` no depende de `supervision` en ningún diagrama. Se rechaza el hallazgo. | ❎ Falso positivo |
| 10 | C5 | `Pasajero.consultarETA` vs `consultar_eta` | Los nombres difieren entre diagrama y código. | Aceptable: conversión camelCase a snake_case por PEP 8; la equivalencia está documentada en `round-trip.md` (C5). | ℹ️ Documentado |
| 11 | C5 | Paquetes vs ADR-001 | Los nombres de paquete no coinciden con los módulos del ADR-001. | Correcto en parte: se usan los 5 módulos del ADR-001 en snake_case (`ingesta_gps`, `eta_geocercas`, `notificaciones`, `catalogo`, `supervision`) más `compartido`. | ✅ Corregido |

## Resumen
- **Hallazgos totales:** 11. **Aceptados y corregidos:** 8. **Falsos positivos:** 2 (hallazgos 7 y 9). **Documentados:** 1.
- **Falso positivo 9 y su riesgo:** si se hubiera aceptado sin verificar, se habría "corregido" una dependencia que ya iba en el sentido correcto, invirtiéndola y creando un ciclo real con `eta_geocercas`.
- **Regla de oro aplicada:** la IA propone, el equipo decide y verifica.
