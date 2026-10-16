# Análisis Comparativo de Modelado y Vistas (Laboratorio 06 — Modelo C4)

Este documento contiene los análisis comparativos solicitados en la guía del Laboratorio 06 para la evaluación crítica de representaciones arquitectónicas.

---

## 1. Comparación: Vista Dinámica C4 vs Diagrama de Secuencia UML (E4)

El diagrama de secuencia UML (`secuencia-consultar-tiempo.puml`) muestra detalles de diseño fino que la vista dinámica C4 (`structurizr-ConsultarTiempoLlegada`) omite deliberadamente: fragmentos condicionales (`alt` para éxito o error de buses vacíos/desviados), bucles de iteración (`loop por cada viaje`), firmas exactas de métodos con parámetros tipados (`calcularTiempoLlegada(paradero)`), y la barra de activación temporal en la línea de vida de objetos en memoria. 

Mientras que la secuencia UML está dirigida a desarrolladores e ingenieros de QA que requieren implementar el código, controlar hilos y escribir pruebas unitarias sobre ramas condicionales, la vista dinámica C4 sirve a arquitectos de software, líderes técnicos y evaluadores para comunicar el flujo general de datos e interacciones entre módulos de alto nivel sin saturar la vista con detalles algorítmicos.

---

## 2. Comparación de Enfoques: Escritura Manual (C4-PlantUML) vs Modelo Exportado (Structurizr DSL) (E6)

A partir de la experiencia práctica de modelar el Nivel 1 tanto a mano (`contexto-manual.puml`) como mediante el modelo unificado (`workspace.dsl` exportado a `export/`), se evalúan los siguientes criterios:

### A. Tiempo invertido
* **Escritura manual (C4-PlantUML):** Escribir un archivo aislado es rápido para una prueba de concepto inicial (5 a 10 minutos). No obstante, conforme el sistema escala a 5 vistas, el tiempo total se multiplica linealmente ($O(N)$), pues obliga a reescribir y duplicar actores, sistemas externos y etiquetas de estilo en cada diagrama `.puml` individual.
* **Modelo exportado (Structurizr DSL):** Demanda una mayor inversión de tiempo inicial (20 a 30 minutos) para estructurar el metamodelo jerárquico, sus entidades y relaciones. Sin embargo, a partir de ese único esfuerzo, la derivación de las 5 vistas, su exportación simultánea a PlantUML y Mermaid, y la generación de imágenes toma menos de 10 segundos con un script. El retorno de inversión es exponencialmente favorable.

### B. Errores encontrados
* **Escritura manual:** Es altamente propensa a inconsistencias invisibles. En `contexto-manual.puml`, si se comete un error tipográfico en el identificador de un actor o se describe una flecha con una intención distinta a la del diagrama de contenedores, la herramienta no emite advertencias. La coherencia depende 100% de la memoria y disciplina humana.
* **Modelo exportado:** El compilador de Structurizr CLI (`structurizr.sh validate`) actúa como un linter estricto de arquitectura. Si se referencia un elemento inexistente, se omite un protocolo requerido o se anida incorrectamente un componente, el proceso falla de inmediato antes de exportar. Los únicos errores detectados fueron advertencias de sintaxis corregidas tempranamente durante la validación del DSL.

### C. Mantenibilidad: ¿Qué pasaría si mañana cambia el nombre o tecnología de un contenedor?
*(Ejemplo: renombrar `"Worker Espacial y Batch"` a `"Motor de Procesamiento Espacial Celery")*
* **Enfoque manual:** Se tendría que editar manualmente el cambio en múltiples archivos independientes (`contenedores.puml`, `componentes.puml`, `dinamico.puml` y `despliegue.puml`). Esto genera casi con certeza "deriva arquitectónica" (diagramas obsoletos o contradictorios en el mismo repositorio).
* **Enfoque Structurizr DSL:** Solo se modifica **una sola línea** en el bloque `model` de `workspace.dsl`. Al ejecutar nuevamente `./structurizr.sh export` y regenerar los PNGs, **todas las vistas se actualizan instantáneamente de forma atómica y consistente**, garantizando el principio de verdad única (*Single Source of Truth*).

