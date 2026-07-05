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