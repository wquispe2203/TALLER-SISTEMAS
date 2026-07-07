# Resumen Ejecutivo

Este documento define la suite de 12 casos de prueba (Test Cases) diseñados para validar la Calculadora de Montos de Traslado Académico según el algoritmo v4. Los casos están basados en datos reales del Excel oficial y cubren escenarios de éxito, validaciones y casos borde.

# Casos de Prueba (Test Cases)

## TC-1: Traslado CONTADO con saldo a favor

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: S/ 1350, duration_weeks: 20, fecha_inicio: 05/01/2026, fecha_fin: 19/06/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 3489.75"
- Saldo origen: S/ 3557.25
- Costo destino: S/ 67.50
- Diferencia: S/ 3489.75

---

## TC-2: Traslado CONTADO con monto pendiente

**Entradas:**
- Fecha de traslado: 20/03/2026
- Ciclo Origen: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: S/ 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)
- Ciclo Destino: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: MONTO_PENDIENTE
- Mensaje: "Monto pendiente: S/ 3867.75"
- Saldo origen: S/ 607.50
- Costo destino: S/ 4475.25
- Diferencia: -S/ 3867.75

---

## TC-3: Traslado CUOTAS cubierto exactamente (mismas cuotas)

**Entradas:**
- Fecha de traslado: 20/04/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CUOTAS (10 cuotas de S/ 510)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: TRASLADO_CUBIERTO
- Mensaje: "Traslado cubierto exactamente"
- Saldo origen: S/ 4080.00
- Costo destino: S/ 4080.00
- Diferencia: S/ 0.00

---

## TC-4: Modalidad de pago diferente (bloqueo)

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CUOTAS

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Error: "No se permiten traslados entre modalidades de pago diferentes. Si requiere este tipo de traslado, debe procesarlo manualmente."

---

## TC-5: Fecha fuera del rango del ciclo origen

**Entradas:**
- Fecha de traslado: 15/01/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Error: "La fecha de traslado está fuera del rango del ciclo origen (ANUAL MARZO)"

---

## TC-6: Lunes - semana no consumida

**Entradas:**
- Fecha de traslado: 13/04/2026 (lunes)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Saldo origen: S/ 4131.00 (la semana del 13/04 no se cuenta como consumida)

---

## TC-7: Martes - semana no consumida

**Entradas:**
- Fecha de traslado: 14/04/2026 (martes)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Saldo origen: S/ 4131.00 (igual que TC-6)

---

## TC-8: Miércoles - semana SÍ consumida

**Entradas:**
- Fecha de traslado: 15/04/2026 (miércoles)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Saldo origen: S/ 4016.25 (miércoles cuenta como semana consumida)

---

## TC-9: Traslado CUOTAS con saldo a favor (prorrateo de cuota vigente)

**Entradas:**
- Fecha de traslado: 25/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CUOTAS (8 cuotas de S/ 400)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Nota sobre el cálculo:**
- El algoritmo prorratea **solo la cuota vigente** en la fecha del traslado, no suma el monto completo de las cuotas futuras.
- El valor residual depende de cuántas semanas de la cuota vigente ya se han consumido.

**Esperado:**
- Estado: según el prorrateo de la cuota vigente en 25/05/2026
- El cálculo usa: monto de la cuota × (semanas restantes del periodo / semanas totales del periodo)

---

## TC-10: Ciclo no encontrado

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: CICLO INEXISTENTE, SM, PRESENCIAL, CONTADO
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Error: "Ciclo origen no encontrado en la base de datos"

---

## TC-11: Semana de feriado - traslado durante feriado de julio

**Entradas:**
- Fecha de traslado: 29/07/2026 (miércoles, durante Fiestas Patrias)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Nota sobre feriados:**
- Los feriados definidos son: 28/07, 29/07 (Fiestas Patrias) y 25/12 (Navidad).
- Cada feriado "cancela" la semana completa (lunes-domingo) en la que cae.
- El algoritmo extiende la duración efectiva del ciclo sumando las semanas de feriado.

**Esperado:**
- Estado: TRASLADO_CUBIERTO
- Diferencia: S/ 0.00 (mismo ciclo, mismo precio)
- Las semanas de feriado se descuentan del cálculo de semanas consumidas

---

## TC-12: Cuota con vencimiento en semana de feriado

**Entradas:**
- Fecha de traslado: 01/08/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS
- Cuota vigente: identificada por la fecha de traslado dentro de su periodo

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Nota sobre el cálculo en CUOTAS:**
- El algoritmo prorratea **solo la cuota vigente** según las semanas consumidas de su periodo.
- Las semanas se anclan a la fecha de inicio del periodo de la cuota, no al lunes del calendario.
- Las semanas de feriado dentro del periodo de la cuota no se consideran consumidas.

**Esperado:**
- El cálculo identifica la cuota vigente a la fecha 01/08/2026.
- Valor residual = monto de la cuota × (semanas restantes del periodo / semanas totales del periodo)
- Las semanas de feriado (28/07, 29/07) se descuentan del conteo de semanas consumidas si caen dentro del periodo de la cuota