# ISSUE-01: Tiempo de llegada (ETA) negativo si el bus pasó el paradero

**Proyecto:** RutaSIT Arequipa  
**Componente:** `src/monitoreo/estrategias.py` y `src/monitoreo/servicio.py`  
**Prioridad:** Alta  
**Tipo:** Bug / Lógica de Negocio  

---

## 1. Comportamiento Observado (Defecto)
Cuando una unidad de transporte ya superó la ubicación física de un paradero en su recorrido, o cuando se proyecta una distancia relativa negativa (por ejemplo `distancia_km = -0.5` debido a que el bus rebasó la estación por 500 metros), las estrategias de estimación de tiempo de llegada (`ETALinealStrategy`, `ETAHoraPuntaStrategy`, `ETAParadasIntermediasStrategy`) aplican directamente la fórmula cinemática:
$$\text{ETA} = \left\lfloor \frac{\text{distancia\_km}}{v} \times 60 \right\rceil$$

Al recibir un valor de distancia negativo, el método `calcular_eta` retorna números enteros negativos (por ejemplo `-2` o `-5` minutos). Esto genera información errónea y confusa en las pantallas de los paraderos y en la aplicación del pasajero, mostrando textos como *"El bus llega en -2 minutos"*.

## 2. Comportamiento Esperado
1. Si la distancia restante hacia el paradero de consulta es menor o igual a cero (`distancia_km <= 0.0`), el cálculo de ETA debe normalizarse y retornar exactamente `0` minutos (indicando que la unidad se encuentra en el paradero o ya lo rebasó).
2. Bajo ninguna circunstancia `calcular_eta` debe retornar un valor menor a 0.

## 3. Prueba que Reproduce el Defecto
La prueba en [`tests/test_issue_01.py`](file:///home/andersp666/cs-2026b-lab04-grupo06/tests/test_issue_01.py) evalúa las estrategias con distancias negativas (`-0.5` km, `-1.2` km) y verifica que el valor retornado sea `0`. Actualmente, la prueba falla porque las estrategias retornan valores negativos (`-2`, `-5`).
