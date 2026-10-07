# HU-01: Consultar el tiempo de llegada del bus

**Como** pasajero del Sistema Integrado de Transporte (SIT),  
**quiero** consultar el tiempo estimado de llegada (ETA) de un bus a mi paradero actual,  
**para** planificar mi tiempo de espera y evitar contratiempos en mi viaje.

### Criterios de Aceptación

**Criterio 1: Consulta exitosa de bus en ruta**
- **Dado** que el pasajero seleccionó un paradero válido y hay un viaje activo en estado `EnRuta` aproximándose,
- **Cuando** el pasajero solicita consultar el tiempo de llegada en la aplicación,
- **Entonces** el sistema calcula la distancia/tráfico y muestra el tiempo estimado de llegada actualizado en minutos.

**Criterio 2: Notificación de contingencia (Bus desviado o detenido)**
- **Dado** que el pasajero consulta el tiempo de un bus, pero el estado del viaje del bus ha cambiado a `Desviado` o `Detenido`,
- **Cuando** la aplicación procesa la solicitud del tiempo de llegada,
- **Entonces** el sistema informa que el bus presenta un retraso debido a su estado actual y recalcula el ETA considerando la contingencia (o indica "Retrasado").

**Criterio 3: Ausencia de buses disponibles**
- **Dado** que el pasajero consulta un paradero, pero el último bus ya pasó y los siguientes viajes están en estado `Finalizado` o aún no están `Programados`,
- **Cuando** el pasajero solicita el tiempo de llegada,
- **Entonces** el sistema le informa que "No hay buses aproximándose a este paradero en este momento" y le sugiere revisar los horarios oficiales.
