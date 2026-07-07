# Cambios recomendados en la memoria del proyecto

## Visión general

La memoria del proyecto debe documentar la lógica actual de `traslados.py` y las reglas de negocio que dependen del código y de `data/parameters.json`.

> Importante: la memoria no se actualiza automáticamente con el código. Si el algoritmo cambia, la memoria debe modificarse manualmente.

## Qué debe incluir la memoria

1. Propósito del algoritmo
   - Calcular el saldo o monto pendiente al trasladar un estudiante de un ciclo a otro.
   - Aplicar las reglas de negocio de `CONTADO` y `CUOTAS` de forma separada.

2. Reglas de validación
   - Ciclos encontrados por `cycle_name`, `institution` y `modality`.
   - Misma modalidad de pago requerida entre origen y destino.
   - Fecha de traslado debe estar dentro del rango de ambos ciclos.

3. Reglas de `CONTADO`
   - Las semanas se cuentan en bloques lunes-domingo.
   - Lunes y martes no consumen la semana actual; miércoles a domingo sí.
   - Las semanas de feriado completas se excluyen del consumo.
   - El valor residual se calcula sobre `cash_price` dividido por `duration_weeks + semanas_feriado`.

4. Reglas de `CUOTAS`
   - Solo se prorratea la cuota vigente, no se suman cuotas futuras completas.
   - El periodo de la cuota está anclado a la propia fecha de inicio de la cuota.
   - Las semanas feriado dentro del periodo no se cuentan como consumidas.
   - Si la fecha de traslado es anterior a la primera cuota, se cobra la cuota 1 completa.
   - Si la fecha de traslado está fuera del ciclo, el valor residual es `0.00`.

5. Manejo de feriados
   - Los feriados actuales son 28/07, 29/07 y 25/12.
   - En `CONTADO` se usa el lunes de la semana del feriado para anclar la semana de feriado.
   - En `CUOTAS` se calcula la semana de feriado dentro del periodo de la cuota.

6. Dependencias de `parameters.json`
   - `valid_states`, `blocked_states`, `valid_modalities`, `valid_conditions_of_payment` son datos de validación.
   - Cada ciclo requiere `start_date`, `end_date`, `duration_weeks` y `payment_plans`.
   - Los planes de pago incluyen `cash_price` e `installments`.

## Dónde registrar los cambios

Actualiza los siguientes documentos de memoria del repositorio cuando la lógica cambie:

- `.specify/memory/spec.md`: reglas de negocio actuales y cambios en la especificación.
- `.specify/memory/decisions.md`: decisiones importantes como el manejo de fechas de feriado y el prorrateo de cuotas.
- `.specify/memory/lessons.md`: lecciones aprendidas sobre el cálculo de traslados y casos límite.
- `.specify/memory/memory-index.md`: referencia rápida para encontrar la documentación actualizada.

## Cambios concretos a documentar

- Actualizar la memoria para reflejar que `CUOTAS` ya no suma cuotas futuras completas, sino que prorratea solo la cuota vigente.
- Documentar la regla de `lunes/martes = semana no consumida` en `CONTADO`.
- Documentar que los feriados son semanas completas y se manejan de forma distinta entre `CONTADO` y `CUOTAS`.
- Añadir una nota explicando el formato especial `"En la matrícula"` y su fallback a la fecha de inicio del ciclo.
- Señalar que la memoria debe indicar explícitamente que el código normaliza `CONTADO`/`CUOTAS` y `Presencial`/`Virtual` con mayúsculas.

## Recomendación

Si se realiza cualquier cambio en `traslados.py` o en `data/parameters.json`, revise y actualice simultáneamente la memoria para que quede coherente con el comportamiento real del sistema.
