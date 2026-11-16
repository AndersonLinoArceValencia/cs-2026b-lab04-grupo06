# ISSUE-03: Falla no controlada (TypeError) con tramas GPS sin datos o corruptas

**Proyecto:** RutaSIT Arequipa  
**Componente:** `src/monitoreo/adaptadores.py` / `src/monitoreo/servicio.py`  
**Prioridad:** Crítica  
**Tipo:** Bug / Resiliencia y Manejo de Errores  

---

## 1. Comportamiento Observado (Defecto)
Cuando una unidad del SIT transita por zonas con pérdida temporal de línea de visión con satélites GPS (por ejemplo el bypass de la Av. Venezuela, bajo puentes del río Chili o zonas de sombra electromagnética), o cuando el módem celular envía una trama corrupta con valores nulos (`"lat": None`, `"lon": None`, `"velocidad_kmh": None`), el adaptador del concesionario (`GPSOperadorAAdapter.obtener_posicion`) intenta instanciar `DatosTelemetria` o procesar los valores numéricos sin validar nulidad.

Esto dispara una excepción no controlada:
```python
TypeError: unsupported operand type(s) or float conversion on NoneType
```
Esta excepción rompe el ciclo de polling o WebSocket del servicio de monitoreo, provocando la caída del hilo de procesamiento del bus en lugar de degradar elegantemente.

## 2. Comportamiento Esperado
1. El adaptador debe validar exhaustivamente la presencia y validez de las coordenadas geográficas antes de construir el objeto `DatosTelemetria`.
2. Ante una trama con `lat=None`, `lon=None` o campos numéricos nulos/corruptos, el adaptador debe elevar una excepción de dominio específica y controlada (`TramaGPSInvalidaError`), o el servicio debe descartar la lectura corrupta y registrar un evento de advertencia sin arrojar un `TypeError` fatal que colapse la aplicación.

## 3. Prueba que Reproduce el Defecto
La prueba en [`tests/test_issue_03.py`](file:///home/andersp666/cs-2026b-lab04-grupo06/tests/test_issue_03.py) inyecta una respuesta del SDK del Operador A con `{"ok": True, "lat": None, "lon": None, "velocidad_kmh": None}` y verifica que se maneje limpiamente mediante `TramaGPSInvalidaError`. Actualmente falla arrojando errores no controlados o permitiendo `DatosTelemetria` con coordenadas `None` que luego rompen cálculos posteriores con `TypeError`.
