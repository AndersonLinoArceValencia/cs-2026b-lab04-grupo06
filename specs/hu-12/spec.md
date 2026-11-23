# Especificación · HU-12: Estimar la hora de llegada al paradero (RutaSIT Arequipa)

## Historia de usuario
Como pasajero del SIT Arequipa, quiero conocer la hora estimada de llegada de un bus a mi paradero, para decidir si esperar la unidad actual o tomar otra ruta.

## Criterios de aceptación (Gherkin)

### Escenario 1: Bus en ruta aproximándose al paradero
- **Dado** un bus en estado `EN_RUTA` con GPS válido en el kilómetro 2.0 y velocidad 30.0 km/h
- **Cuando** estimo la hora de llegada al paradero ubicado en el kilómetro 5.0 a las 08:00 con estrategia `LINEAL`
- **Entonces** el estado devuelto es `EN_CAMINO`, el tiempo estimado es `6` minutos y la hora estimada es `08:06`

### Escenario 2: Bus que ya pasó el paradero (caso borde obligatorio)
- **Dado** un bus en estado `EN_RUTA` cuya posición en el tramo es el kilómetro 6.2
- **Cuando** estimo la hora de llegada al paradero ubicado en el kilómetro 5.0
- **Entonces** el estado devuelto es `YA_PASO`, `minutos_eta` es `None` y `hora_estimada` es `None`

### Escenario 3: GPS sin datos (caso borde obligatorio)
- **Dado** un bus cuya lectura GPS es `None` o no tiene coordenadas válidas
- **Cuando** estimo la hora de llegada al paradero
- **Entonces** el estado devuelto es `SIN_GPS`, `minutos_eta` es `None` y `hora_estimada` es `None`

### Escenario 4: Seguridad y validación de entradas fuera de rango físico
- **Dado** una velocidad negativa o superior a 120 km/h, o una coordenada fuera del rango geográfico de Arequipa (latitud -16.65 a -16.15, longitud -71.80 a -71.30)
- **Cuando** estimo la hora de llegada
- **Entonces** se lanza `ValueError` con un mensaje descriptivo sin exponer datos internos

### Escenario 5: Estimación en hora punta reutilizando estrategias existentes
- **Dado** un bus en el kilómetro 1.0 hacia el paradero en el kilómetro 4.0 con velocidad 30.0 km/h a las 18:00
- **Cuando** estimo la hora de llegada usando la estrategia `HORA_PUNTA`
- **Entonces** reutiliza `FabricaEstrategiasETA`, devolviendo `14` minutos y hora estimada `18:14`

## Fuera de alcance
- Envío de notificaciones Web Push o correos electrónicos.
- Consultas HTTP a servicios de mapas externos o escritura de archivos en disco.
- Modificación de las estrategias ya probadas en `src/monitoreo/estrategias.py`.
