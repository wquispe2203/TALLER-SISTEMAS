# plan.md

# Resumen Ejecutivo

Este plan describe la implementación conceptual de una Calculadora de Montos de Traslado Académico basada en las reglas definidas en spec.md y gobernada por los principios establecidos en constitution.md. La decisión técnica principal consiste en desacoplar la lógica de cálculo, las validaciones y la presentación de resultados, utilizando una fuente única de parámetros académicos derivada del Excel oficial de Gerencia. Esto permitirá adaptar cambios en ciclos, montos y fechas sin modificar las reglas de negocio. La solución prioriza mantenibilidad, trazabilidad y consistencia de resultados. Permanecen abiertas las definiciones relacionadas con futuras reglas académicas, frecuencia de actualización de parámetros y posibles ampliaciones del alcance.

---

# 1. Enfoque Técnico (Alto Nivel)

La solución se implementará mediante componentes independientes responsables de captura de datos, validaciones, cálculo y presentación de resultados.

La interfaz será una aplicación web sencilla con HTML, CSS y JavaScript vanilla servidos por Flask desde `templates/` y `static/`. El backend se desarrollará en Python 3.11+ con Flask y expondrá un endpoint HTTP `POST /api/traslados/calcular` (verificado en `zproyect/app.py`) que recibe JSON, valida en cascada, ejecuta el motor de cálculo y devuelve resultado, estado y desglose. Los parámetros académicos y financieros se cargarán desde `data/parameters.json`, generado a partir del Excel oficial aprobado por Gerencia. Antes de calcular, el sistema aplicará validaciones fail-fast. El motor determinará semanas restantes, saldo disponible y costo del ciclo destino usando `decimal.Decimal` para montos. Las pruebas unitarias usarán pytest con cobertura mínima del 80% sobre validación y cálculo; el estilo de código se validará con ruff (PEP8).

No se contempla almacenamiento histórico de cálculos en esta fase.

---

# 2. Stack y Estructura de Archivos

> **Estructura real (verificada 2026-07-07, ver `zproyect/`):** el código vive bajo `zproyect/`, no en la raíz del repo como se planificó originalmente. La separación `validation.py`/`calculator.py` **no se ha realizado**: toda la lógica de validación y cálculo sigue junta en `traslados.py` (435 líneas). Esto es la tarea T004/T005 de `tasks.md`, todavía pendiente — contradice ADR-1 (separación lógica/UI) parcialmente: la UI sí está separada, pero validación y cálculo no lo están entre sí.

```
TALLER-SISTEMAS/zproyect/
├── app.py                  # Rutas Flask (UI + API)
├── traslados.py            # Validaciones + motor de cálculo, JUNTOS (pendiente separar en validation.py/calculator.py)
├── data/parameters.json    # Parámetros oficiales
├── templates/index.html
├── static/css/styles.css
├── static/js/app.js
├── test/test_traslados.py  # nota: carpeta "test" (singular), no "tests/"
└── requirements.txt
```

Convención de rutas (mismo origen, sin CORS) — **verificada contra `app.py`**:

* `GET /` → página del formulario
* `GET /health` → healthcheck
* `GET /api/ciclos` → lista de ciclos disponibles en `parameters.json`
* `POST /api/traslados/calcular` → cálculo (antes documentado erróneamente como `/api/transfer-calculator`)
* Assets en `/static/...`
* `fetch` con rutas relativas desde el frontend

Dependencias (`requirements.txt`): Flask, pytest, pytest-cov, ruff.

---

# 3. Componentes / Archivos Afectados

### Módulo de Captura de Datos

Responsable de recibir la información de entrada del usuario y pasarla al siguiente paso.

* Fecha de traslado
* Ciclo origen (Nombre, Universidad, Modalidad Académica, Pago en)
* Ciclo destino (Nombre, Universidad, Modalidad Académica, Pago en)

---

### Módulo de Normalización y Parseo

Responsable de transformar los datos crudos recibidos en un formato estructurado, consistente y tipado antes de enviarlos a validación.

* Convertir fechas a formato estándar
* Normalizar nombres de modalidades
* Validar tipos numéricos de montos
* Construir un DTO / contrato de entrada
* Rechazar entradas imposibles de parsear

Este módulo asegura que la validación y el cálculo trabajen con datos limpios y predecibles.

---

### Módulo de Validaciones

Responsable de verificar en cascada y en orden de prioridad:

1. Existencia de ciclo origen y ciclo destino en parameters.json
2. Igualdad de modalidad de pago entre origen y destino
3. Fecha válida dentro del periodo académico de ambos ciclos
4. (Opcional) Integridad de los datos de entrada (tipos, formato de fecha)

El módulo debe aplicar validaciones "fail-fast" para detener el proceso tan pronto se encuentre una condición inválida.

---

### Motor de Cálculo de Traslados

Responsable de:

* Calcular semanas restantes (con ajuste por semanas de feriado)
* Calcular saldo disponible
* Calcular costo requerido del ciclo destino
* Aplicar reglas para modalidad al contado
* Aplicar reglas para modalidad en cuotas
* Determinar saldo a favor, traslado cubierto o monto pendiente
* Calcular semanas consumidas con ajuste de fecha por feriados

#### Reglas específicas para CONTADO

* Las semanas se anclan al **calendario global** (lunes-domingo).
* Si la fecha de traslado cae en **lunes o martes**, la semana actual NO se considera consumida.
* Si la fecha de traslado cae entre **miércoles y domingo**, la semana actual SÍ se considera consumida.
* Las semanas de feriado completas no se cuentan como consumidas.

#### Reglas específicas para CUOTAS

* Las semanas se anclan a la **fecha de inicio del periodo de la cuota**, no al lunes del calendario.
* El algoritmo calcula solo el **valor residual de la cuota vigente** (no suma todas las cuotas futuras).
* El periodo de una cuota va desde su fecha de inicio hasta la fecha de la siguiente cuota.
* Las semanas feriado dentro del periodo de la cuota no se consideran consumidas.

---

### Fuente de Parámetros Académicos (`data/parameters.json`)

Responsable de almacenar:

* Ciclos académicos
* Fechas académicas
* Semanas por ciclo
* Cuotas por ciclo
* Montos al contado
* Montos por cuota
* Modalidades disponibles

El contenido será generado a partir del Excel oficial aprobado por Gerencia.

---

### Módulo de Resultados

Responsable de presentar:

* Saldo a favor
* Traslado cubierto
* Monto pendiente
* Mensajes de validación
* Observaciones de negocio
* Operaciones del resultado
---

# 4. Decisiones de Arquitectura (Mini-ADR)

## ADR-1

### DECISIÓN

Separar la lógica de cálculo de la interfaz de usuario.

### POR QUÉ

Las reglas de negocio poseen mayor probabilidad de cambio que la forma de captura o visualización de datos. El desacoplamiento facilita pruebas, mantenimiento y evolución de la solución.

### ALTERNATIVA DESCARTADA

Implementar las reglas directamente dentro de la interfaz.

### MOTIVO DEL DESCARTE

Genera alto acoplamiento entre presentación y negocio, dificulta las pruebas unitarias y aumenta el costo de mantenimiento.

---

## ADR-2

### DECISIÓN

Centralizar todos los parámetros académicos y financieros en una única fuente de datos derivada del Excel oficial.

### POR QUÉ

Garantiza consistencia con la información aprobada por Gerencia y cumple el principio de Single Source of Truth (SSoT) definido en la Constitución. El Excel también define las fechas de feriados que afectan el conteo de semanas.

### ALTERNATIVA DESCARTADA

Mantener valores codificados manualmente dentro de la solución.

### MOTIVO DEL DESCARTE

Viola el principio de Single Source of Truth, incrementa el riesgo de inconsistencias y obliga a modificar la solución cada vez que Gerencia publique nuevas tarifas o ciclos.

---

## ADR-3

### DECISIÓN

Aplicar validaciones antes de ejecutar cualquier cálculo.

### POR QUÉ

Evita procesar información inválida y garantiza que únicamente se ejecuten cálculos sobre datos consistentes.

### ALTERNATIVA DESCARTADA

Realizar cálculos antes de validar.

### MOTIVO DEL DESCARTE

Puede generar resultados inconsistentes, incrementar la complejidad del flujo y dificultar la identificación de errores operativos.

---

## ADR-4

> Producido vía SDD Enterprise real (2026-07-07) por el agente **Architect** (`.github/agents/architect.agent.md`), resolviendo las preguntas abiertas que dejó el agente **Requirement Analyst** al formalizar FR-011 en `spec.md`.

### DECISIÓN

Exponer `fecha_inicio_periodo`, `fecha_fin_periodo` (string) y `semana_actual` (integer) como campos estructurados dentro de los diccionarios que ya retornan `generar_pasos_contado` y `generar_pasos_cuotas` (el bloque `detalle`), en vez de crear una ruta de cálculo paralela. Los tres campos se derivan leyendo variables que esas funciones **ya calculan** para construir la narrativa de `pasos` — no se introduce ninguna fórmula nueva.

**4.1 Base de `semana_actual`: 1-based.** El propio código ya narra "semana X" en base 1; el campo estructurado debe ser consistente con lo ya narrado, no con el índice interno 0-based (`idx_actual`) que es un detalle de implementación.

**4.2 Formato de fecha: `DD/MM/YYYY`.** Toda la app (narrativa de `pasos`, `parse_fecha`, `parameters.json`) ya usa ese formato; introducir ISO en un campo estructurado del mismo payload crearía dos formatos de fecha en una misma respuesta.

**4.3 CB-8/CB-9: `null` explícito, sin fallback inventado.** Art. 7 NEVER DO prohíbe asumir valores por defecto cuando faltan datos obligatorios. `fuera_de_ciclo` → los 3 campos `null`. `antes_primera_cuota` → `fecha_inicio_periodo: null` (no ha empezado ningún periodo), `fecha_fin_periodo` = vencimiento de la cuota 1 (ya se calcula y ya se narra), `semana_actual: 1` (consistente con `semanas_totales:1, semanas_restantes:1` que esa rama ya retorna). Los campos van `null` explícito, nunca se omiten — un contrato de forma estable evita que cada consumidor tenga que chequear existencia de la clave.

**4.4 Clamp de `semana_actual` en CONTADO: sí, agregar.** CUOTAS ya clampea `idx_actual` a `[0, semanas_totales-1]`; CONTADO no clampeaba `indice_semana_actual`, una asimetría no justificada para el mismo concepto de negocio. Se agrega `semana_actual = max(1, min(indice_semana_actual, semanas_totales))`.

**4.5 Nombres de campo: unificados, sin prefijo por modalidad.** `detalle.origen/destino` ya tiene campos (`semanas_totales`, etc.) cuyo significado depende de `pago_en` sin llevarlo en el nombre — mismo patrón se aplica a los 3 campos nuevos.

### ALTERNATIVA DESCARTADA

Base 0 para `semana_actual`; ISO para fechas; fallback a fechas del ciclo completo en CB-8/CB-9; sin clamp en CONTADO; nombres de campo prefijados por modalidad (`semana_actual_contado`/`semana_actual_cuotas`).

### MOTIVO DEL DESCARTE

Cada alternativa introducía una inconsistencia con una convención que el código YA establece en otro lugar de la misma respuesta (narrativa en base 1, fechas en `DD/MM/YYYY`, clamp ya presente en CUOTAS, campos sin prefijo de modalidad ya existentes) — mantenerlas habría creado dos convenciones distintas para el mismo concepto dentro de un solo payload JSON.

### Componentes / Archivos Afectados

| Componente (`zproyect/traslados.py`) | Cambio conceptual |
|---|---|
| `generar_pasos_contado` | `detalle` agrega `fecha_inicio_periodo`/`fecha_fin_periodo` (fechas del ciclo) y `semana_actual` (clampeado). No toca la fórmula del monto ni `pasos`. |
| `generar_pasos_cuotas` | `detalle` agrega los 3 campos según el `caso` de `_seleccionar_cuota_vigente` (`vigente`/`antes_primera_cuota`/`fuera_de_ciclo`). |
| `_detalle_semanas_periodo`, `_seleccionar_cuota_vigente` | Sin cambios — ya retornan lo necesario. |
| *(nuevo)* `_fmt_fecha_opt(f)` | Helper de una línea para no repetir `strftime(...) if f else None` (Synthesis · Simplificación). |
| `calcular_traslado` | Sin cambios — reenvía `det_origen`/`det_destino` tal cual. |

### Synthesis Assessment

**Generalización:** se evaluó un helper único para "semana_actual + periodo" en ambas modalidades; se descarta porque CONTADO y CUOTAS anclan las semanas a reglas de negocio distintas (calendario global vs. inicio del periodo de cuota) ya documentadas como tales en el código — solo se generaliza el *nombre* de los campos de salida, no la fórmula.
**Build vs. Adopt:** no aplica — no se necesita librería externa; es una ampliación del contrato de salida sobre cálculo ya construido.
**Simplificación:** cambio mínimo (agregar 3 claves a dicts existentes); único riesgo es repetir el formateo de fecha, mitigado con el helper `_fmt_fecha_opt`.

---

# 5. Riesgos y Dependencias

## Riesgos

### R-1

Cambios en las reglas de negocio definidos por Gerencia.

**Mitigación:** Mantener las reglas de cálculo centralizadas y documentadas para facilitar modificaciones futuras.

### R-2

Errores o inconsistencias en el Excel oficial.

**Mitigación:** Validar la estructura e integridad de `parameters.json` antes de permitir cálculos.

### R-3

Interpretaciones ambiguas de fechas académicas o semanas restantes.

**Mitigación:** Documentar explícitamente las reglas de conteo de semanas y validarlas con el área usuaria.

### R-4

Cambio en el calendario de feriados institucionales.

**Mitigación:** Los feriados están definidos en el código como `FERIADOS_DIAS = [(7, 28), (7, 29), (12, 25)]`. Actualizar estas constantes cuando cambie la política institucional.

---

## Dependencias

### D-1

Disponibilidad del Excel oficial actualizado.

### D-2

Disponibilidad de las fechas académicas necesarias para calcular semanas restantes.

### D-3

Definición clara de las semanas de feriados institucionales.

---

# 6. Trazabilidad

## US-1 (Obtener resultado económico del traslado)

Implementación:

* Módulo de Captura de Datos
* Motor de Cálculo de Traslados
* Fuente de Parámetros Académicos
* Módulo de Resultados

---

## US-2 (Validar reglas de negocio antes del cálculo)

Implementación:

* Módulo de Validaciones
* Fuente de Parámetros Académicos
* Módulo de Resultados

---

## US-3 (Mostrar desglose de operaciones y resumen)

Implementación:

* Motor de Cálculo de Traslados (generar_pasos_contado / generar_pasos_cuotas)
* Módulo de Resultados (detalle con pasos narrativos)
* Interfaz de Usuario (botón de copiado, T012)

---

## US-4 (Interfaz de usuario premium)

Implementación:

* Interfaz de Usuario (HTML semántico, CSS glassmorphism, JS)
* Módulo de Resultados (conexión del formulario con la API)

---

```
```
