# Comparativa de Compuertas de Calidad · HU-12 (E5)

Se comparó un borrador generado con un prompt vago sin `AGENTS.md` ni `spec.md` (`borrador_v0`), una corrección mínima eliminando únicamente la dependencia inventada (`borrador_v1`) y la versión final construida con SDD + TDD (`src.monitoreo.llegada`). Además, se incorporó la 8.ª compuerta `Arquitectura (import-linter)` para verificar automáticamente los contratos FF-01, FF-02 y FF-03 del Laboratorio 08.

| Compuerta | Borrador v0 | Borrador v1 | Versión final (Spec + TDD) |
|---|---|---|---|
| 1. Dependencias aprobadas | FALLA (`geopy_fast_eta`, `subprocess`) | FALLA (`subprocess`) | PASA (4 aprobadas) |
| 2. Pruebas HU-12 | FALLA (0/8) | FALLA (2/8) | PASA (8/8) |
| 3. Cobertura (>= 85 %) | FALLA (14 %) | PASA (86 %) | PASA (100 %) |
| 4. Ruff (estilo y seguridad) | FALLA (3 hallazgos) | FALLA (2 hallazgos) | PASA (0 hallazgos) |
| 5. Bandit (seguridad) | FALLA (B404, B602) | FALLA (B404, B602) | PASA (sin hallazgos) |
| 6. Radon (complejidad <= B) | PASA (B, CC=6) | PASA (B, CC=6) | PASA (A, CC=3) |
| 7. Secretos en el código | PASA (0) | PASA (0) | PASA (0) |
| 8. Arquitectura (`import-linter`) | PASA (3 contratos) | PASA (3 contratos) | PASA (3 contratos) |
| **Total aprobadas** | **3/8** | **4/8** | **8/8** |
