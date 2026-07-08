---
# Wave 23 §23.A.9/§23.A.10 — memory frontmatter for time-decay ranking
last_referenced_at: "2026-04-11T16:24:38.145323+00:00"
reference_count: 0
---
# Lecciones Aprendidas

> Registro **a nivel de proyecto** de lo que funcionó y lo que no.
> Los agentes añaden entradas después de correcciones, detección de bloqueos o gates fallidos.
> Se revisa al inicio de cada nueva funcionalidad.

---

## Cómo Usar

Después de una corrección, gate fallido o detección de bloqueo, añade:

```
## [AAAA-MM-DD] Funcionalidad NNN: [Título de la Lección]

**Qué Pasó:** [Breve descripción del problema]

**Causa Raíz:** [Por qué ocurrió]

**Qué Aprendimos:**
- [Lección 1]
- [Lección 2]

**Regla de Prevención:**
- [Cómo evitar esto en el futuro]
```

---

## Lecciones

<!-- Añadir nuevas lecciones debajo de esta línea -->

## 2026-07-01 Feature 001: Mantener la memoria sincronizada antes de seguir con la implementación

**What Happened:** Se avanzó con la implementación de la aplicación antes de registrar en memoria la arquitectura y los acuerdos tomados.

**Root Cause:** Los archivos de especificación estaban incompletos en algunas decisiones de implementación y la memoria seguía vacía en varias secciones.

**What We Learned:**
- Es mejor documentar la decisión de arquitectura y alcance antes de construir sobre ella.
- La memoria debe reflejar tanto los requerimientos como la solución elegida para evitar ambigüedades.

**Prevention Rule:**
- Actualizar decisions.md, session-state.md y el índice de memoria antes de continuar con cambios de implementación.
---

## 2026-07-04 Feature 001: Definir el algoritmo completo antes de redactar la especificación

**Qué Pasó:** Se redactó la especificación funcional (spec.md) antes de tener el algoritmo completo validado contra el Excel oficial, lo que generó discrepancias en campos de entrada, validaciones y casos de prueba.

**Causa Raíz:** No se partió del Excel y del algoritmo acordado con el negocio como base para redactar la spec.

**Qué Aprendimos:**
- Definir el algoritmo completo antes de redactar la especificación evita discrepancias y retrabajo.
- Los artefactos deben derivarse del algoritmo y del Excel, no al revés.

**Regla de Prevención:**
- En futuros proyectos, partir del Excel y del algoritmo acordado con el negocio, y luego redactar la spec, plan y casos de prueba basándose en esa base.

---

## 2026-07-07 Feature 001: "Actualizar la memoria" sin ejecutar el código no corrige nada — solo mueve el error de lugar

**Qué Pasó:** La entrada de decisión del 2026-07-04 ("Adoptar algoritmo v4 como referencia canónica") marcó T003 como completado, pero `test-cases.md` seguía citando dos ciclos que no existen en `parameters.json` ("SEMIANUAL ENERO, SM" y "ANUAL MARZO, UNI") y 4 de los 12 valores esperados no correspondían al algoritmo real. El error no se detectó hasta que se ejecutó `calcular_traslado()` directamente contra los datos reales.

**Causa Raíz:** Los valores esperados de `test-cases.md` se escribieron/editaron a mano (probablemente copiando y ajustando números del documento anterior) en vez de generarse ejecutando el código. Un checkbox se marcó `[x]` como acto de fe, no como verificación.

**Qué Aprendimos:**
- "Alinear la spec con el algoritmo" solo cuenta como hecho si cada valor esperado se generó ejecutando el código contra los datos reales — no si "suena razonable" o seguía el patrón del caso anterior.
- Un nombre de ciclo en un test case es una afirmación verificable (`buscar_ciclo()` en `traslados.py` lo confirma o lo rechaza); debe verificarse contra `parameters.json`, no asumirse.
- Marcar una tarea `[x]` sin correr `pytest` (o el script equivalente) después es peor que dejarla `[ ]`: crea falsa confianza en quien lee `tasks.md`.

**Regla de Prevención:**
- Ningún valor numérico en `spec.md` o `test-cases.md` se escribe a mano. Se genera con un script que llama a `calcular_traslado()` (o el módulo equivalente) y se copia el resultado literal.
- Antes de marcar `[x]` una tarea de alineación de documentos con código, ejecutar la suite de tests real y confirmar que pasa — no basta con "revisar visualmente".

---

## 2026-07-07 Feature 001: Un test con datos reales puede pasar sin probar nada — verificar con mutation testing

**Qué Pasó:** Al implementar FR-011 (clamp de `semana_actual` en CONTADO), se escribió un test (CB-10) usando un ciclo real de `parameters.json` en la fecha límite del ciclo, verificando `semana_actual <= semanas_totales`. El agente Review corrió el mismo escenario quitando el clamp del código (mutation testing) y el test **siguió pasando** — porque ningún ciclo real de `parameters.json` genera un `indice_semana_actual` que realmente exceda `semanas_totales`. El test daba una falsa sensación de cobertura.

**Causa Raíz:** Se asumió que "probar con datos reales" es automáticamente más riguroso que probar con datos sintéticos. Pero un caso borde de código (un `if`/clamp que protege contra un valor fuera de rango) solo se prueba de verdad si el escenario elegido realmente fuerza ese valor fuera de rango — y los datos de negocio reales no siempre generan esos escenarios (de hecho, casi nunca: si el negocio los generara, probablemente ya habría un bug reportado).

**Qué Aprendimos:**
- Una aserción `<=`/`>=` que es trivialmente cierta en el escenario de prueba no es una prueba — es una tautología con apariencia de test.
- Ya habíamos aprendido esto para CB-8 (rama del código inalcanzable con datos reales) pero no se aplicó el mismo razonamiento a CB-10 en el momento de escribirlo — la lección no se generalizó automáticamente de un caso al otro.
- Mutation testing (cambiar deliberadamente el código para ver si el test lo detecta) es la forma más directa de responder "¿este test realmente prueba algo?".

**Regla de Prevención:**
- Para cualquier test de un caso borde defensivo (clamp, guard clause, validación de rango), verificar explícitamente: "si borro esta línea de protección, ¿el test falla?". Si la respuesta no es obviamente sí, agregar un caso con datos sintéticos que sí fuerce el escenario — documentado como sintético (no fabricar un ciclo/entidad falsa en los datos de negocio).
- Cuando un agente Review (u otra revisión independiente) señale este tipo de hallazgo, no basta con "estar de acuerdo" — hay que reproducir el mutation test uno mismo antes de dar el hallazgo por resuelto.