---
description: Genera spec.md, plan.md y tasks.md a partir de una historia de usuario y AGENTS.md
---
Lee `AGENTS.md` y `.importlinter`. A partir de la historia `${input:historia}` con identificador `${input:hu}`:
1. Crea `specs/${input:hu}/spec.md` con al menos 4 escenarios Gherkin (incluyendo un escenario de seguridad o caso borde) y una sección "Fuera de alcance".
2. Crea `specs/${input:hu}/plan.md` indicando módulos a reutilizar, contratos arquitectónicos y dependencias permitidas.
3. Crea `specs/${input:hu}/tasks.md` dividido en al menos 4 tareas pequeñas listas para TDD.
