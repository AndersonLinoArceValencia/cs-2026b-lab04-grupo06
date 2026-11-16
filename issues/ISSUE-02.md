# ISSUE-02: Desvío de ruta no detectado o falsos positivos en curvas cerradas

**Proyecto:** RutaSIT Arequipa  
**Componente:** `src/monitoreo/desvios.py` / `src/monitoreo/servicio.py`  
**Prioridad:** Alta  
**Tipo:** Bug / Algoritmo Geoespacial  

---

## 1. Comportamiento Observado (Defecto)
El algoritmo de detección de desvío de unidades (`evaluar_desvio_ruta`) verifica la posición de un bus calculando únicamente la distancia euclidiana mínima contra los vértices/waypoints discretos definidos en la ruta:
$$\text{distancia\_min} = \min_{p \in \text{waypoints}} \text{distancia}(bus, p)$$

En curvas pronunciadas o giros cerrados (como en la Variante de Uchumayo, Puente Chilina o subidas de Cayma), los waypoints de la ruta están separados por 100 a 150 metros. Cuando un bus transita legalmente sobre la calzada intermedia que conecta ambos vértices en curva, su distancia a cualquiera de los dos vértices extremos supera los 50 metros (umbral de tolerancia). En consecuencia, el sistema emite una falsa alarma de desvío (`True`), notificando incorrectamente al Centro de Control y a los pasajeros.

## 2. Comportamiento Esperado
1. El algoritmo debe calcular la distancia ortogonal (perpendicular) más corta de la posición del bus hacia los **segmentos de recta continuos** que unen los waypoints consecutivos de la ruta, o interpolar la trayectoria en curvas.
2. Si un bus viaja sobre el segmento válido entre dos waypoints en curva (dentro del umbral de tolerancia de 50 metros), el método debe retornar `False` (dentro de ruta).
3. Solo debe retornar `True` si el bus se encuentra verdaderamente apartado de cualquier segmento de la ruta por más de 50 metros.

## 3. Prueba que Reproduce el Defecto
La prueba en [`tests/test_issue_02.py`](file:///home/andersp666/cs-2026b-lab04-grupo06/tests/test_issue_02.py) simula una curva con dos waypoints distanciados 120 metros y una posición del bus ubicada exactamente a mitad del segmento de curva a 15 metros del eje. Actualmente falla porque el algoritmo ingenuo compara solo contra los extremos (distancia $\approx 60$ m $> 50$ m) y emite un falso positivo `True`.
