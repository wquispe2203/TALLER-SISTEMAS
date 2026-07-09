# Resumen Ejecutivo

Este documento define la suite de 15 casos de prueba (Test Cases) para la Calculadora de Montos de Traslado Académico. **Todos los valores esperados de este documento fueron generados ejecutando directamente `zproyect/traslados.py` contra `zproyect/data/parameters.json` (2026-07-09)** — no son cálculos manuales ni provienen del Excel original. Todos los ciclos referenciados existen verificados en `parameters.json`; ningún caso usa nombres de ciclo inventados.

> **Actualización 2026-07-09 (Corrección de feriados):** se corrigió el algoritmo para que las semanas de feriado NO se cobren al alumno (ni diluidas ni de ninguna otra forma). Anteriormente se sumaban al denominador (`duration_weeks + feriados`), lo que diluía el costo del feriado entre todas las semanas en vez de eliminarlo. Ahora `duration_weeks` se usa directamente como denominador, y las semanas feriado simplemente no cuentan ni en semanas consumidas ni en semanas totales. Ver `decisions.md` → entrada 2026-07-09. Los valores de TC-1, TC-2, TC-6/7/8, TC-12, TC-13 y TC-15 cambiaron; TC-3/9, TC-10, TC-14 permanecen iguales (sus periodos no incluyen feriados).

## Cómo reproducir estos valores

```python
from datetime import date
from traslados import CicloInput, cargar_parametros, calcular_traslado
P = cargar_parametros("data/parameters.json")
calcular_traslado(date(2026, 5, 15),
    CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO"),
    CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO"), P)
```

---

# Casos de Prueba (Test Cases)

## TC-1: Traslado CONTADO con saldo a favor

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO (cash_price: S/ 3240, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)

**Esperado (verificado en `zproyect/test/test_traslados.py`):**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 1046.25"
- Saldo origen: S/ 3557.25
- Costo destino: S/ 2511.00
- Diferencia: S/ 1046.25

**Nota de cálculo:** `valor_semana = cash_price / duration_weeks = 4590/40 = 114.75`. `semanas_consumidas = 9` al 15/05/2026. `semanas_restantes = 40 - 9 = 31`. `saldo = 114.75 * 31 = 3557.25`. Los feriados (2 en el ciclo completo) no se incluyen en el denominador ni en el numerador.

---

## TC-2: Traslado CONTADO con monto pendiente (reverso exacto de TC-1)

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, VIRTUAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, PRESENCIAL, CONTADO

**Esperado:**
- Estado: MONTO_PENDIENTE
- Mensaje: "Monto pendiente: S/ 1046.25"
- Saldo origen: S/ 2511.00
- Costo destino: S/ 3557.25
- Diferencia: -S/ 1046.25

---

## TC-3: Traslado CUOTAS cubierto exactamente (mismo ciclo, misma modalidad)

**Entradas:**
- Fecha de traslado: 20/04/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS
- Ciclo Destino: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (idéntico al origen)

**Esperado:**
- Estado: TRASLADO_CUBIERTO
- Mensaje: "Traslado cubierto exactamente"
- Saldo origen: S/ 382.50
- Costo destino: S/ 382.50
- Diferencia: S/ 0.00

**Nota:** origen y destino son el mismo ciclo/modalidad, por lo que el resultado es trivialmente igual sin importar la fórmula de prorrateo. Cubre CB-2 (ciclo origen = ciclo destino).

---

## TC-4: Modalidad de pago diferente (bloqueo)

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CUOTAS

**Esperado:**
- Error: "No se permiten traslados entre modalidades de pago diferentes. Si requiere este tipo de traslado, debe procesarlo manualmente."

---

## TC-5: Fecha fuera del rango del ciclo origen

**Entradas:**
- Fecha de traslado: 15/01/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL MARZO, SM, VIRTUAL, CONTADO (fecha_inicio: 16/03/2026)

**Esperado:**
- Error: "La fecha de traslado está fuera del rango del ciclo origen (ANUAL MARZO)"

---

## TC-6: Lunes - semana no consumida (CONTADO)

**Entradas:**
- Fecha de traslado: 13/04/2026 (lunes)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO

**Esperado (verificado en `zproyect/test/test_traslados.py`):**
- Saldo origen: S/ 4131.00 (la semana del 13/04 NO se cuenta como consumida)

---

## TC-7: Martes - semana no consumida (CONTADO)

**Entradas:**
- Fecha de traslado: 14/04/2026 (martes)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO

**Esperado (verificado en `zproyect/test/test_traslados.py`):**
- Saldo origen: S/ 4131.00 (igual que TC-6)

---

## TC-8: Miércoles - semana SÍ consumida (CONTADO)

**Entradas:**
- Fecha de traslado: 15/04/2026 (miércoles)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO

**Esperado (verificado en `zproyect/test/test_traslados.py`):**
- Saldo origen: S/ 4016.25 (menor que TC-6/TC-7: el miércoles sí consume la semana)

---

## TC-9: CUOTAS con saldo a favor — prorrateo de la cuota vigente (mismo ciclo, distinta modalidad)

> Antes de 2026-07-04 este era el "TC-3" y esperaba S/ 4080.00 (suma de las 10 cuotas futuras completas). Esa regla quedó obsoleta: el algoritmo v4 prorratea **solo la cuota vigente** a la fecha de traslado. Ver `traslados.py::calcular_valor_cuotas`.

**Entradas:**
- Fecha de traslado: 20/04/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (cuota vigente: cuota 2, S/ 510, periodo 11/04/2026–09/05/2026)
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CUOTAS (cuota vigente: cuota 2, S/ 360, mismo periodo)

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 112.50"
- Saldo origen: S/ 382.50 (= 510 × 3/4 semanas restantes del periodo de la cuota 2)
- Costo destino: S/ 270.00 (= 360 × 3/4)
- Diferencia: S/ 112.50

---

## TC-10: CUOTAS con saldo a favor — ciclos distintos (cuotas y montos diferentes)

**Entradas:**
- Fecha de traslado: 25/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)
- Ciclo Destino: SEMIANUAL MARZO, SM, VIRTUAL, CUOTAS (7 cuotas de S/ 360)

**Nota sobre el cálculo:**
- El algoritmo prorratea **solo la cuota vigente** en la fecha del traslado, no suma el monto completo de las cuotas futuras.
- El valor residual depende de cuántas semanas de la cuota vigente ya se han consumido.

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 75.00"
- Saldo origen: S/ 255.00
- Costo destino: S/ 180.00
- Diferencia: S/ 75.00

---

## TC-11: Ciclo no encontrado

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: CICLO INEXISTENTE, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO

**Esperado (modo `calcular_traslado_seguro`):**
```json
{"success": false, "error": "Ciclo origen no encontrado en la base de datos"}
```

---

## TC-12: Semana de feriado (Fiestas Patrias) — CONTADO

**Entradas:**
- Fecha de traslado: 29/07/2026 (miércoles, dentro de la semana de Fiestas Patrias)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO

**Nota sobre feriados (corregido 2026-07-09):**
- Los feriados NO se cobran al alumno. No se suman al denominador. `duration_weeks=40` se usa directamente.
- La semana feriado se salta en el conteo de semanas consumidas: aunque el 29/07 cae en la semana 20 del ciclo, esa semana no se cuenta como consumida.
- Semanas consumidas reales = 19 (de las 20 semanas calendario transcurridas, 1 es feriado y no cuenta).

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 708.75"
- Saldo origen: S/ 2409.75 (= 4590/40 × 21)
- Costo destino: S/ 1701.00 (= 3240/40 × 21)
- Semanas consumidas (origen y destino): 19 de 40 semanas de clase
- Semanas restantes: 40 − 19 = 21

---

## TC-13: Cuota vigente cuyo periodo incluye una semana de feriado (CUOTAS)

**Entradas:**
- Fecha de traslado: 05/08/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (cuota vigente: cuota 5, S/ 510, periodo 04/07/2026–08/08/2026 → 5 semanas calendario, incluye la semana de Fiestas Patrias)
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CUOTAS (cuota vigente: cuota 5, S/ 360, mismo periodo)

**Nota (corregido 2026-07-09):**
- Anteriormente la semana feriado se excluía solo del consumo pero se mantenía en el total (5 total, 3 consumidas, 2 restantes → 510×2/5=204.00).
- Ahora la semana feriado se excluye del total también: 5 calendario − 1 feriado = 4 semanas reales. De las 4 semanas completas transcurridas, 3 son reales (una es feriado). Restante: 1 semana.
- `510 × 1/4 = 127.50`, `360 × 1/4 = 90.00`.

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 37.50"
- Saldo origen: S/ 127.50 (= 510 × 1/4)
- Costo destino: S/ 90.00 (= 360 × 1/4)
- `detalle.origen`: `semanas_totales: 4, semanas_consumidas: 3, semanas_restantes: 1`

---

## TC-14: Desglose humano CUOTAS (AC-3.4) — sin cambios (periodo sin feriados)

**Entradas:**
- Fecha de traslado: 25/03/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CUOTAS

**Esperado (verificado en `zproyect/test/test_traslados.py`, AC-3.4/TC-14):**
- Estado: SALDO_A_FAVOR — Mensaje: "Saldo a favor: S/ 112.50"
- Saldo origen: S/ 382.50 — Costo destino: S/ 270.00 — Diferencia: S/ 112.50
- `detalle.origen`: `semanas_totales: 4, semanas_consumidas: 1, semanas_restantes: 3`

**`detalle.origen.pasos` (desglose humano real, `generar_pasos_cuotas`):**
1. "Ciclo origen: fecha de traslado 25/03/2026."
2. "La cuota vigente es la cuota 1, de S/ 510.00, con periodo del 16/03/2026 al 11/04/2026 (26 días)."
3. "Ese periodo equivale a 4 semana(s) (26 días ÷ 7 = 3.71, redondeado)."
4. "Desde el inicio del periodo (16/03/2026) hasta la fecha de traslado han pasado 9 día(s)."
5. "Ninguna semana feriado cae dentro de este periodo."
6. "Semanas consumidas del periodo: 1. Semanas restantes: 4 − 1 = 3."
7. "Valor residual = monto de la cuota (S/ 510.00) × semanas restantes (3) ÷ semanas totales del periodo (4) = S/ 382.50 (redondeo half-up a 2 decimales)."

---

## TC-15: Desglose humano CONTADO (AC-3.5) — corregido por exclusión de feriados

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: SEMIANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 3213, duration_weeks: 28, fecha_inicio: 16/03/2026, fecha_fin: 02/10/2026)
- Ciclo Destino: SEMIANUAL MARZO, SM, VIRTUAL, CONTADO (cash_price: S/ 2268, duration_weeks: 28, mismas fechas)

**Esperado (verificado en `zproyect/test/test_traslados.py`, AC-3.5/TC-15):**
- Estado: SALDO_A_FAVOR — Mensaje: "Saldo a favor: S/ 641.25"
- Saldo origen: S/ 2180.25 — Costo destino: S/ 1539.00 — Diferencia: S/ 641.25
- `detalle.origen`: `semanas_totales: 28, semanas_consumidas: 9, semanas_restantes: 19`

**`detalle.origen.pasos` (desglose humano real, `generar_pasos_contado`):**
1. "Ciclo origen: fecha de traslado 15/05/2026 (viernes)."
2. "El ciclo inicia el 16/03/2026 y termina el 02/10/2026."
3. "La fecha de traslado cae en la semana 9 del ciclo (11/05/2026 al 17/05/2026)."
4. "Como es viernes (miércoles a domingo consumen la semana), esa semana SÍ se cuenta como consumida."
5. "Semanas consumidas: 9."
6. "Dentro del ciclo completo hay 1 semana(s) de feriado. No se cobran al alumno: no se incluyen ni en las semanas de clase ni en las semanas restantes."
7. "Semanas de clase del ciclo (duration_weeks, feriados ya excluidos): 28."
8. "Semanas restantes = semanas de clase (28) − semanas consumidas (9) = 19."
9. "Valor por semana = cash_price (S/ 3213.00) ÷ semanas de clase (28) = S/ 114.7500."
10. "Saldo = valor por semana × semanas restantes (19) = S/ 2180.25 (redondeo half-up a 2 decimales)."
