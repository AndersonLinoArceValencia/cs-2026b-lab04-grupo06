# Catálogo de Olores de Código y Patrones Propuestos (E1) — RutaSIT Arequipa

> **Módulo:** `src/monitoreo/antes/servicio.py`  
> **Herramienta de análisis estático:** `radon cc -s -a`, `radon raw -s`, `radon mi -s`  
> **Complejidad del método crítico (`consultar_tiempo_llegada`):** `D (25)`  
> **Líneas de código:** 167 LOC / 124 SLOC

---

## 1. Salida de Métricas con Radon (Versión Antes)

```text
src/monitoreo/antes/servicio.py
    M 56:4 ServicioMonitoreoSIT.consultar_tiempo_llegada - D (25)
    C 47:0 ServicioMonitoreoSIT - C (13)
    M 156:4 ServicioMonitoreoSIT.explicar_retraso - B (8)
    M 50:4 ServicioMonitoreoSIT.__init__ - A (4)
    C 18:0 Coordenada - A (1)
    C 24:0 Paradero - A (1)
    C 32:0 Bus - A (1)
    C 39:0 Viaje - A (1)

8 blocks (classes, functions, methods) analyzed.
Average complexity: B (6.75)

src/monitoreo/antes/servicio.py
    LOC: 167
    LLOC: 131
    SLOC: 124
    Comments: 12
    Single comments: 11
    Multi: 9
    Blank: 23
    - Comment Stats: (C % L): 7% | (C % S): 10%
    Maintainability Index: A (50.22)
```

---

## 2. Tabla de Olores Detectados con IA y Decisiones del Equipo

| Líneas | Olor detectado (Fowler) | Patrón GoF propuesto | Principio SOLID | Costo de aplicarlo | Decisión del equipo |
|---|---|---|---|---|:---:|
| **118–132** | **Switch Statements / Conditional Complexity:** Bloque `if/elif` para seleccionar el algoritmo de ETA (`LINEAL`, `HORA_PUNTA`, `PARADAS_INTERMEDIAS`). Obliga a modificar el servicio cada vez que se agrega un algoritmo nuevo. | **Strategy** + **Factory** | **Open/Closed Principle (OCP)** y **Single Responsibility (SRP)** | Incrementa la cantidad de clases (`IEstrategiaETA`, `ETALineal`, etc.), pero desacopla la formulación matemática del flujo de negocio. | **Aceptado** |
| **81–115** | **Inappropriate Intimacy / Divergent Change:** El servicio conoce los detalles técnicos de bajo nivel y formatos dispares de cada proveedor GPS (dict en grados vs tupla en microgrados/cm por segundo). | **Adapter** | **Dependency Inversion (DIP)** y **Single Responsibility (SRP)** | Requiere definir un puerto formal `IProveedorGPS` y una clase adaptadora por concesionario, aislando el dominio de cambios externos. | **Aceptado** |
| **59–73** | **Primitive Obsession / Type Code:** Verificación manual de estados (`"PROGRAMADO"`, `"DETENIDO"`, etc.) mediante condicionales repetitivos que validan qué transiciones y operaciones están permitidas. | **State** | **Single Responsibility (SRP)** y **Open/Closed (OCP)** | Multiplica el número de clases de estado, pero garantiza transiciones válidas e invariantes de negocio sin `if` anidados. | **Aceptado** |
| **135–144** | **Shotgun Surgery / Feature Envy:** Emisión de eventos concatenando strings a mano en una lista interna (`self.eventos.append`) y acoplamiento directo a `ServicioWebPushExterno`. | **Observer** | **Open/Closed (OCP)** y **Single Responsibility (SRP)** | Agrega indirección mediante interfaces de suscriptor y despacho desacoplado, pero permite registrar nuevos oyentes sin tocar el cálculo de ETA. | **Aceptado** |
| **83–113** | **Scattered Concern / Duplicación de lógica:** Bucles `for` y bloques `try/except TimeoutError` duplicados para reintentar lecturas en cada operador GPS dentro del método principal. | **Decorator** | **Single Responsibility (SRP)** | Introduce una capa envolvente adicional, pero centraliza la resiliencia y reintentos para cualquier proveedor de telemetría. | **Aceptado** |
| **N/A** | **Propuesta de la IA descartada:** Aplicar patrón **Singleton** a `ServicioMonitoreoSIT` o a la fábrica de adaptadores para "evitar instancias múltiples globales". | **Singleton** | N/A (Antipatrón en este contexto) | Introduce acoplamiento global, estado mutable compartido y bloquea la ejecución de pruebas concurrentes parametrizadas en pytest. | **RECHAZADO** |
| **N/A** | **Propuesta de la IA descartada:** Aplicar patrón **Command** para envolver la consulta de tiempo de llegada como objeto comando con soporte de `undo/redo`. | **Command** | N/A | Sobrecarga de clases para una operación de lectura pura e idempotente que no requiere encolamiento diferido ni transacciones reversibles (*patternitis*). | **RECHAZADO** |

---

## 3. Justificación del Rechazo de Patrones (Control de Patternitis)

1. **Rechazo de Singleton:**
   - La IA propuso estructurar `ServicioMonitoreoSIT` como un Singleton para "controlar el acceso global al monitoreo del SIT".
   - **Razón del rechazo:** En Python, los Singletons suelen ser antipatrones que introducen variables globales ocultas, dificultan la inyección de dependencias y rompen la suite de pruebas unitarias (`test_comportamiento.py`), la cual requiere instanciar servicios con diferentes mocks/fallas simuladas de forma aislada.

2. **Rechazo de Command para lecturas:**
   - La IA sugirió transformar `consultar_tiempo_llegada` en un comando ejecutable (`ConsultarETACommand`).
   - **Razón del rechazo:** El flujo es una consulta en tiempo real que no modifica estado persistente, no requiere histórico de deshacer (*undo*) ni ejecución diferida por lotes. Introducir Command aumentaría la complejidad accidental sin aportar valor arquitectónico.
