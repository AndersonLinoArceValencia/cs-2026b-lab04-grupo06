# Análisis Comparativo de Modelado y Vistas (Laboratorio 06 — Modelo C4)

Este documento contiene los análisis comparativos solicitados en la guía del Laboratorio 06 para la evaluación crítica de representaciones arquitectónicas.

---

## 1. Comparación: Vista Dinámica C4 vs Diagrama de Secuencia UML (E4)

El diagrama de secuencia UML (`secuencia-consultar-tiempo.puml`) muestra detalles de diseño fino que la vista dinámica C4 (`structurizr-ConsultarTiempoLlegada`) omite deliberadamente: fragmentos condicionales (`alt` para éxito o error de buses vacíos/desviados), bucles de iteración (`loop por cada viaje`), firmas exactas de métodos con parámetros tipados (`calcularTiempoLlegada(paradero)`), y la barra de activación temporal en la línea de vida de objetos en memoria. 

Mientras que la secuencia UML está dirigida a desarrolladores e ingenieros de QA que requieren implementar el código, controlar hilos y escribir pruebas unitarias sobre ramas condicionales, la vista dinámica C4 sirve a arquitectos de software, líderes técnicos y evaluadores para comunicar el flujo general de datos e interacciones entre módulos de alto nivel sin saturar la vista con detalles algorítmicos.

---
