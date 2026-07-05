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