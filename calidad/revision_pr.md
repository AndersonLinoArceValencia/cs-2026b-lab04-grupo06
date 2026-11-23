# Lista de verificación para revisar código asistido por IA

- [ ] El cambio implementa SOLO la tarea pedida y coincide con `spec.md` (criterios de aceptación).
- [ ] Las pruebas se escribieron antes y fallaban; ninguna prueba existente fue modificada para pasar.
- [ ] Reutiliza funciones y clases del proyecto en lugar de duplicar reglas de negocio.
- [ ] Ninguna dependencia nueva fuera de `calidad/dependencias_aprobadas.txt`.
- [ ] Sin `shell=True`, `eval`, `exec`, rutas o SQL armados con datos externos, ni secretos.
- [ ] Respeta los contratos arquitectónicos de `.importlinter` (FF-01, FF-02, FF-03).
- [ ] El equipo entiende y puede explicar cada línea antes de fusionar.
- [ ] Compuertas de calidad en verde en local y en CI.
- [ ] El commit o PR declara la asistencia de IA según ADR-012.
