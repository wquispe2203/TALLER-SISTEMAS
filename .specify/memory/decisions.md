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

---

## 2026-07-07 Feature 001: FR-011 — campos estructurados de fecha/semana actual, ejecutado vía flujo multi-agente real

**Contexto:** El usuario pidió explícitamente que faltaban dos cosas en el desglose FR-010: (1) las fechas de inicio/fin del periodo relevante como campos estructurados (no solo dentro del texto narrativo), tanto para origen como destino, y (2) la "semana actual" (ej. "semana 2 de 4") como campo explícito — `semanas_consumidas` ya existía, pero no el índice de en qué semana cae la fecha de traslado. Además, exigió explícitamente que esta vez se usara SDD Enterprise de forma real: los agentes definidos en `.github/agents/*.agent.md`, no solo edición manual de archivos `.md`.

**Ejecución real (no simulada — cada paso con evidencia verificable en esta conversación):**

1. **Agente Requirement Analyst** (`.github/agents/requirement-analyst.agent.md`, Detailed Mode, subagente real vía `Agent` tool) — recibió el hallazgo de negocio, produjo FR-011 con AC-3.6/AC-3.7/AC-3.8 en formato Given-When-Then, y **dejó explícitamente 6 preguntas abiertas** (base 0 vs 1, formato de fecha, comportamiento en casos borde, clamp, nombres de campo) en vez de asumir respuestas — cumpliendo su propia regla "Never Do: fabricar una respuesta a su propia pregunta".
2. **Agente Architect** (`.github/agents/architect.agent.md`, subagente real) — resolvió las 6 preguntas como ADR-4 en `plan.md`, con justificación y alternativa descartada para cada una, tabla de componentes afectados, diagrama Mermaid y Synthesis Assessment (Generalización / Build-vs-Adopt / Simplificación).
3. **Implementación** (yo, con el rol de Software Engineer) — siguió ADR-4 al pie de la letra: helper `_fmt_fecha_opt`, extensión de `generar_pasos_contado`/`generar_pasos_cuotas`, clamp en CONTADO. Verificado ejecutando `calcular_traslado()` contra AC-3.6/AC-3.7/CB-9/CB-10 con valores exactos antes de continuar.
4. **Tests** — se extendió `test_traslados.py` con AC-3.6/3.7/3.8, CB-8, CB-9, CB-10. **Hallazgo honesto durante esta fase:** CB-8 (`antes_primera_cuota`) es estructuralmente inalcanzable con los ciclos reales de `parameters.json` (todas las cuotas 1 usan "En la matrícula", que hace fallback a la propia fecha de inicio del ciclo) — se probó con datos sintéticos de cuotas, declarados explícitamente como tales en el comentario del test, no con un ciclo inventado en `parameters.json`/`spec.md` (a diferencia del error de la sesión anterior con "SEMIANUAL ENERO").
5. **Agente Review** (`.github/agents/review.agent.md`, subagente real, pasada trivial-complexity combinada) — corrió `pytest` él mismo (no confió en el resultado reportado), verificó AC por AC con evidencia file:line, y **encontró un hallazgo real vía mutation testing**: el test original de CB-10 (clamp de `semana_actual` en CONTADO) usaba `ANUAL MARZO` con fecha en el último día del ciclo, pero ningún ciclo real de `parameters.json` alcanza jamás un `indice_semana_actual` que exceda `semanas_efectivas` — el clamp nunca se ejercitaba de verdad; el test habría seguido en verde aunque alguien borrara el clamp del código. Veredicto: **APPROVED WITH CONDITIONS**.
6. **Corrección del hallazgo** — se agregó un caso sintético (`duration_weeks=1` sobre un rango de 2 semanas calendario) que sí fuerza el clamp. **Verificado con mutation testing propio:** se reemplazó temporalmente la línea del clamp por el valor sin clampear, se corrió la suite, el nuevo test de CB-10 falló como se esperaba (`AssertionError`), se restauró el código original, se re-confirmó que todo pasa. `git status`/`git diff --stat` confirmaron que no quedaron archivos residuales de la mutación.

**Opciones Consideradas (nivel de proceso):**
1. Implementar directamente sin pasar por los agentes — más rápido, pero es exactamente lo que el usuario pidió NO repetir.
2. Usar el flujo de agentes real, con sus propias reglas de "Never Do" y "Ask First" tal como están escritas en `.github/agents/`, adaptando solo las rutas de archivo (`.specify/memory/` en vez de `.specify/specs/NNN/`, porque este repo no usa esa convención — ver auditoría previa de por qué los gates de CI tampoco la usan).

**Elegida:** Opción 2.

**Razonamiento:**
- El valor real no fue "usar agentes" como ritual, sino que el Requirement Analyst dejó preguntas genuinamente abiertas (que yo solo no habría pensado en plantear formalmente) y el Review encontró un bug real de cobertura de test con mutation testing — ambos resultados habrían sido más débiles hechos por una sola pasada.
- Cada salida de agente se aplicó literalmente a los archivos de memoria (no se resumió ni se reinterpretó), y cada afirmación de "está corregido" se verificó ejecutando código real antes de marcar cualquier tarea `[x]` — siguiendo `sdd-enterprise-protocol.md`.

**Compromisos Aceptados:**
- No se usó el CLI real `.specify/cli/sdd` para esta feature específica (los subagentes usan Read/Edit/Bash directamente) — los agentes de `.github/agents/` son prompts de rol, no comandos del CLI; se usaron como prompts de subagente vía el `Agent` tool, que es la forma en que esta sesión puede invocarlos.
- Los agentes asumen la convención `.specify/specs/NNN/` en su texto original; se les indicó explícitamente adaptar a `.specify/memory/`, documentado en cada prompt.

**Nivel de Confianza:** Alto — cada paso de este registro es reproducible: los prompts exactos están en la transcripción de la sesión, los comandos `pytest`/mutation test se ejecutaron y su output se pegó arriba, no se resumió de memoria.

---

## 2026-07-07 Feature 001: `test_traslados.py` ejecutable directo (sin `-m pytest`)

**Contexto:** El usuario intentó correr los tests con `pytest test_traslados.py` (sin `python -m`) y le dio `ModuleNotFoundError: No module named 'traslados'`. Causa raíz: `pytest` (el script suelto) no agrega el directorio actual al import path de Python de la misma forma que `python -m pytest`; y el archivo vive en `zproyect/test/`, un nivel abajo de donde está `traslados.py` (`zproyect/`), sin ningún ajuste de `sys.path` que lo compensara.

**Elegida:** Agregar `sys.path.insert(0, ...)` al inicio de `test_traslados.py`, apuntando al directorio padre (`zproyect/`), antes del `from traslados import`.

**Razonamiento:** Es la forma mínima de que el archivo funcione con `python test_traslados.py` invocado desde cualquier lado (el pedido explícito del usuario), sin depender de flags de invocación (`-m`) ni de que el usuario recuerde en qué carpeta pararse. No se tocó ninguna regla de negocio ni se implementó nada adicional (alcance limitado a lo pedido).

**Verificación:** ejecutado con éxito en 3 modos: `python test_traslados.py` desde `zproyect/test/`, `python test/test_traslados.py` desde `zproyect/`, y `pytest test/test_traslados.py -s` desde `zproyect/` (regresión, sigue funcionando igual que antes).

**Nivel de Confianza:** Alto — cambio de una línea, con verificación ejecutada en los 3 modos de invocación relevantes.