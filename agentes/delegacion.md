# Hoja de Ruta de Autonomía y Delegación Progresiva — RutaSIT Arequipa

**Caso:** Caso 6 — RutaSIT Arequipa  
**Equipo:** Arce Valencia Anderson Lino & Carlos Ccamaqque Wilson Freddy  
**Referencia:** Albada (2025, cap. 13); Koenigstein (2026, cap. 2); OWASP Top 10 for LLM (2025)  

---

## 1. Filosofía de Delegación Progresiva

La autonomía de un agente de inteligencia artificial en la ingeniería de software no debe ser estática ni absoluta: **debe ganarse gradualmente a medida que el sistema demuestra confiabilidad empírica mediante sus trazas y métricas**. 

En RutaSIT Arequipa, un fallo en producción (como desvíos falsos o estimaciones de tiempo corruptas) afecta directamente a miles de usuarios del transporte público y a los despachadores del consorcio. Por tanto, se adopta la **Regla de Oro**:

> *El agente propone; el contrato y la política filtran; el humano aprueba.*

---

## 2. Los Cuatro Roles Humanos en la Evolución del Agente

A continuación se define la matriz de transición por etapas para el sistema agéntico de RutaSIT:

| Etapa / Rol Humano | Nivel de Autonomía del Agente | Permisos y Herramientas Permitidas | Acciones Bloqueadas / Guardrails | Evidencia Requerida en Trazas para Pasar a la Siguiente Etapa |
| :--- | :--- | :--- | :--- | :--- |
| **1. Humano como Ejecutor** *(Asistente Pasivo / Diagnóstico)* | **Nivel 0: Solo Lectura.** El agente únicamente analiza y diagnostica; el humano redacta todo el código. | `mapa_repo`, `leer_archivo`, `buscar`, `leer_notas`. | Bloqueo absoluto de `editar_archivo`, comandos de consola y mutación de archivos. | $\ge 95\%$ de precisión en la identificación de causa raíz en al menos 10 issues consecutivos, con $0$ violaciones de contrato JSON. |
| **2. Humano como Revisor** *(Estado Actual Lab 10 - HITL Supervisado)* | **Nivel 1: Actor-Crítico Supervisado.** El agente propone código en un sandbox aislado; cada edición requiere confirmación explícita `'s'`/`'n'` en consola (`aprobar_edicion`), y el Pull Request final es evaluado por un humano. | Todas las de Nivel 0 + `editar_archivo` (con HITL obligatorio), `ejecutar_pruebas` (sandbox), `ver_cambios`, `anotar`. | Bloqueo de rutas protegidas (`tests/`), comandos fuera de lista blanca, acceso a red (`curl`, `pip`) y git push directo a `main`. | $\ge 15$ ejecuciones en sandbox sin caídas por `TypeError`, $0$ violaciones de rutas protegidas, $0\%$ de regresiones en pruebas de arquitectura (fitness functions) y tasa de rechazo humano $< 10\%$. |
| **3. Humano como Colaborador** *(Autonomía Parcial en Ramas Feature)* | **Nivel 2: Co-desarrollo en Ramas.** El agente puede editar y autoverificarse en ramas de trabajo `fix/issue-XX` sin solicitar confirmación línea por línea. El humano colabora resolviendo conflictos complejos y aprueba el merge final. | Todas las de Nivel 1 con `editar_archivo` autónomo dentro del sandbox de la rama feature + `ejecutar_comando` (linter, radon, pytest). | Bloqueo estricto de merge automático a `main` o `develop`, bloqueo de variables de entorno de producción y credenciales. | Ratio de acciones bloqueadas por política $= 0\%$, estabilidad en métricas de complejidad ciclomática Radon (rango A/B) y ausencia de inyecciones indirectas tras pruebas de estrés. |
| **4. Humano como Gobernador** *(Supervisión por Políticas y Auditoría)* | **Nivel 3: Auto-reparación en Preproducción.** El agente diagnostica, aplica parches, corre pruebas de regresión y abre PRs automáticamente con evidencia adjunta. El humano solo audita trazas consolidadas y define políticas de seguridad. | Todas las de Nivel 2 + auto-creación de Pull Requests en GitHub con plantilla formal y traza Mermaid incrustada. | Bloqueo de auto-aprobación del propio PR, límites estrictos de presupuesto de tokens por issue ($< 25{,}000$ tokens) y máximo de pasos ($12$). | Historial de auditoría limpio durante 30 días, cero incidentes de exceso de agencia (OWASP LLM06) y aprobación del 100% de tests en CI/CD. |

---

## 3. Patrones de Humano en el Circuito Implementados

Siguiendo a Koenigstein (2026, cap. 2), se han integrado en el framework:

1. **Aprobar o Rechazar Interactivo:** Mediante la función `pedir_aprobacion_humana(args)` conectada al hook `aprobar_edicion` de `Politica`, el desarrollador visualiza el fragmento original (`antes`), el código sugerido (`despues`) y el archivo destino antes de cualquier escritura a disco.
2. **Validación Estricta de la Entrada Humana:** Se asegura que el operador humano solo pueda responder `'s'` (aprobar) o `'n'` (rechazar), repitiendo la solicitud ante entradas ambiguas para evitar fallos por tipeo accidental.
3. **Revisión del Diff Final:** El humano inspecciona la salida consolidada de `ver_cambios()` y el veredicto del revisor antes de autorizar el merge en el repositorio oficial.

---

## 4. Mitigación de Riesgos Críticos de Seguridad

* **Exceso de Agencia (OWASP LLM06, 2025):** Cada rol agéntico cuenta con la mínima cantidad de herramientas necesarias. El planificador carece de herramientas de ejecución; el revisor tiene permisos exclusivos de solo lectura; y el ejecutor no puede modificar la carpeta `tests/`.
* **Inyección Indirecta (Greshake et al., 2023):** Las instrucciones no confiables provenientes de descripciones de issues o datos externos se tratan como cadenas de texto pasivas; el agente solo ejecuta acciones válidas predefinidas en el catálogo del contrato, impidiendo que órdenes maliciosas camufladas en comentarios ejecuten comandos del sistema operativo.
