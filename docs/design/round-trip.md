# E6: Round-trip con IA (Ingeniería Inversa)

## 1. Generación de Código
Se utilizó IA para generar el esqueleto en Python (`src/monitoreo/dominio.py`) a partir del diagrama de clases (`clases.puml`).
Se respetaron:
- Dataclasses de Python 3.10+ y Type hints.
- Interfaces usando el módulo `abc` (`ABC`, `@abstractmethod`).
- Nomenclatura convertida de `camelCase` (diagrama) a `snake_case` (Python).
- Lógica mínima en `Viaje` y `ServicioMonitoreoSIT`.

## 2. Ingeniería Inversa
Se ejecutó satisfactoriamente `pyreverse` en un entorno virtual aislado:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pylint
pyreverse -o puml -p monitoreo src/monitoreo/
```
Esto generó los diagramas `classes_monitoreo.puml` y `packages_monitoreo.puml`.

## 3. Comparativa y Diferencias (Diseño vs Código)

| N.º | Diferencia Encontrada en `classes_monitoreo.puml` respecto a `clases.puml` | Causa (¿Por qué se perdió/cambió la información?) | Acción Tomada / Decisión |
| :---: | :--- | :--- | :--- |
| **1** | **Pérdida del estereotipo `<<interface>>`** en `IProveedorGPS` e `IServicioMapas`. | `pyreverse` dibuja las clases `ABC` como clases regulares con métodos `{abstract}`, pero no inyecta el estereotipo nativo de interfaz de PlantUML. | **Documentar limitación:** Python no tiene interfaces puras; se comprende que `ABC` cumple ese rol semántico. |
| **2** | **Pérdida de la composición y asociaciones en listas** (Ej. no se dibuja la relación de `Ruta` hacia `Paradero`). | `pyreverse` no infiere correctamente las relaciones a partir de genéricos como `List[Paradero]`. Solo dibuja asociaciones (como `-->`) de atributos de tipo simple (como `bus` o `estado`). | **Corregir diagrama original:** Se asume que el diagrama de diseño dicta las multiplicidades estrictas. El código de Python y su auto-diagrama son solo vistas de implementación estática. |
| **3** | **Omisión de los valores del Enum `EstadoViaje`**. | El diagrama generado solo muestra un atributo estandarizado `name` para la clase Enum en lugar de listar los valores reales (`PROGRAMADO`, `EN_RUTA`, etc.). | **Documentar limitación:** Las herramientas estáticas de Python agrupan las constantes dinámicas, perdiendo el detalle UML. |
| **4** | **Conversión de nomenclatura** de `camelCase` a `snake_case`. | Los estándares de codificación de Python (PEP-8) exigen `snake_case`, mientras que el modelo UML clásico suele usar `camelCase`. | **Se aceptó la discrepancia:** Es una buena práctica adaptarnos al lenguaje destino. |
