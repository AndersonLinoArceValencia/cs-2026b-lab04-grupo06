# Especificación · HU-13: Evaluar alerta de desvío de ruta (RutaSIT Arequipa)

*Generada con el comando reutilizable `/nueva-historia` del Grupo 06.*

## Historia de usuario
Como operador del centro de control SIT, quiero recibir una alerta priorizada cuando un bus se desvía más de 250 metros de su corredor asignado, para contactar al conductor y avisar a los pasajeros.

## Criterios de aceptación (Gherkin)

### Escenario 1: Bus dentro de la tolerancia del corredor
- **Dado** un bus en ruta a 120 metros del eje del corredor
- **Cuando** evalúo el desvío de ruta
- **Entonces** el estado es `NORMAL` y no se emite alerta

### Escenario 2: Bus desviado por encima del umbral
- **Dado** un bus en ruta a 340 metros del eje del corredor
- **Cuando** evalúo el desvío de ruta
- **Entonces** el estado es `ALERTA_DESVIO` con prioridad `ALTA`

### Escenario 3: Lectura GPS ausente (caso borde)
- **Dado** un bus sin coordenada GPS reciente (`None`)
- **Cuando** evalúo el desvío de ruta
- **Entonces** el estado es `SIN_GPS` y no se genera una falsa alerta de desvío

### Escenario 4: Distancia negativa o inválida (seguridad)
- **Dado** una distancia de desvío negativa o mayor a 50 000 metros
- **Cuando** evalúo el desvío de ruta
- **Entonces** se lanza `ValueError` con un mensaje descriptivo

## Fuera de alcance
- Despacho real de notificaciones push o SMS.
- Modificación del modelo geoespacial en PostGIS.
