# No determinismo (E7)

Se ejecutó la v3.1 tres veces sobre H1, H2 y H3 (`criterios/grabaciones/no_determinismo/corridaN/v3.1/`).

| Caso | Corrida 1 | Corrida 2 | Corrida 3 |
|---|---|---|---|
| H1 | exito, borde, exito, error | exito, borde, error, borde | exito, borde, borde, error |
| H2 | exito, exito, borde, error | exito, exito, borde, error | exito, exito, borde, error |
| H3 | exito, borde, borde, error | exito, borde, borde, borde | exito, borde, error |

1. En las 9 respuestas `invest_ok` fue `true` y el JSON cumplió el esquema: la decisión se mantuvo estable.
2. El número y el tipo de escenarios cambió entre corridas (H1 y H3), y también los títulos y las preguntas.
3. Una aserción como "al menos un éxito y un error o borde" resiste esa variación; una que compare texto exacto no.
4. Las grabaciones fijan una sola muestra: sirven para repetir la evaluación, no para probar que el modelo responderá igual mañana.
5. Con un modelo real conviene temperatura 0, aserciones sobre propiedades y repetir la evaluación periódicamente.
