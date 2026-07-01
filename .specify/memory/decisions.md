---
# Wave 23 §23.A.9/§23.A.10 — memory frontmatter for time-decay ranking
last_referenced_at: "2026-04-11T16:24:38.141489+00:00"
reference_count: 0
---
# Decisions Log

> **Project-wide** architectural and design decisions with rationale.
> Agents append entries when significant decisions are made during Planning or Implementation.
> Human review recommended after each feature.

---

## How to Use

After making a significant decision, append a new entry:

```
## [YYYY-MM-DD] Feature NNN: [Decision Title]

**Context:** [Why this decision was needed]

**Options Considered:**
1. [Option A] — [pros/cons]
2. [Option B] — [pros/cons]

**Chosen:** Option [X]

**Reasoning:**
- [Key reason 1]
- [Key reason 2]

**Trade-offs Accepted:**
- [Trade-off 1]

**Confidence:** [High/Medium/Low]
```

---

## Decisions

<!-- Append new decisions below this line -->

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
