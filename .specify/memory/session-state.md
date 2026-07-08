---
# Wave 23 §23.A.9/§23.A.10 — memory frontmatter for time-decay ranking
last_referenced_at: "2026-07-07T02:00:00.000000+00:00"
reference_count: 3
---
# Estado de la Sesión

> **Actualizado automáticamente** por scripts de gate y agentes. Se permiten ediciones manuales.
> Nota (2026-07-07): este frontmatter estaba congelado en 2026-04-11 con `reference_count: 0` en los 8 archivos de memoria — anterior incluso al primer commit real del proyecto (2026-06-15). Eso confirma que los "scripts de gate" automáticos nunca corrieron sobre este repo; esta actualización fue manual.

## Funcionalidad Activa

- **ID de la Funcionalidad:** transfer-calculator
- **Nombre de la Funcionalidad:** Calculadora de Montos de Traslado Académico
- **Nivel de Ceremonia:** estándar
- **Fase Actual:** Implementación (US-6 / FR-011 completada vía flujo multi-agente real: Requirement Analyst → Architect → implementación → Review; T004/T005/T007-T010/T012/T016/T017 siguen pendientes)
- **Último Gate Aprobado:** Review (`.github/agents/review.agent.md`, pasada trivial-complexity) — veredicto APPROVED WITH CONDITIONS, condición resuelta el mismo día (ver `decisions.md`)
- **Marca de Tiempo del Último Gate:** 2026-07-07

## Progreso de Fases

- [x] Fase 0: Constitución — `constitution.md` tiene contenido específico del proyecto, sin contradicciones con el código.
- [x] Fase 1: Requerimientos (Gate 1) — AC-1.1/1.2/1.3/3.4/3.5 de `spec.md` verificados ejecutando `calcular_traslado()` contra datos reales.
- [ ] Fase 2: Diseño (Gate 2) — `plan.md` describe separar `validation.py`/`calculator.py`; el código real mantiene ambos junto con el cálculo en `traslados.py` (ver T004/T005, pendientes).
- [ ] Fase 3: Preparación (Gate 3) — `tasks.md` tiene 9 de 20 tareas sin marcar (T004, T005, T007, T008, T009, T010, T012, T016, T017).
- [ ] Fase 4: Implementación — endpoint core, UI, desglose completo (US-3/US-5, ya no roto para CUOTAS) funcionan; validaciones en cascada explícitas (T009/T010) y refactor a módulos separados (T004/T005) siguen pendientes — las validaciones SÍ existen hoy dentro de `traslados.py` (PASO 1-3 de `calcular_traslado`), solo no están en `validation.py` como planeaba `plan.md`.
- [ ] Fase 5: Aseguramiento de Calidad (Gate 4) — `zproyect/test/test_traslados.py` corre limpio (`pytest -s`, todas las verificaciones OK), pero: no hay cobertura medida (T017), ruff no se ha corrido (T016), y el archivo no define `def test_*` (pytest reporta "0 items"/exit 5 aunque todo pase — ver nota en T020 de `tasks.md`).

## Agente Actual

- **Activo:** (ninguno)
- **Modo:** —

## Decisiones Clave (De esta Funcionalidad)

<!-- Poblado a partir de aclaraciones específicas de la funcionalidad y el plan -->
- Se adoptó stack Python full-stack: Flask + HTML/CSS/JS vanilla.
- Endpoint real: `POST /api/traslados/calcular` (corregido 2026-07-07; nunca fue `/api/transfer-calculator`).
- Parámetros desde `data/parameters.json`.
- Dependencias en `requirements.txt` (Flask, pytest, pytest-cov, ruff).
- CUOTAS prorratea solo la cuota vigente a la fecha de traslado (no suma cuotas futuras completas) — ver `traslados.py::calcular_valor_cuotas`.
- FR-010 (2026-07-07): el desglose (`detalle.origen/destino`) se narra paso a paso ("cálculo manual"), no solo como resultado de una resta — ver `traslados.py::generar_pasos_contado`/`generar_pasos_cuotas`.
- FR-011 (2026-07-07): `detalle.origen/destino` expone `fecha_inicio_periodo`, `fecha_fin_periodo`, `semana_actual` como campos estructurados (no solo dentro de `pasos`) — ver ADR-4 en `plan.md`.

## Archivos Modificados

### Sesión 1 (2026-07-07, sincronización inicial contra código)
- `.specify/memory/test-cases.md`, `spec.md`, `plan.md`, `tasks.md`, `decisions.md`, `lessons.md`, `session-state.md`, `memory-index.md` — ver historial de decisiones para el detalle completo.

### Sesión 2 (2026-07-07, FR-010 — desglose estilo cálculo manual, vía SDD)
- `.specify/memory/spec.md` — agregado FR-010, AC-3.4, AC-3.5; resuelta la nota de brecha de AC-3.1.
- `.specify/memory/tasks.md` — agregada Fase 8 (US-5): T018, T019, T020, todas marcadas `[x]` tras verificación real con `pytest -s`.
- `.specify/memory/decisions.md` — nueva entrada: diseño del desglose (reutiliza funciones existentes, no duplica fórmulas — Art. 4.4), aclaraciones de redondeo (round() vs ROUND_HALF_UP), y hallazgo adicional: el mismo bug de CUOTAS (detalle usando semanas del ciclo completo) también existía en CONTADO.
- `.specify/memory/test-cases.md` — agregados TC-14 (CUOTAS) y TC-15 (CONTADO), con el desglose humano completo, verbatim de lo verificado en `test_traslados.py`.
- `zproyect/traslados.py` — nuevas funciones `_detalle_semanas_periodo`, `_seleccionar_cuota_vigente`, `generar_pasos_cuotas`, `generar_pasos_contado`; refactor de `_prorratear_cuota` y `calcular_valor_cuotas` para usarlas (comportamiento idéntico, verificado sin regresiones); `calcular_traslado` ahora arma `detalle.origen/destino` (incluyendo `pasos`) a partir de estas funciones en vez de `calcular_semanas_consumidas` directo.
- `zproyect/test/test_traslados.py` — **corregido TC-3** (esperaba 4080.00, ahora 382.50, la brecha original que motivó toda esta sesión); agregadas verificaciones de `detalle` para TC-1 y TC-3/TC-9; agregados los bloques AC-3.4/TC-14 y AC-3.5/TC-15.

### Sesión 3 (2026-07-07, FR-011 — campos de fecha/semana actual, vía flujo multi-agente real)
- **Agentes reales invocados** (subagentes vía `Agent` tool, usando literalmente los prompts de `.github/agents/*.agent.md`, adaptados solo en rutas de archivo): Requirement Analyst (Detailed Mode) → Architect → Review (pasada trivial-complexity). Transcripción completa de cada salida disponible en la conversación de esta sesión.
- `.specify/memory/spec.md` — agregada "Extensión a US-3": FR-011, AC-3.6, AC-3.7, AC-3.8, CB-8, CB-9, CB-10 (producido por el agente Requirement Analyst).
- `.specify/memory/plan.md` — agregado ADR-4 (producido por el agente Architect: resuelve 5 decisiones de diseño con diagrama Mermaid y Synthesis Assessment).
- `.specify/memory/tasks.md` — agregada Fase 9 (US-6): T021, T022, T023, marcadas `[x]` tras verificación real.
- `zproyect/traslados.py` — nuevo helper `_fmt_fecha_opt`; `generar_pasos_contado`/`generar_pasos_cuotas` extendidas con los 3 campos nuevos, siguiendo ADR-4 al pie de la letra (clamp en CONTADO, `null` explícito en casos borde de CUOTAS).
- `zproyect/test/test_traslados.py` — agregados bloques AC-3.6/3.7/3.8, CB-8 (sintético, documentado como tal), CB-9, CB-10 (con caso sintético agregado tras el hallazgo del Review).
- `.specify/memory/decisions.md` — nueva entrada "FR-011" con el registro completo del flujo de 6 pasos, incluyendo el hallazgo del Review (mutation testing sobre CB-10) y su corrección verificada.
- `.specify/memory/lessons.md` — nueva entrada sobre por qué un test con datos reales puede no probar nada si no fuerza genuinamente el caso borde.
- `.specify/memory/detalle-operaciones-referencia.md` **(nuevo)** — catálogo de referencia de todos los campos de `detalle`, pedido explícitamente por el usuario ("arma un md").

**Verificación final de esta sesión:** `pytest -s` sobre `zproyect/test/test_traslados.py` → 49 verificaciones `check()`, todas `OK`. Mutation testing manual sobre el clamp de CONTADO: con el clamp removido, el nuevo test de CB-10 falla (`AssertionError`); restaurado, todo vuelve a pasar. `git status`/`git diff --stat` confirmados limpios de residuos.

## Siguiente Paso

- T004/T005: separar `traslados.py` en `validation.py` + `calculator.py`.
- T007/T008: pruebas unitarias formales adicionales para CONTADO/CUOTAS (más allá de las ya existentes).
- T012: botón de copiado rápido en la UI.
- T016/T017: correr ruff y medir cobertura con pytest-cov (objetivo ≥80% según constitution.md Art. 3.2).
- Opcional: convertir `test_traslados.py` de asserts a nivel de módulo a funciones `def test_*` reales, para que `pytest` reporte los resultados de forma estándar (actualmente exit code 5 aunque todo pase — señalado también por el agente Review).
- Opcional: exponer `pasos`/`fecha_inicio_periodo`/`fecha_fin_periodo`/`semana_actual` en la UI (`zproyect/static/js/app.js` / `templates/index.html`) — hoy el backend ya los devuelve en el JSON, pero el frontend no los renderiza (fuera del alcance pedido en esta sesión).
- Opcional (menor, señalado por el Review): reforzar el test de AC-3.8 con un escenario donde origen y destino tengan fechas de ciclo distintas, no solo verificar presencia de claves.

## Operaciones de Memoria

- **Última Sincronización de Memoria:** 2026-07-07 (tres sesiones el mismo día: sincronización inicial → FR-010 desglose humano → FR-011 campos estructurados vía flujo multi-agente real, todas verificadas ejecutando código real, ninguna automática)
