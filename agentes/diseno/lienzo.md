# Lienzo de Diseño del Sistema Agéntico — RutaSIT Arequipa
**Caso:** Caso 6 — RutaSIT Arequipa (Monitoreo en tiempo real del Sistema Integrado de Transporte de Arequipa)  
**Equipo:** Arce Valencia Anderson Lino & Carlos Ccamaqque Wilson Freddy  
**Laboratorio:** Laboratorio 10 — Sistemas Agénticos en la Construcción de Software (2026-B)  

---

## 1. Lienzo de Decisiones de Diseño (Paso 2 de la Guía)

| Decisión de Diseño | Elección para RutaSIT Arequipa | Justificación Técnica |
| :--- | :--- | :--- |
| **1. ¿Agente o flujo de trabajo?** | **Enfoque híbrido:**<br>• **Agente Autónomo:** Para diagnóstico, reproducción y corrección de incidencias/bugs en el repositorio (`ISSUE-01`, `ISSUE-02`, `ISSUE-03`).<br>• **Flujo de Trabajo Fijo:** Para la ingesta en producción de 30 tramas GPS/s, cálculo cinemático de ETA y despacho WebPush. | Las tareas de depuración en software no son lineales: el espacio de estados y la causa raíz son desconocidos a priori, requiriendo exploración interactiva, formulación de hipótesis y ensayo-error mediante ReAct. Por el contrario, la ingesta en producción requiere latencia sub-segundo ($p95 \le 15$ s), determinismo matemático estricto y cero costo de tokens de LLM. |
| **2. Arquetipo** | **Planificador-Ejecutor + ReAct** (Yao et al., 2023; Albada, 2025 cap. 4) | El arquetipo planificador-ejecutor descompone la meta del issue en un plan acotado (3 a 5 pasos), evitando divagaciones. El ejecutor implementa el ciclo ReAct (*Reasoning + Acting*): cada acción viene precedida por un pensamiento explícito (`pensamiento`) y genera una observación del entorno antes del siguiente paso. |
| **3. Herramientas** | **Caja de herramientas de mínimo privilegio:**<br>`listar_directorio`, `leer_archivo`, `buscar_texto`, `editar_archivo`, `ejecutar_pruebas` (pytest en sandbox), `ver_cambios`. *(En E4 se agregan `mapa_repo`, `anotar`, `leer_notas`)* | El agente de mantenimiento de software solo necesita inspeccionar código, aplicar parches contiguos y verificar con pruebas unitarias. Se prohíben herramientas con acceso a red (`curl`, `pip install`, `git push`) o ejecución arbitraria del sistema operativo para evitar comportamientos destructivos. |
| **4. Memoria** | **Memoria de corto plazo (Historial de la tarea)** complementada en E4 con **Memoria de trabajo externa (`notas.md`)** | La memoria de corto plazo almacena los turnos de la sesión ReAct actual para mantener el hilo de razonamiento. La memoria de notas previene la saturación de contexto al permitir que el agente anote hipótesis y hallazgos clave sin arrastrar todo el contenido de archivos leídos. No se requiere memoria episódica a largo plazo (vectorial) dado que cada issue es independiente. |
| **5. Coordinación** | **Por gestor (Planificador) + Actor-Crítico (Ejecutor y Revisor)** (Albada, 2025 cap. 8) | Separación estricta de intereses (*Separation of Concerns*): el ejecutor (actor) se enfoca en reparar la falla; el revisor (crítico, con permisos exclusivos de solo lectura) evalúa el `git diff` y la salida de pruebas para detectar regresiones o parches sucios. Se limita a un máximo de 2 rondas de retroalimentación para controlar costos y prevenir bucles oscilatorios. |
| **6. Rol humano** | **Revisor / Humano en el circuito (HITL - Human-in-the-loop)** con delegación progresiva | Nivel inicial de confianza baja: ningún agente realiza `git merge` ni `git push` a `main`. El humano supervisa la ejecución, aprueba o rechaza cada edición (`aprobar_edicion` en consola en E6) y decide la integración final del Pull Request. |
| **7. Control** | **Contrato estructurado JSON + Política por rol + Presupuesto estricto** | Todo turno del agente debe cumplir el esquema JSON validado por `validar_decision()`. La política impone un sandbox de directorio raíz (no salir con `../../`), comando seguro solo para `pytest`, un máximo de 12 pasos por ejecutor y 2 rondas actor-crítico, bloqueando inmediatamente excesos de agencia o llamadas a herramientas no registradas. |

---

## 2. Definición del Ámbito de Tareas del Agente

El sistema agéntico se configurará para actuar como **Ingeniero de Mantenimiento y Calidad de RutaSIT**, atacando tres incidencias críticas de lógica de transporte:

1. **`ISSUE-01` (Cálculo de ETA):** Corregir el cálculo cinemático de tiempo estimado de llegada cuando el bus ya superó el paradero de destino, garantizando que el ETA no retorne tiempos negativos.
2. **`ISSUE-02` (Detección de Desvíos):** Resolver falsos positivos y no detección de desvíos en trazados curvos de la ruta mediante evaluación de distancia a segmentos ortogonales en lugar de distancia simple a vértices dispersos.
3. **`ISSUE-03` (Resiliencia de Telemetría GPS):** Fortalecer el adaptador de GPS ante tramas con datos nulos (`None`) o coordenadas incompletas, evitando caídas por `TypeError` y garantizando degradación elegante.

---

## 3. Justificación de Flujo de Trabajo Fijo frente a Agente

| Componente del Sistema RutaSIT | ¿Agente o Flujo Fijo? | Justificación de la Elección |
| :--- | :--- | :--- |
| **Ingesta de telemetría GPS (30 req/s)** | **Flujo fijo (FastAPI / Redis)** | Requiere procesamiento determinista en $< 5$ ms. Un LLM introduciría latencia inaceptable ($> 800$ ms) y costo prohibitivo. |
| **Motor de cálculo de ETA en tiempo real** | **Flujo fijo (Strategy Pattern)** | Algoritmos cinemáticos basados en velocidad y distancia fija (OCP) matemáticamente comprobables. |
| **Alertas a pasajeros (WebPush)** | **Flujo fijo (Observer Pattern)** | Disparado por eventos del dominio sin deliberación semántica. |
| **Resolución de bugs y refactorización** | **Agente (ReAct + Actor-Crítico)** | Requiere lectura de stack traces, inspección de archivos, formulación de hipótesis y edición de código. |
