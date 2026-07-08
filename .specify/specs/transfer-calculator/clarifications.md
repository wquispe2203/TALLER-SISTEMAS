# Clarifications

## 2026-07-07: Desglose estilo cálculo manual (FR-010)

- Redondeo de "semanas totales del periodo" en CUOTAS: se usa round() (half-to-even), no ceil()
- Semanas feriado contadas aunque el traslado sea antes de que ocurran
- Redondeo final de montos: Decimal.quantize con ROUND_HALF_UP, no round() nativo

## 2026-07-07: Campos estructurados (FR-011)

- Base de semana_actual: 1-based
- Formato de fecha: DD/MM/YYYY
- CB-8/CB-9: null explícito, sin fallback inventado
- Clamp de semana_actual en CONTADO: sí, agregar
- Nombres de campo: unificados, sin prefijo por modalidad
