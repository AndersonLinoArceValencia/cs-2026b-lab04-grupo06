# Cuestionario — Laboratorio 05 (Grupo 06, RutaSIT Arequipa)

## 1. ¿Qué diferencia hay entre el diseño arquitectónico del Laboratorio 04 y el diseño detallado de este laboratorio?
El Lab 04 decidió **cómo se organiza el sistema**: un monolito modular asíncrono con Redis y PostgreSQL/PostGIS dividido en cinco módulos (ADR-001). El Lab 05 diseña **el interior de esos módulos**: qué clases existen, cómo colaboran y qué estados atraviesan. Ejemplo: en el Lab 04 definimos el módulo "ETA y Geocercas"; en el Lab 05 definimos que `ServicioMonitoreoSIT` consulta a `Viaje`, que este usa el puerto `IServicioMapas` y que el viaje pasa por los estados `PROGRAMADO`, `EN_RUTA`, `DESVIADO`, `DETENIDO` y `FINALIZADO`.

## 2. ¿Cuándo usaría composición y cuándo agregación? Justifique con dos relaciones de su diagrama.
Composición cuando la parte no existe sin el todo; agregación cuando sí. En nuestro diagrama usamos **agregación** en `Ruta "1" o-- "2..*" Paradero`, porque un paradero (por ejemplo, Plaza de Armas) sigue existiendo y lo comparten varias rutas aunque se elimine una de ellas. Una **composición** correspondería, por ejemplo, a un tramo de recorrido que solo tiene sentido dentro de una ruta concreta, algo que en este MVP no modelamos.

## 3. ¿Por qué en el diagrama de clases se modela la pasarela (el servicio externo) como interfaz y no como superclase? Relaciónelo con el ADR-001.
`IProveedorGPS`, `IServicioMapas` e `INotificador` son **puertos**: contratos que el dominio necesita y que cada proveedor cumple con un adaptador (`ProveedorGPSAdapter`, `ServicioMapasAdapter`, `WebPushAdapter`). Con una superclase el dominio heredaría de un proveedor concreto, contradiciendo el ADR-001, que pide fronteras y contratos explícitos entre módulos y la posibilidad de extraer o reemplazar piezas. Con interfaces, cambiar de OpenStreetMap a otro servicio solo exige un nuevo adaptador.

## 4. Explique la regla C1 y muestre un mensaje de su diagrama de secuencia que la incumplía antes de corregirlo.
C1: todo mensaje dirigido a un objeto debe ser una operación de la clase de ese objeto. En la primera versión, `Viaje ->> ServicioMonitoreoSIT : procesarAlertaDesvio(this)` incumplía la regla porque en el diseño y en el código era el servicio quien invocaba `procesarAlertaDesvio` sobre sí mismo, y `Viaje` no tenía relación con `IServicioMapas`. Se rehízo la secuencia: el servicio llama a su propia operación y luego envía `->> INotificador : notificarRetraso(viaje)`.

## 5. ¿Cómo se derivan casos de prueba a partir de un diagrama de máquina de estados? Indique cuántas pruebas mínimas requiere su diagrama.
Se escribe **una prueba por transición**, verificando el estado resultante cuando se cumple la guarda (y que no cambia cuando no se cumple). Nuestro diagrama tiene **9 transiciones** (`programar`, `PROGRAMADO→EN_RUTA`, `EN_RUTA→DETENIDO`, `EN_RUTA→DESVIADO`, `DETENIDO→EN_RUTA`, `DESVIADO→EN_RUTA`, `DETENIDO→FINALIZADO`, `DESVIADO→FINALIZADO`, `EN_RUTA→FINALIZADO`), por lo que requiere como mínimo 9 pruebas.

## 6. ¿Qué información del diagrama de diseño se perdió en la ingeniería inversa (E6) y por qué?
Se perdieron las multiplicidades, la agregación `Ruta`–`Paradero`, los estereotipos de puerto y los valores de la enumeración `EstadoViaje`. La causa es que Python no expresa multiplicidades y que pyreverse no infiere asociaciones desde colecciones tipadas ni lista las constantes de un `Enum`. Detalle en [round-trip.md](round-trip.md).

## 7. ¿Qué falso positivo detectó en la revisión de consistencia con IA? ¿Qué habría pasado si lo aceptaba sin verificar?
El hallazgo C4 que decía que `eta_geocercas` y `supervision` formaban un ciclo: se había leído al revés la flecha `SUP ..> ETA`. Aceptarlo habría llevado a "corregir" una dependencia que ya iba bien, invirtiéndola y creando un ciclo real. Ver [consistencia.md](consistencia.md).

## 8. Según Fowler, UML puede usarse como boceto, plano o lenguaje de programación. ¿Cuál de esos usos aplicó en este laboratorio y por qué es adecuado para un MVP de 1 mes?
Usamos UML como **boceto** para pensar y comunicar (estados, actividades) y como **plano** de la parte crítica (clases y secuencia de HU-01, de las que generamos el esqueleto de código). Es adecuado para un MVP de 1 mes con 2 desarrolladores porque modela solo lo necesario para tomar buenas decisiones y evita documentar todo el sistema.
