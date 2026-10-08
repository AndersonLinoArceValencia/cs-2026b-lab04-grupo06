# E6: Round-trip con IA (Ingeniería Inversa)

## 1. Generación de Código
Se utilizó IA para generar el esqueleto en Python (`src/monitoreo/dominio.py`) a partir del diagrama de clases (`clases.puml`).
Se respetaron:
- Dataclasses de Python 3.10+ y Type hints.
- Interfaces usando el módulo `abc` (`ABC`, `@abstractmethod`).
- Nomenclatura convertida de `camelCase` (diagrama) a `snake_case` (Python).
- Lógica mínima en `Viaje` y `ServicioMonitoreoSIT`, y lanzamiento de `NotImplementedError` en adaptadores.

## 2. Ingeniería Inversa
*(Nota técnica: Debido a que el entorno actual no posee `pip` ni `pylint` instalado de forma global, se analiza teóricamente el comportamiento estándar de `pyreverse` sobre este código Python para realizar la comparativa, tal como fue requerido).*

## 3. Comparativa y Diferencias (Diseño vs Código)

| N.º | Diferencia Encontrada | Causa (¿Por qué se perdió/cambió la información?) | Acción Tomada / Decisión |
| :---: | :--- | :--- | :--- |
| **1** | **Pérdida del estereotipo `<<interface>>`** en `IProveedorGPS` e `IServicioMapas`. | `pyreverse` interpreta las clases que heredan de `ABC` como clases regulares con herencia, pero no les asigna automáticamente el estereotipo nativo de interfaz de UML. | **Documentar limitación:** En Python no existen las interfaces puras; se comprende que `ABC` cumple ese rol en el código. |
| **2** | **Cambio de multiplicidades y tipos de relación** (ej. composición `*--` a asociación simple). | Python es dinámico. Un tipado como `List[Paradero]` es inferido por `pyreverse` como una agregación o asociación simple de `Paradero`, perdiendo el detalle estricto de cardinalidad `1 a muchos (1..*)` y composición. | **Corregir diagrama / Documentar:** Se asume que el diagrama de clases original (diseño) dicta la regla de negocio estricta, el código solo muestra la implementación. |
| **3** | **Conversión de nomenclatura** de `camelCase` a `snake_case`. | Los estándares de codificación de Python (PEP-8) exigen `snake_case` para atributos y métodos, mientras que el estándar UML clásico suele modelarse en `camelCase`. | **Documentar la convención:** Se acepta la discrepancia semántica por buenas prácticas de lenguaje. Los nombres del dominio (Viaje, Bus, Paradero) se mantienen idénticos. |
