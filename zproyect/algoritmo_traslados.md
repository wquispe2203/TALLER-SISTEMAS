# Algoritmo de traslados

## Propósito

Este documento describe el algoritmo de **traslados** para calcular el saldo o el monto pendiente cuando un alumno solicita un traslado entre ciclos de estudio.

## Flujo general

1. Recibe una fecha de traslado y dos ciclos: origen y destino.
2. Valida que ambos ciclos existan en `data/parameters.json`.
3. Verifica que ambos ciclos tengan la misma modalidad de pago (`CONTADO` o `CUOTAS`).
4. Comprueba que la fecha de traslado esté dentro del rango de ambos ciclos.
5. Calcula el valor residual del ciclo origen y el costo residual del ciclo destino.
6. Devuelve la diferencia como `saldo_a_favor`, `monto_pendiente` o `traslado_cubierto`.

## Entradas

- `fecha_traslado`: fecha en formato `D/M/YYYY`, `DD/MM/YYYY` o `YYYY-MM-DD`.
- `origen`: objeto con `nombre`, `universidad`, `modalidad_academica` y `pago_en`.
- `destino`: objeto con la misma estructura que `origen`.

## Validaciones

- El ciclo de `origen` debe encontrarse en `parameters.json` usando coincidencia case-insensitive de `cycle_name`, `institution` y `modality`.
- El ciclo de `destino` debe encontrarse de la misma forma.
- `origen.pago_en` y `destino.pago_en` deben ser iguales y válidos (`CONTADO` o `CUOTAS`).
- `fecha_traslado` debe estar dentro de los rangos de fechas de ambos ciclos.

## Pago CONTADO

El cálculo de valores residuales para `CONTADO` sigue estos pasos:

1. Se calcula cuántas semanas se han consumido desde el inicio del ciclo origen hasta la fecha de traslado, **excluyendo** las semanas de feriado.
2. Se calcula cuántas semanas se han consumido desde el inicio del ciclo destino hasta la fecha de traslado (mismo criterio).
3. **Las semanas de feriado NO se cobran al alumno.** No se suman al denominador: `duration_weeks` representa las semanas reales de clase.
4. El valor por semana se obtiene dividiendo `cash_price` entre `duration_weeks` (sin añadir feriados).
5. El saldo restante es `valor_semana * (duration_weeks - semanas_consumidas)`.

### Reglas de semanas consumidas en CONTADO

- Las semanas se anclan al calendario global: cada semana empieza en lunes y termina en domingo.
- Si la fecha de traslado cae en lunes o martes, la semana actual no se considera consumida.
- Si la fecha de traslado cae entre miércoles y domingo, la semana actual sí se considera consumida.
- Las semanas de feriado completas no se cuentan como consumidas ni se incluyen en ningún lado del cálculo.

### Feriados para CONTADO

- Los feriados se definen como fechas puntuales en `FERIADOS_DIAS`:
  - 28/07
  - 29/07
  - 25/12
- Cada feriado cancela la semana completa en la que cae, usando el lunes de esa semana.
- El algoritmo busca estas semanas en el año anterior, el año del traslado y el año siguiente para cubrir rangos que crucen años.
- Las semanas feriado son solo informativas en la narrativa: se listan pero no afectan el cálculo del monto.

## Pago CUOTAS

Para `CUOTAS`, el algoritmo ya no suma el monto completo de las cuotas futuras. Ahora calcula solo el valor residual de la cuota vigente en la fecha del traslado.

### Cómo funciona el cálculo de CUOTAS

1. Convierte las fechas de vencimiento de las cuotas usando `parse_fecha`.
2. Identifica la cuota cuyo periodo contiene la `fecha_traslado`.
   - El periodo de una cuota va desde su fecha de inicio hasta la fecha de la siguiente cuota.
   - Para la última cuota, el periodo va hasta el fin del ciclo.
3. Prorratea el monto de la cuota vigente según cuántas semanas completas de ese periodo ya se han consumido.
4. La prorrata descuenta las semanas de feriado que ocurran dentro del mismo periodo de la cuota.

### Reglas de prorrateo de cuota

- Las semanas se anclan a la fecha de inicio del periodo de la cuota, no al lunes del calendario.
- Las semanas feriado dentro de ese periodo no se consideran consumidas.
- Si la fecha de traslado es anterior a la primera cuota, se debe el valor completo de la primera cuota.
- Si la fecha de traslado es igual o posterior al fin del ciclo, el valor residual es `0.00`.

## Utilidades de fecha

- `parse_fecha(valor, fallback)`: convierte valores tipo `D/M/YYYY`, `DD/MM/YYYY`, `YYYY-MM-DD` o `En la matrícula`.
- `En la matrícula` se interpreta como la fecha de inicio del ciclo (`fallback`).

## Salida del cálculo

El resultado final contiene:

- `saldo_origen`: valor residual del ciclo de origen.
- `costo_destino`: valor residual del ciclo de destino.
- `diferencia`: `saldo_origen - costo_destino`.
- `estado`: uno de `SALDO_A_FAVOR`, `MONTO_PENDIENTE`, `TRASLADO_CUBIERTO`.
- `mensaje`: texto amigable con el resultado.
- `detalle`: objeto con `semanas_totales`, `semanas_consumidas` y `semanas_restantes` para origen y destino.

## Dependencias de parámetros

- Los datos de ciclos y planes de pago se cargan desde `data/parameters.json`.
- El algoritmo usa `cycle_name`, `institution`, `modality`, `start_date`, `end_date`, `duration_weeks` y `payment_plans`.
- `payment_plans` contiene `Contado` y `Cuotas`, y cada plan tiene `cash_price` e `installments`.

## Notas importantes

- El cálculo de `CUOTAS` es distinto al de `CONTADO`.
- El algoritmo no permite traslados entre modos de pago diferentes.
- Las semanas feriado se manejan de forma diferente según la modalidad de pago.
