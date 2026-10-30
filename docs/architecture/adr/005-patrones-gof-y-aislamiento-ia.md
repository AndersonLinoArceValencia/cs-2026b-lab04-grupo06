# ADR-005: Refactorización hacia Patrones de Diseño GoF y Aislamiento del Componente de IA

- **Estado:** Aceptado
- **Fecha:** 2026-10-25
- **Decisores:** Anderson Lino Arce Valencia (Arquitecto Líder), Wilson Freddy Carlos Ccamaqque (Desarrollador)

## Contexto
El sistema de monitoreo RutaSIT presentaba olores de código identificados en el Lab 07 (acoplamiento rígido con SDKs de GPS, condicionales complejas para cálculo de tarifas/ETA y falta de aislamiento en el componente experimental de IA). Se requería refactorizar hacia patrones GoF estándar preservando el comportamiento observable y protegiendo el núcleo de dominio ante fallos del modelo de IA.

## Alternativas consideradas
1. Mantener código procedural con funciones auxiliares globales.
2. Refactorizar con microservicios independientes para IA y GPS.
3. Aplicar patrones GoF (Strategy, Adapter, Factory, State, Observer, Decorator) y encapsular la IA mediante el patrón Facade/Proxy dentro del monolito modular.

## Decisión
Adoptamos el diseño con patrones GoF:
- **Strategy:** Algoritmos intercambiables de estimación ETA (`EstrategiaVelocidadPromedio`, `EstrategiaTraficoHistorico`).
- **Adapter:** Unificación de SDKs heterogéneos de proveedores GPS (`AdaptadorGPSWialon`, `AdaptadorGPSTraccar`).
- **Factory:** Creación centralizada de alertas e instancias telemétricas.
- **State:** Gestión del ciclo de vida del viaje de un bus (`EnTerminal`, `EnRuta`, `Desviado`, `Finalizado`).
- **Observer:** Desacoplamiento de eventos de telemetría y notificación a observadores.
- **Decorator:** Enriquecimiento de telemetría con métricas de tiempo y validación.
- **Facade/Proxy:** Aislamiento del componente de IA (`ServicioExplicacionIA`) para garantizar que una caída del modelo no afecte la operación en tiempo real.

## Consecuencias
- **Positivas:** Reducción drástica de complejidad ciclomática, código 100% testeable (40 pruebas unitarias en verde) y cumplimiento de contratos verificados por `import-linter`.
- **Negativas / riesgos:** Ligero incremento en el número de clases y llamadas polimórficas (mitigado por tipado estático en Python).
