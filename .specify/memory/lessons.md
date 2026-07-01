---
# Wave 23 §23.A.9/§23.A.10 — memory frontmatter for time-decay ranking
last_referenced_at: "2026-04-11T16:24:38.145323+00:00"
reference_count: 0
---
# Lessons Learned

> **Project-wide** record of what worked and what didn't.
> Agents append entries after corrections, stuck detection, or failed gates.
> Reviewed at the start of each new feature.

---

## How to Use

After a correction, failed gate, or stuck detection, append:

```
## [YYYY-MM-DD] Feature NNN: [Lesson Title]

**What Happened:** [Brief description of the issue]

**Root Cause:** [Why it happened]

**What We Learned:**
- [Lesson 1]
- [Lesson 2]

**Prevention Rule:**
- [How to avoid this in the future]
```

---

## Lessons

<!-- Append new lessons below this line -->

## 2026-07-01 Feature 001: Mantener la memoria sincronizada antes de seguir con la implementación

**What Happened:** Se avanzó con la implementación de la aplicación antes de registrar en memoria la arquitectura y los acuerdos tomados.

**Root Cause:** Los archivos de especificación estaban incompletos en algunas decisiones de implementación y la memoria seguía vacía en varias secciones.

**What We Learned:**
- Es mejor documentar la decisión de arquitectura y alcance antes de construir sobre ella.
- La memoria debe reflejar tanto los requerimientos como la solución elegida para evitar ambigüedades.

**Prevention Rule:**
- Actualizar decisions.md, session-state.md y el índice de memoria antes de continuar con cambios de implementación.
