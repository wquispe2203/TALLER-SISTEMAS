# Posibles Preguntas sobre SDD y el Proyecto

---

## 🔵 Sobre qué es SDD

**¿Qué es SDD?**
> SDD (Spec-Driven Development) es un framework donde la especificación va antes que el código. Primero defines qué vas a construir y por qué, con gates que validan que cada fase esté completa antes de avanzar. Todo tiene trazabilidad: cada línea de código se puede rastrear hasta un requisito.

**¿Cuál es la diferencia entre SDD y desarrollo normal?**
> En desarrollo normal se escribe código y luego se documenta. En SDD la especificación va primero y nunca se puede saltar una fase. Los gates son obligatorios: si no pasas el Gate 1, no puedes diseñar; si no pasas el Gate 3, no puedes implementar.

**¿Qué es la Constitución del proyecto?**
> Es el documento `constitution.md` que define las reglas que ningún agente puede violar: el stack tecnológico (Python 3.11+, Flask), los estándares de calidad (cobertura ≥80%, PEP8), los principios de arquitectura (separación de capas) y lo que NUNCA se puede hacer (duplicar fórmulas, mezclar lógica con UI, modificar datos sin validación).

---

## 🟡 Sobre el Flujo y los Gates

**¿Cuántos gates tiene el proyecto y qué valida cada uno?**
> Tiene 4 gates:
> - **Gate 1**: Spec completa — User Stories, Acceptance Criteria, sin ambigüedades pendientes
> - **Gate 2**: Diseño completo — arquitectura, plan técnico, stack definido
> - **Gate 3**: Listo para implementar — test cases y tasks generados y ordenados
> - **Gate 4**: Listo para ship — todos los tests pasando, review aprobado

**¿Qué pasa si un gate falla?**
> No puedes avanzar a la siguiente fase. En este proyecto, el Gate 2 falló una vez y el Gate 4 falló dos veces antes de quedar en PASS. Los fallos están registrados en `metrics-log.md`.

**¿Por qué el Gate 4 falló dos veces?**
> El Gate 4 valida que todos los artefactos sean consistentes entre sí (spec, plan, tasks, tests, código). Las primeras corridas fallaron porque había artefactos desincronizados o incompletos. Después de corregirlos, pasó limpio.

**¿Se pueden saltear fases en SDD?**
> No. El `AGENTS.md` del proyecto dice explícitamente: *"Never skip a phase. Never generate implementation before specification and planning."*

---

## 🟢 Sobre los Agentes

**¿Qué es un agente en SDD?**
> Es un rol especializado de IA definido en `.github/agents/`. Cada agente tiene instrucciones específicas, herramientas permitidas, y handoffs hacia otros agentes. No son "chatbots genéricos" — cada uno está restringido a su fase y tiene reglas de "Always Do / Never Do".

**¿Cuántos agentes tiene el proyecto?**
> 16 agentes disponibles: Requirement Analyst, Architect, Clarification, Constitution, Software Engineer, Review, Security Reviewer, Test Engineer, Test Explorer, Analysis, Gherkin Analyst, Refactoring, Brainstorming, API Champion, Messaging Champion, Tech Context Maintainer.

**¿Qué agentes se usaron realmente?**
> El flujo real que se ejecutó fue: **Requirement Analyst → Architect → Software Engineer → Review**. Se invocaron como subagentes reales con sus prompts de `.github/agents/`, no como edición manual de archivos.

**¿Qué hace el agente Requirement Analyst?**
> Transforma necesidades de negocio en requerimientos estructurados. Opera en 3 modos: Vision (captura contexto del PO), Detailed (elabora la spec con el FA), Teaching (mentoría). En este proyecto produjo FR-011 con sus Acceptance Criteria en formato Given-When-Then y dejó 6 preguntas abiertas explícitas en vez de asumirlas.

**¿Qué hace el agente Architect?**
> Convierte specs clarificadas en diseño técnico. Produce `plan.md` con ADRs (Architecture Decision Records), diagramas, y decisiones de diseño justificadas. En este proyecto resolvió las 6 preguntas del Requirement Analyst como ADR-4.

**¿Qué hace el agente Review?**
> Es el gate final de calidad. Corre en dos pasadas: Pass 1 verifica que cada Acceptance Criteria tiene evidencia en tests; Pass 2 verifica calidad de código, seguridad y documentación. Produce el `ship-checklist.md`. En este proyecto encontró un bug real de cobertura (test CB-10 que pasaba aunque borraras el clamp) usando mutation testing.

---

## 🔴 Sobre el Proyecto Específico

**¿Qué problema resuelve el proyecto?**
> Automatiza el cálculo de montos de traslado académico, que antes se hacía manualmente con Excel en 10-20 minutos por solicitud con ~5-10% de error humano. Ahora responde en menos de 1 segundo con 0% de error (cálculo determinista).

**¿Cuál es la fuente de datos del proyecto?**
> `data/parameters.json`, generado a partir del Excel oficial aprobado por Gerencia. Es la única fuente de verdad — ningún monto se inventa ni se escribe a mano.

**¿Los montos de los test cases los inventó la IA?**
> No, no debería haberlos inventado — pero al inicio sí lo hizo. El problema fue que la IA escribía los valores a mano sin ejecutar el código. Cuando se detectó (auditoría 2026-07-07), se estableció la regla obligatoria: *ningún valor numérico en test-cases.md se escribe sin ejecutar `calcular_traslado()` contra `parameters.json` real*.

**¿Cuántos test cases tiene el proyecto y cuántos pasan?**
> 15 test cases definidos en `test-cases.md`. En `test_traslados.py` hay 61 assertions (`check()`), todas pasando.

**¿Qué es el `ship-checklist.md`?**
> Es el output del agente Review. Es el "acta de aprobación" del proyecto. En la sección 11 dice `✅ READY TO SHIP` con fecha 2026-07-09.

**¿En qué Gate está actualmente el proyecto?**
> Gate 4 — el último. El checkpoint registra `"gate": 4`, lo que significa que superó todos los gates.

---

## 🟣 Sobre Dificultades y Lecciones

**¿Qué dificultades tuvieron?**
> Tres principales:
> 1. **Fecha del 16**: los ciclos inician el 16/03, no el 1ro de mes — afecta el conteo de semanas en todos los casos de prueba
> 2. **Ambigüedad cuotas/ciclos**: si prorratar el ciclo completo o solo la cuota vigente. El algoritmo v4 prorratea solo la cuota vigente a la fecha de traslado
> 3. **La IA marcaba tests como validados sin ejecutar el código**: se detectó tarde y generó inconsistencias que requirieron una auditoría completa

**¿Qué es mutation testing y por qué se usó?**
> Es una técnica donde deliberadamente "rompes" el código (borras una línea de protección) para verificar si el test lo detecta. Se usó porque el agente Review descubrió que el test CB-10 pasaba aunque se borrara el clamp — el test daba falsa confianza. Se agregó un caso sintético que sí fuerza el escenario y ahora el test sí falla cuando el clamp no está.

**¿Qué pasó cuando la IA marcaba tests como aprobados sin verificar?**
> Había ciclos referenciados en los test cases que no existían en `parameters.json` ("SEMIANUAL ENERO, SM"). TC-3 esperaba S/ 4080.00 pero el valor real era S/ 382.50. Se detectó porque al ejecutar el código los valores no coincidían. La lección quedó en `lessons.md` y se convirtió en regla en `sdd-enterprise-protocol.md`.

**¿Qué es el SDD Enterprise Protocol?**
> Es un documento (`sdd-enterprise-protocol.md`) con reglas obligatorias que surgieron de fallas reales en este proyecto. Por ejemplo: ningún checkbox se marca `[x]` sin citar el comando exacto ejecutado y su resultado; ningún valor numérico se escribe a mano. No es opcional — el `AGENTS.md` obliga a leerlo antes de hacer cualquier cosa.

---

## ⚪ Preguntas técnicas del proyecto

**¿Cuál es el stack tecnológico?**
> Python 3.11+ con Flask como backend, HTML/CSS/JS vanilla como frontend, `data/parameters.json` como fuente de datos, pytest para tests, ruff para linting.

**¿Cuáles son los endpoints de la API?**
> `GET /` (UI), `GET /health` (health check), `GET /api/ciclos` (lista ciclos), `POST /api/traslados/calcular` (cálculo).

**¿Cómo funciona el cálculo de CONTADO?**
> `saldo = (cash_price / semanas_efectivas) × semanas_restantes`
> Donde `semanas_efectivas = duration_weeks` (los feriados se excluyen completamente, no se cobran al alumno).
> `semanas_consumidas`: lunes y martes no cuentan como semana consumida; miércoles a domingo sí.

**¿Cómo funciona el cálculo de CUOTAS?**
> Se identifica la cuota vigente a la fecha de traslado, y se prorratea **solo esa cuota**:
> `valor = monto_cuota × (semanas_restantes_del_periodo / semanas_totales_del_periodo)`
> No se suman todas las cuotas futuras.

**¿Qué tareas quedaron pendientes como backlog?**
> T007/T008 (unit tests formales adicionales), T009/T010 (validaciones en cascada explícitas + tests de error), T012 (botón copy-to-clipboard), T016/T017 (ruff lint + cobertura ≥80%).
