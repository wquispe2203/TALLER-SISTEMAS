---
name: detalle-operaciones-referencia
description: Catálogo de referencia de todos los campos que devuelve detalle.origen/detalle.destino en POST /api/traslados/calcular, con ejemplos reales verificados.
---

# Referencia: campos de `detalle` (desglose "estilo cálculo manual")

> Complementa `spec.md` (FR-006, FR-010, FR-011) con una vista práctica de tabla, pensada para quien construye la UI o explica el cálculo a un analista de soporte. Todos los valores de ejemplo de este documento fueron generados ejecutando `zproyect/traslados.py` contra `zproyect/data/parameters.json` — no son cálculos a mano.

## ¿Dónde vive esto en el código?

`calcular_traslado()` (`zproyect/traslados.py`) llama a **una sola función por modalidad** — `generar_pasos_contado()` o `generar_pasos_cuotas()` — que calcula el monto, arma el texto narrado (`pasos`) y arma los campos estructurados, todo a partir de los mismos números. Nunca hay dos cálculos separados que puedan desincronizarse (Art. 4.4 de la constitución).

## Campos de `detalle.origen` / `detalle.destino`

| Campo | Tipo | CONTADO significa... | CUOTAS significa... |
|---|---|---|---|
| `semanas_totales` | integer | Semanas efectivas del ciclo completo (`duration_weeks` + semanas feriado del ciclo) | Semanas del periodo de la cuota vigente |
| `semanas_consumidas` | integer | Semanas ya transcurridas del ciclo (regla lunes/martes no consumen, miércoles-domingo sí) | Semanas ya transcurridas del periodo de la cuota vigente |
| `semanas_restantes` | integer | `semanas_totales − semanas_consumidas` | `semanas_totales − semanas_consumidas` |
| `fecha_inicio_periodo` | string `DD/MM/YYYY` o `null` | Fecha de inicio del ciclo completo | Fecha de inicio del periodo de la cuota vigente — **`null` si aún no ha empezado ningún periodo** (fecha de traslado anterior a la cuota 1) |
| `fecha_fin_periodo` | string `DD/MM/YYYY` o `null` | Fecha de fin del ciclo completo | Fecha de vencimiento de la cuota vigente — **`null` si no queda ninguna cuota pendiente** (fecha de traslado ≥ fin del ciclo) |
| `semana_actual` | integer (1-based) o `null` | En qué semana del ciclo cae la fecha de traslado (clampeada, nunca excede `semanas_totales`) | En qué semana del periodo de la cuota vigente cae la fecha de traslado — **`null`** si no hay periodo vigente |
| `pasos` | array de string | Narrativa completa, paso a paso, en español | Narrativa completa, paso a paso, en español |
| `valor` *(interno, no viaja en el JSON — se usa para `saldo_origen`/`costo_destino`)* | Decimal | Monto residual calculado | Monto residual calculado |

**Regla general:** `1 ≤ semana_actual ≤ semanas_totales` siempre que `semana_actual` no sea `null`. Si es `null`, los otros dos campos de fecha también son `null` — nunca hay una combinación parcial.

## Ejemplo 1 — CONTADO (verificado)

**Input:** `fecha_traslado=15/05/2026`, origen `SEMIANUAL MARZO / SM / Presencial / Contado`, destino `SEMIANUAL MARZO / SM / Virtual / Contado`.

```json
{
  "saldo_origen": 2215.86,
  "costo_destino": 1564.14,
  "diferencia": 651.72,
  "estado": "SALDO_A_FAVOR",
  "detalle": {
    "origen": {
      "semanas_totales": 29,
      "semanas_consumidas": 9,
      "semanas_restantes": 20,
      "fecha_inicio_periodo": "16/03/2026",
      "fecha_fin_periodo": "02/10/2026",
      "semana_actual": 9
    }
  }
}
```

## Ejemplo 2 — CUOTAS (verificado)

**Input:** `fecha_traslado=25/03/2026`, origen `ANUAL MARZO / SM / Presencial / Cuotas`, destino `ANUAL MARZO / SM / Virtual / Cuotas`.

```json
{
  "saldo_origen": 382.50,
  "costo_destino": 270.00,
  "diferencia": 112.50,
  "estado": "SALDO_A_FAVOR",
  "detalle": {
    "origen": {
      "semanas_totales": 4,
      "semanas_consumidas": 1,
      "semanas_restantes": 3,
      "fecha_inicio_periodo": "16/03/2026",
      "fecha_fin_periodo": "11/04/2026",
      "semana_actual": 2
    }
  }
}
```

Nótese: en CUOTAS, `fecha_inicio_periodo`/`fecha_fin_periodo` son las fechas de la **cuota vigente** (16/03–11/04), no las del ciclo completo (16/03–31/12) — es el error que existía antes de FR-011/AC-3.1 y ya está corregido.

## Ejemplo 3 — CUOTAS, sin periodo vigente (`null` explícito)

**Input:** `fecha_traslado=31/12/2026` (fin exacto del ciclo), CUOTAS — no queda ninguna cuota pendiente.

```json
{
  "detalle": {
    "origen": {
      "semanas_totales": 0,
      "semanas_consumidas": 0,
      "semanas_restantes": 0,
      "fecha_inicio_periodo": null,
      "fecha_fin_periodo": null,
      "semana_actual": null
    }
  }
}
```

## Preguntas frecuentes

**¿Por qué a veces `fecha_inicio_periodo` es `null`?** Porque no existe ningún periodo de cuota vigente que describir en ese momento (la fecha de traslado es anterior a la primera cuota, o el ciclo ya terminó). El sistema nunca inventa una fecha de relleno — eso violaría la regla de "nunca asumir valores por defecto" de la constitución (Art. 7).

**¿Por qué CUOTAS y CONTADO calculan "semana actual" distinto?** Porque anclan las semanas a cosas distintas: CONTADO ancla al lunes del calendario global (toda la institución comparte la misma "semana 1"); CUOTAS ancla al día en que empezó esa cuota específica (cada cuota puede empezar cualquier día). Ambas reglas de negocio ya existían antes de este documento — acá solo se exponen como campos.

**¿Puedo confiar en `pasos` como fuente de verdad, o en los campos estructurados?** En cualquiera de los dos — se generan del mismo cálculo, en la misma función, nunca por separado.

## Trazabilidad

- Requisito: `spec.md` → FR-011, AC-3.6, AC-3.7, AC-3.8, CB-8, CB-9, CB-10.
- Diseño: `plan.md` → ADR-4.
- Implementación: `zproyect/traslados.py` → `_fmt_fecha_opt`, `generar_pasos_contado`, `generar_pasos_cuotas`.
- Tests: `zproyect/test/test_traslados.py` (bloques AC-3.6/3.7/3.8, CB-8/9/10).
- Historial de decisiones y ejecución del flujo multi-agente: `decisions.md`, entrada "FR-011" (2026-07-07).
