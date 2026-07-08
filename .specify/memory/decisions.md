---
# Wave 23 §23.A.9/§23.A.10 — memory frontmatter for time-decay ranking
last_referenced_at: "2026-04-11T16:24:38.141489+00:00"
reference_count: 0
---
# Registro de Decisiones

> Decisiones de diseño y arquitectura **a nivel de proyecto** con su respectiva justificación.
> Los agentes añaden entradas cuando se toman decisiones importantes durante la Planificación o la Implementación.
> Se recomienda la revisión humana después de cada funcionalidad.

---

## Cómo Usar

Después de tomar una decisión importante, añade una nueva entrada:

```
## [AAAA-MM-DD] Funcionalidad NNN: [Título de la Decisión]

**Contexto:** [Por qué se necesitó esta decisión]

**Opciones Consideradas:**
1. [Opción A] — [pros/contras]
2. [Opción B] — [pros/contras]

**Elegida:** Opción [X]

**Razonamiento:**
- [Razón clave 1]
- [Razón clave 2]

**Compromisos Aceptados:**
- [Compromiso 1]

**Nivel de Confianza:** [Alto/Medio/Bajo]
```

---

## Decisiones

<!-- Añadir nuevas decisiones debajo de esta línea -->

## 2026-07-01 Feature 001: Adoptar una app web simple con frontend HTML/CSS y backend Node.js

**Context:** La especificación tenía definiciones pendientes sobre la forma de implementación de la solución, y se necesitaba elegir una propuesta concreta para la interfaz y el servicio de cálculo.

**Options Considered:**
1. Implementación basada en Python y una interfaz simple — alineada con la constitución previa, pero menos directa para una demo rápida.
2. Aplicación web sencilla con HTML/CSS y un backend en Node.js con endpoint HTTP — adecuada para la propuesta solicitada.

**Chosen:** Option 2

**Reasoning:**
- Permite una interfaz simple y rápida de usar.
- Mantiene la lógica de negocio separada de la presentación.
- Facilita exponer un endpoint para calcular traslados y probarlo fácilmente.

**Trade-offs Accepted:**
- Se adopta un stack distinto al descrito inicialmente en la constitución, pero con un enfoque más práctico para la entrega del taller.

**Confidence:** High

---

## 2026-07-01 Feature 001: Stack Python full-stack con Flask

**Contexto:** Se evaluó usar Node para frontend y Python para API, Node puro, o Python full-stack. La constitución exige Python 3.11+, PEP8 y cobertura ≥80% con tests unitarios. Un stack híbrido añade complejidad (dos procesos, CORS) sin beneficio para una app web simple.

**Opciones consideradas:**
1. Node.js frontend + Python API — válido en enterprise, pero dos runtimes y CORS para un taller.
2. Solo Node.js — simple, pero desalineado con la constitución.
3. Solo Python con Flask sirviendo HTML/CSS/JS estáticos + endpoint REST — alineado con constitución y un solo proceso.

**Elegida:** Opción 3

**Razonamiento:**
- Un solo comando levanta UI y API.
- La lógica de cálculo y validación queda en Python puro, testeable con pytest.
- Flask sirve `templates/` y `static/` sin framework frontend adicional.
- Cumple separación de capas: `calculator.py` / `validation.py` independientes de rutas HTTP.

**Stack acordado:**
- Python 3.11+
- Flask (HTTP + estáticos)
- `decimal.Decimal` (montos en soles)
- `datetime` (fechas DD/MM/YYYY)
- pytest + pytest-cov (tests, ≥80% en lógica de negocio)
- ruff (PEP8 / formato)

**Compromisos aceptados:**
- Se revoca la decisión previa de backend Node.js (2026-07-01, entrada anterior).
- No se usa SPA ni bundler; frontend vanilla HTML/CSS/JS.
- Dependencias declaradas en `requirements.txt` en la raíz del proyecto.

**Nivel de confianza:** Alto
---

## 2026-07-04 Feature 001: Adoptar algoritmo v4 como referencia canónica

**Contexto:** Se identificaron discrepancias entre la especificación original (spec.md), el plan (plan.md) y los casos de prueba (test-cases.md) con respecto al algoritmo de traslados académicos v4, el cual se considera la implementación definitiva basada en el Excel oficial de Gerencia.

**Opciones Consideradas:**
1. Mantener los artefactos actuales y ajustar el algoritmo a la especificación — inviable, el algoritmo ya está validado contra el Excel.
2. Actualizar todos los artefactos para alinearlos con el algoritmo v4 — asegura consistencia con la fuente única de verdad.

**Elegida:** Opción 2

**Razonamiento:**
- El algoritmo y el archivo parameters.json (generado desde el Excel oficial) son la única fuente de verdad.
- Los artefactos anteriores (FR sobre estados, descuentos, beneficios) ya no aplican al algoritmo actual.
- Alinear todo con el algoritmo v4 elimina ambigüedades y garantiza que los estándares de calidad se midan sobre la base correcta.

**Compromisos Aceptados:**
- Se requiere actualizar spec.md, plan.md, test-cases.md, constitution.md y otros archivos de memoria.
- Los casos de prueba antiguos (TC-4 a TC-16) quedan obsoletos y se reemplazan por los 12 casos del algoritmo.

**Nivel de Confianza:** Alto

---

## 2026-07-07 Feature 001: Sincronizar toda la memoria contra `app.py`/`traslados.py` ejecutados (no contra el Excel ni cálculos manuales)

**Contexto:** Al auditar `.specify/memory`, se detectó que la sincronización de la entrada anterior (2026-07-04) quedó incompleta: `test-cases.md` seguía referenciando dos ciclos que **no existen** en `data/parameters.json` ("SEMIANUAL ENERO, SM" y "ANUAL MARZO, UNI") y varios valores esperados (TC-3, TC-6, TC-7, TC-8) correspondían a la fórmula CUOTAS/CONTADO anterior a la v4. `tasks.md` marcaba T003 como `[x]` completado pese a que esto seguía roto — el checkbox no reflejaba la realidad. Además, `spec.md`, `plan.md`, `session-state.md` y `tasks.md` documentaban el endpoint como `POST /api/transfer-calculator`, que nunca existió en el código; el real es `POST /api/traslados/calcular`.

**Opciones Consideradas:**
1. Corregir solo los valores numéricos incorrectos y dejar el resto — más rápido, pero perpetúa la causa raíz (nadie ejecutó el código para verificar).
2. Regenerar cada valor esperado ejecutando `calcular_traslado()` directamente contra `parameters.json` real, usando únicamente ciclos verificados como existentes, y documentar explícitamente qué se cambió y por qué.

**Elegida:** Opción 2

**Razonamiento:**
- `app.py` y `traslados.py` son la fuente de verdad del comportamiento real del sistema (el código es "la ley"); la memoria debe describir lo que el código hace, no lo que se planeó que hiciera.
- Verificar ejecutando el código (en vez de recalcular a mano) elimina la clase de error que causó esta desincronización en primer lugar.
- Se documentó además una limitación real no registrada antes: en modalidad CUOTAS, el bloque `detalle` de la respuesta usa una fórmula de semanas distinta a la que realmente calcula el monto (ver TC-13 y spec.md → AC-3.1).

**Compromisos Aceptados:**
- `test-cases.md` reescrito completo (13 casos, todos verificados por ejecución real, ver nota de sincronización al inicio del archivo).
- `spec.md` (endpoint real, nota de limitación en AC-3.1) y `plan.md` (estructura real de archivos, endpoint real, estado real de la separación validation/calculator) corregidos.
- **Pendiente fuera de este alcance:** `zproyect/test/test_traslados.py` (el test ejecutable real) todavía falla en su aserción de TC-3 con el valor viejo (4080.00) — no se tocó porque el pedido de esta sesión fue limitado a `.specify/memory`. Debe corregirse por separado.

**Nivel de Confianza:** Alto

---

## 2026-07-07 Feature 001: Diseño del desglose "estilo cálculo manual" (FR-010) y aclaración de reglas de redondeo

**Contexto:** El usuario pidió que el desglose de operaciones (US-3/FR-006) deje de mostrarse como una resta directa y narre el cálculo como lo haría un analista a mano — mostrando en qué semana cae la fecha, desde cuándo empieza esa semana, cuántas semanas van consumidas, etc. Esto además cierra la brecha real detectada el mismo día: `detalle` en CUOTAS mostraba las semanas del ciclo completo, no las del periodo de la cuota vigente que realmente usa la fórmula.

**Opciones Consideradas:**
1. Construir el desglose con una lógica nueva y paralela a `calcular_valor_contado`/`calcular_valor_cuotas` — más simple de escribir, pero duplica fórmulas (viola Art. 4.4 de la constitución: "no duplicar fórmulas de cálculo en múltiples componentes") y arriesga que texto y monto se desincronicen otra vez.
2. Extraer los valores intermedios que las funciones de cálculo YA computan internamente (semana índice, periodo de la cuota, semanas feriado) hacia funciones auxiliares reutilizables, y una función narradora que arma el texto a partir de esos mismos intermedios.

**Elegida:** Opción 2

**Razonamiento:**
- Garantiza que el texto explicativo y el monto final siempre sean consistentes, porque ambos se derivan de los mismos números.
- Es exactamente el patrón que ya pedía `plan.md` ADR-1 (separar cálculo de presentación) aplicado a la narrativa, no solo al monto.

**Aclaraciones verificadas contra el código real (respondiendo las dudas del usuario sobre sus dos ejemplos manuales):**
- **Redondeo de "semanas totales del periodo" en CUOTAS:** `_semanas_en_periodo` usa `round(dias / 7)` de Python (redondeo half-to-even), **no** `ceil()`. Para 26 días da 4 (round(3.714)=4), coincide con ceil en ese caso puntual, pero no es la regla general — hay que decirlo explícitamente en la narrativa para no inducir a error en otros periodos.
- **Semanas feriado contadas aunque el traslado sea antes de que ocurran:** confirmado. En CONTADO, `semanas_feriado` se cuenta sobre el ciclo completo (`fecha_inicio` a `fecha_fin`), no hasta la fecha de traslado — por eso extiende la duración total sin importar si el feriado ya pasó.
- **Redondeo final de montos:** el código usa `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`, no el `round()` nativo de Python (que redondea .5 al par más cercano). Son distintos en casos de empate exacto en el tercer decimal — la narrativa debe decir "redondeo half-up a 2 decimales", no "round() estándar".
- Ambos ejemplos manuales del usuario (CUOTAS 25/03/2026 → 382.50/270.00/112.50; CONTADO 15/05/2026 SEMIANUAL MARZO → 2215.86/1564.14/651.72) se verificaron **exactos** ejecutando `calcular_traslado()` contra `parameters.json` real. Quedan como AC-3.4 y AC-3.5 en `spec.md`, y como TC-14/TC-15 en `test-cases.md`.

**Compromisos Aceptados:**
- Nuevas funciones en `traslados.py`: `generar_pasos_contado`, `generar_pasos_cuotas` (T018), integradas en `detalle.origen/destino.pasos` (T019).
- `test_traslados.py` se corrige y se extiende (T020), incluyendo por fin la corrección de TC-3.

**Hallazgo adicional durante la implementación (2026-07-07):** al centralizar `detalle` en `generar_pasos_contado`, se descubrió que el bug de CUOTAS (semanas del ciclo completo en vez del periodo real) tenía un equivalente en CONTADO: `detalle.semanas_totales`/`semanas_restantes` usaban `duration_weeks` sin ajustar por feriados, mientras la fórmula real usa `semanas_efectivas = duration_weeks + semanas_feriado`. Para TC-1 (15/05/2026) esto mostraba `semanas_restantes: 31` en el detalle cuando la fórmula real usó `33`. Se corrigió igual que CUOTAS: `detalle` ahora deriva directamente de los mismos números que calculan el monto. Verificado con `pytest -s`, sin regresiones (ver `test_traslados.py`).

**Nivel de Confianza:** Alto