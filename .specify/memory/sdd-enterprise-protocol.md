---
name: sdd-enterprise-protocol
description: Reglas obligatorias de verificación para que cualquier sesión (IA u humano) que continúe este proyecto use SDD Enterprise de verdad, no solo de nombre.
---

# Protocolo de Verificación SDD Enterprise (obligatorio, sin excepción)

> Si estás leyendo esto porque vas a continuar este proyecto — en una sesión nueva de Claude, en opencode, o cualquier otra herramienta — **léelo completo antes de tocar código o documentación.** `AGENTS.md` te manda a usar SDD Enterprise; este archivo es el "cómo", basado en errores reales que ya ocurrieron en este mismo repo.

## Por qué existe este documento

Una auditoría (2026-07-07) encontró que SDD Enterprise estaba **instalado pero no operando**:

- `tasks.md` tenía tareas marcadas `[x]` que en la práctica seguían rotas (T003 decía "alineado con el algoritmo v4" y `test-cases.md` seguía citando ciclos que no existían en `parameters.json`).
- El frontmatter de `last_referenced_at`/`reference_count` de los archivos de memoria estaba congelado en una fecha **anterior al primer commit real del proyecto** — prueba de que los "scripts de gate automáticos" nunca corrieron.
- Los workflows de CI (`spec-gate-enforcement.yml`, etc.) filtran por rutas (`.specify/specs/**`) que **no existen** en este repo (acá todo vive en `.specify/memory/`) — estructuralmente no pueden dispararse.
- `zproyect/test/test_traslados.py` fallaba en tiempo de colección por una aserción con un valor obsoleto, sin que nadie lo hubiera notado.

Ninguna de estas fallas requería mala intención — bastó con no verificar antes de dar algo por hecho. Este documento existe para que no se repita.

## Reglas obligatorias

1. **Ningún checkbox `[x]`** en `tasks.md` o `session-state.md` se marca sin que la entrada correspondiente cite el comando exacto ejecutado y su resultado real (no "revisé y está bien" — el comando y su salida, aunque sea resumida).
2. **Ningún valor numérico** en `spec.md` o `test-cases.md` se escribe a mano. Se genera ejecutando el algoritmo real (`traslados.py` u otro módulo de negocio) contra los datos reales (`parameters.json`), y se copia el resultado literal.
3. **Ningún nombre de entidad** (ciclo académico, endpoint, ruta, archivo) se cita en documentación sin verificar primero que existe en el código o los datos reales — con `grep`/búsqueda, no de memoria ni copiando de una versión anterior del documento.
4. Antes de decir "sincronizado", "alineado" o "completado", **correr la suite de tests real** (`pytest`) y mostrar el resultado — no basta con "revisar visualmente" el código.
5. Si un gate de CI **no puede dispararse** (mismatch de rutas, archivo `.example`, etc.), documentarlo explícitamente como "gate inactivo" en `session-state.md`. Nunca asumir que "el archivo `.yml` existe" equivale a "el gate protege el repo".
6. Si el CLI real (`sdd`, bajo `.specify/cli/`) puede invocarse para una operación (status, gate, analyze), **preferirlo sobre editar archivos a mano** — y si falla o no aplica a la estructura de este repo, decirlo explícitamente en vez de omitirlo en silencio.

## Checklist de auto-verificación antes de cerrar cualquier tarea

- [ ] ¿Ejecuté código real para obtener este valor? (sí/no + comando usado)
- [ ] ¿Verifiqué que la entidad citada existe en los datos/código reales?
- [ ] ¿Corrí la suite de tests después del cambio, y confirmé que pasa?
- [ ] ¿El checkbox que voy a marcar `[x]` tiene evidencia (comando + resultado) junto a él?
- [ ] Si toqué `detalle`/salida de la API, ¿el texto explicativo y el monto se derivan de la MISMA función (no de dos cálculos separados que puedan desincronizarse)?

## Punto de partida confiable (estado real al 2026-07-07)

- Todos los archivos de `.specify/memory/*.md` están sincronizados y verificados contra `zproyect/app.py` / `zproyect/traslados.py` ejecutados — no contra el Excel original ni cálculos a mano. Ver `decisions.md` para el historial completo de qué se corrigió y por qué.
- `zproyect/test/test_traslados.py` corre limpio (`pytest -s`, sin fallos) — pero el archivo usa asserts a nivel de módulo, no `def test_*`, así que pytest reporta "0 items"/exit 5 aunque todo pase. Migrar a funciones `test_*` reales es una mejora pendiente, no un bloqueante.
- Tareas reales pendientes (ver `tasks.md`): **T004, T005** (separar `traslados.py` en `validation.py`/`calculator.py`), **T007, T008** (tests unitarios formales adicionales), **T009, T010** (validaciones en cascada explícitas + tests de error), **T012** (botón de copiado en la UI), **T016, T017** (ruff + cobertura ≥80%).
- El CLI real `sdd` (bajo `.specify/cli/`) es invocable: `PYTHONPATH=.specify/cli python -m sdd status` corre (confirmado 2026-07-07), pero reporta "No features found" porque esta feature nunca se registró con `sdd new`/`feature.lock.json`. Si se retoma el uso del CLI en vez de edición manual, ese es el primer paso real a dar — no asumir que ya está integrado.

## Qué NO hacer

- No fabricar evidencia de que un gate/CI corrió si no corrió.
- No marcar una tarea como completa "para que se vea usado" — eso es precisamente el problema que este documento existe para prevenir.
- No copiar valores de una versión anterior del documento asumiendo que siguen vigentes; el algoritmo puede haber cambiado (ver `lessons.md`, entrada 2026-07-04).
