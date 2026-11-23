# Revisión del Pull Request · HU-12 (E4)

## 1. Comparación: Revisión de la IA vs. Revisión Humana

| Aspecto evaluado | Hallazgo de la revisión IA | Hallazgo de la revisión humana (`revision_pr.md`) | ¿Coincidieron? | Acción tomada |
|---|---|---|---|---|
| Reutilización de `FabricaEstrategiasETA` | Confirmó el uso correcto de la fábrica de estrategias. | Verificó además que no se importen adaptadores ni infraestructura (contrato FF-01/FF-02). | Parcial | Se mantiene el aislamiento de capas. |
| Caso borde `km_bus == km_paradero` | Sugirió agregar prueba explícita para distancia cero. | Ya existía `test_bus_en_el_mismo_paradero` verificando `minutos_eta == 0`. | Falso positivo de la IA | Sin cambios; se documentó como falso positivo. |
| Rango de velocidad máxima | No cuestionó el límite de 120 km/h. | Validó que 120 km/h es coherente para buses urbanos SIT en Arequipa y bloquea valores anómalos de GPS. | Solo humano | Aprobado y conservado en `VELOCIDAD_MAX_KMH`. |
| Declaración de asistencia IA | No revisó el formato del mensaje de commit. | Comprobó la línea `Asistencia-IA` en el commit según ADR-012. | Solo humano | Confirmado en el historial de commits. |
| Seguridad y dependencias | Confirmó cero uso de `shell=True`, `eval`, `exec` ni paquetes externos. | Validó manualmente `calidad/dependencias_aprobadas.txt` y salida de Bandit. | Sí | Aprobado. |

## 2. Lista de verificación humana aplicada (`calidad/revision_pr.md`)
- [x] El cambio implementa SOLO la tarea pedida y coincide con `spec.md`.
- [x] Las pruebas se escribieron antes (commit `E3-T1`) y fallaban; ninguna prueba existente fue modificada.
- [x] Reutiliza `FabricaEstrategiasETA` y `Coordenada` sin duplicar reglas de negocio.
- [x] Ninguna dependencia nueva fuera de `calidad/dependencias_aprobadas.txt`.
- [x] Sin `shell=True`, `eval`, `exec`, SQL dinámico ni secretos.
- [x] Respeta `.importlinter` (FF-01, FF-02, FF-03).
- [x] Ambos integrantes explican cada línea de `src/monitoreo/llegada.py`.
- [x] Compuertas de calidad y suite completa de `pytest` en verde.
- [x] Asistencia de IA declarada en el commit y en el PR.
