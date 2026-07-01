---
# Wave 23 §23.A.9/§23.A.10 — memory frontmatter for time-decay ranking
last_referenced_at: "2026-04-11T13:18:21.979015+00:00"
reference_count: 0
---
# Caché de Investigación

> Caché **a nivel de proyecto** de los hallazgos de investigaciones externas.
> Los agentes añaden entradas tras completar una investigación (evaluación tecnológica, análisis de patrones, comparación de librerías, etc.).
> Las entradas expiran después de 7 días por defecto — investigue de nuevo si están obsoletas.

---

## Cómo Usar

Después de investigar un tema, añade:

```
## [Nombre del Tema]

**Investigado:** [AAAA-MM-DD]
**Funcionalidad:** [NNN o "a nivel de proyecto"]
**Relevancia:** [ALTA / MEDIA / BAJA]
**Expira:** [+7 días desde la fecha de investigación]

### Hallazgos Clave
- [Hallazgo 1 con referencia de fuente]
- [Hallazgo 2 con referencia de fuente]

### Patrones Encontrados
- [Patrón con contexto]

### Restricciones Descubiertas
- [Restricción de la constitución o fuente externa]

### Preguntas Abiertas
- [Pregunta sin responder]
```

---

## Guía de Frescura

| Relevancia | Edad | Acción |
|------------|------|--------|
| ALTA | < 3 días | Usar directamente |
| MEDIA | 3-7 días | Usar con precaución, verificar si es crítica |
| BAJA | > 7 días | Investigar de nuevo antes de usar |

---

## Caché

<!-- Añadir nuevas entradas de investigación debajo de esta línea -->
