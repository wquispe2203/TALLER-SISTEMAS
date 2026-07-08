# Resumen Ejecutivo

Este documento define la suite de 15 casos de prueba (Test Cases) para la Calculadora de Montos de Traslado Académico. **Todos los valores esperados de este documento fueron generados ejecutando directamente `zproyect/traslados.py` contra `zproyect/data/parameters.json` (2026-07-07)** — no son cálculos manuales ni provienen del Excel original. Todos los ciclos referenciados existen verificados en `parameters.json`; ningún caso usa nombres de ciclo inventados.

> Actualización 2026-07-07 (FR-010): se agregaron TC-14 y TC-15, que documentan el desglose "estilo cálculo manual" (`detalle.origen/destino.pasos`) — la respuesta de la API ahora narra el cálculo paso a paso (qué semana, desde cuándo, cuántas consumidas) en vez de mostrar solo el resultado final de una resta. Ver spec.md AC-3.4/AC-3.5 y `zproyect/traslados.py::generar_pasos_contado`/`generar_pasos_cuotas`. Los 13 casos anteriores (TC-1 a TC-13) siguen siendo válidos; todos, ejecutados hoy, quedan verificados 1:1 contra `zproyect/test/test_traslados.py`.

> Nota de sincronización (2026-07-07): la versión anterior de este documento usaba dos ciclos que **no existen** en `parameters.json` ("SEMIANUAL ENERO, SM" y "ANUAL MARZO, UNI") y varios valores esperados correspondían a una versión previa del algoritmo (antes de que CUOTAS pasara a prorratear solo la cuota vigente). Ver `decisions.md` → entrada 2026-07-07 y `lessons.md` → entrada 2026-07-07.

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
- Mensaje: "Saldo a favor: S/ 1060.72"
- Saldo origen: S/ 3606.43
- Costo destino: S/ 2545.71
- Diferencia: S/ 1060.72

**Nota de cálculo:** `semanas_efectivas = duration_weeks + semanas_feriado_del_ciclo_completo = 40 + 2 = 42` (el ciclo 16/3–31/12/2026 cruza las semanas de feriado de julio y diciembre). `semanas_consumidas = 9` al 15/05/2026.

---

## TC-2: Traslado CONTADO con monto pendiente (reverso exacto de TC-1)

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, VIRTUAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, PRESENCIAL, CONTADO

**Esperado:**
- Estado: MONTO_PENDIENTE
- Mensaje: "Monto pendiente: S/ 1060.72"
- Saldo origen: S/ 2545.71
- Costo destino: S/ 3606.43
- Diferencia: -S/ 1060.72

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
- Saldo origen: S/ 4152.86 (la semana del 13/04 NO se cuenta como consumida)

---

## TC-7: Martes - semana no consumida (CONTADO)

**Entradas:**
- Fecha de traslado: 14/04/2026 (martes)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO

**Esperado (verificado en `zproyect/test/test_traslados.py`):**
- Saldo origen: S/ 4152.86 (igual que TC-6)

---

## TC-8: Miércoles - semana SÍ consumida (CONTADO)

**Entradas:**
- Fecha de traslado: 15/04/2026 (miércoles)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CONTADO

**Esperado (verificado en `zproyect/test/test_traslados.py`):**
- Saldo origen: S/ 4043.57 (menor que TC-6/TC-7: el miércoles sí consume la semana)

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

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 739.28"
- Saldo origen: S/ 2513.57
- Costo destino: S/ 1774.29
- Semanas consumidas (origen y destino): 19 de 40 (la semana feriado 27/07–02/08 no se cuenta)

---

## TC-13: Cuota vigente cuyo periodo incluye una semana de feriado (CUOTAS)

**Entradas:**
- Fecha de traslado: 05/08/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (cuota vigente: cuota 5, S/ 510, periodo 04/07/2026–08/08/2026 → 5 semanas, incluye la semana de Fiestas Patrias)
- Ciclo Destino: ANUAL MARZO, SM, VIRTUAL, CUOTAS (cuota vigente: cuota 5, S/ 360, mismo periodo)

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 60.00"
- Saldo origen: S/ 204.00 (= 510 × 2/5: de las 4 semanas transcurridas del periodo, 1 es la semana feriado y no cuenta como consumida → solo 3 consumidas, 2 restantes)
- Costo destino: S/ 144.00 (= 360 × 2/5)

**Nota (resuelta 2026-07-07, ver TC-14/TC-15):** la limitación que describía esta nota — el bloque `detalle` de CUOTAS mostraba las semanas del ciclo completo en vez del periodo de la cuota vigente — está corregida. `detalle.origen/destino` ahora usa, para CUOTAS, exactamente las semanas de `_detalle_semanas_periodo` (4 semanas totales / 2 consumidas / 2 restantes para este caso), las mismas que calculan el monto.

---

## TC-14: Desglose humano CUOTAS (AC-3.4) — verificado, ejemplo aportado por el usuario

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

## TC-15: Desglose humano CONTADO (AC-3.5) — verificado, ejemplo aportado por el usuario

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: SEMIANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 3213, duration_weeks: 28, fecha_inicio: 16/03/2026, fecha_fin: 02/10/2026)
- Ciclo Destino: SEMIANUAL MARZO, SM, VIRTUAL, CONTADO (cash_price: S/ 2268, duration_weeks: 28, mismas fechas)

**Esperado (verificado en `zproyect/test/test_traslados.py`, AC-3.5/TC-15):**
- Estado: SALDO_A_FAVOR — Mensaje: "Saldo a favor: S/ 651.72"
- Saldo origen: S/ 2215.86 — Costo destino: S/ 1564.14 — Diferencia: S/ 651.72
- `detalle.origen`: `semanas_totales: 29, semanas_consumidas: 9, semanas_restantes: 20`

**`detalle.origen.pasos` (desglose humano real, `generar_pasos_contado`):**
1. "Ciclo origen: fecha de traslado 15/05/2026 (viernes)."
2. "El ciclo inicia el 16/03/2026 y termina el 02/10/2026."
3. "La fecha de traslado cae en la semana 9 del ciclo (11/05/2026 al 17/05/2026)."
4. "Como es viernes (miércoles a domingo consumen la semana), esa semana SÍ se cuenta como consumida."
5. "Semanas consumidas: 9."
6. "Dentro del ciclo completo hay 1 semana(s) de feriado (cuentan igual, haya pasado el traslado antes o después de que ocurran)."
7. "Semanas efectivas del ciclo = duración (28) + semanas feriado (1) = 29."
8. "Semanas restantes = semanas efectivas (29) − semanas consumidas (9) = 20."
9. "Valor por semana = cash_price (S/ 3213.00) ÷ semanas efectivas (29) = S/ 110.7931."
10. "Saldo = valor por semana × semanas restantes (20) = S/ 2215.86 (redondeo half-up a 2 decimales)."

**Nota de verificación cruzada:** ambos TC-14 y TC-15 fueron calculados primero a mano por el usuario y luego confirmados exactos (mismos 6 valores, sin ninguna diferencia de redondeo) ejecutando `calcular_traslado()` contra el código real — ver `decisions.md`, entrada 2026-07-07, para las aclaraciones sobre reglas de redondeo que surgieron de esa verificación (round() vs ceil() en semanas de periodo; ROUND_HALF_UP vs round() nativo en montos).
