# spec.md

# Resumen Ejecutivo

Se propone implementar una Calculadora de Montos de Traslado Académico para automatizar el cálculo actualmente realizado de forma manual por el área de TI utilizando un Excel oficial proporcionado por Gerencia. La solución permitirá determinar automáticamente si una solicitud de traslado genera saldo a favor, traslado cubierto o monto pendiente de pago, aplicando las reglas institucionales vigentes según la condición de pago (contado o cuotas) y la modalidad académica (presencial o virtual).

---

# 1. Contexto de Negocio

## Problema que resuelve

Actualmente el cálculo de montos de traslado académico se realiza manualmente utilizando fórmulas contenidas en un Excel oficial. Este proceso requiere entre 10 y 20 minutos por solicitud y depende del conocimiento individual del analista, aumentando el riesgo de errores y diferencias de criterio.

## Por qué ahora / a quién impacta

Durante campañas académicas el volumen de solicitudes de traslado puede duplicarse o triplicarse, incrementando la carga operativa del área de TI.

La solución impacta directamente al equipo de Soporte TI, responsable de calcular y comunicar los resultados económicos de los traslados académicos.

---

# 2. User Stories y Criterios de Aceptación

## US-1 (P1)

Como analista de soporte,

quiero ingresar los datos necesarios para un traslado académico,

para obtener automáticamente el resultado económico del traslado.

### AC-1.1 (Saldo a favor)

Dado un traslado válido (TC-1 del algoritmo):
* Fecha de traslado: 15/05/2026
* Ciclo origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
* Ciclo destino: ANUAL MARZO, SM, VIRTUAL, CONTADO (cash_price: S/ 3240, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:
* Resultado: S/ 1046.25 de saldo a favor
* Estado: "Saldo a favor"

> **Nota (2026-07-09):** Corregido de S/ 1060.72 a S/ 1046.25 por la exclusión de feriados. Anteriormente el denominador era `duration_weeks + feriados` (42), ahora es solo `duration_weeks` (40). Ver `decisions.md` entrada 2026-07-09.

### AC-1.2 (Traslado cubierto)

Dado un traslado válido (TC-3 del algoritmo):
* Fecha de traslado: 20/04/2026
* Ciclo origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)
* Ciclo destino: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:
* Resultado: S/ 0
* Estado: "Traslado cubierto exactamente"

### AC-1.3 (Monto pendiente)

Dado un traslado válido (TC-2 del algoritmo):
* Fecha de traslado: 15/05/2026
* Ciclo origen: ANUAL MARZO, SM, VIRTUAL, CONTADO (cash_price: S/ 3240, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
* Ciclo destino: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:
* Resultado: S/ 1046.25 pendiente de pago
* Estado: "Monto pendiente"

> **Nota (2026-07-09):** Corregido de S/ 1060.72 a S/ 1046.25 — reverso simétrico de AC-1.3, misma corrección por exclusión de feriados.

---

## US-2 (P1)

Como analista de soporte,

quiero que el sistema valide las reglas de negocio antes de ejecutar el cálculo,

para evitar resultados incorrectos.

### AC-2.0 (Validación en cascada)

Dado una solicitud de traslado,

Cuando el usuario inicia el cálculo,

Entonces el sistema debe validar en el siguiente orden y detenerse en el primer error encontrado:

1. Existencia de ciclo origen y ciclo destino en parameters.json
2. Igualdad de modalidad de pago entre origen y destino
3. Fecha de traslado dentro del periodo académico de ambos ciclos
4. (Opcional) Integridad de los datos de entrada

### AC-2.1 (Fecha inválida)

Dado una fecha que no pertenece al periodo académico válido del ciclo origen o destino,

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"La fecha de traslado está fuera del rango del ciclo [ORIGEN/DESTINO]."

### AC-2.2 (Modalidad de pago diferente)

Dado que pago_en_origen != pago_en_destino,

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"No se permiten traslados entre modalidades de pago diferentes. Si requiere este tipo de traslado, debe procesarlo manualmente."

### AC-2.3 (Ciclo no encontrado)

Dado que el ciclo origen o destino no existe en parameters.json,

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"Ciclo [origen/destino] no encontrado en la base de datos"


## US-3 (P2)

Como analista de soporte,

quiero que el sistema muestre el desglose de las operaciones realizadas para obtener el resultado,

para poder analizar y validar cómo se llegó al monto final.

### AC-3.1 (Mostrar desglose completo)

Dado un traslado válido,

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra además del resultado final:

* Semanas totales de clase del ciclo origen (feriados ya excluidos)
* Semanas transcurridas a la fecha de traslado (ajustado por feriados)
* Semanas restantes
* Fórmula y resultado del saldo disponible (con valor residual de contado/cuotas)
* Fórmula y resultado del costo del ciclo destino
* Operación final y resultado

> **Historial (2026-07-07):** se detectó que para CUOTAS, `detalle.origen/destino` se calculaba con `calcular_semanas_consumidas` (semanas del **ciclo completo**) mientras el monto real (`saldo_origen`/`costo_destino`) se calculaba con `_prorratear_cuota` (semanas del **periodo de la cuota vigente**) — un número totalmente distinto, que hacía el desglose engañoso. Se corrigió junto con FR-010 (ver abajo): `detalle` ahora usa, para CUOTAS, las semanas del periodo de la cuota vigente. Task: T018/T019 en `tasks.md`.

### FR-010 Desglose expresado como cálculo manual (no como una resta directa)

El sistema MUST presentar el desglose de FR-006 como una secuencia de pasos redactados en lenguaje natural que reproduzcan el razonamiento que seguiría un analista calculando a mano — no únicamente los números finales de una resta.

* **Para CONTADO**, la secuencia MUST incluir explícitamente: la fecha de inicio del ciclo y su día de semana; en qué semana (por índice y rango de fechas, ancladas al lunes del calendario) cae la fecha de traslado; si esa semana se considera consumida o no según la regla lunes/martes (no consumida) vs miércoles-domingo (consumida); cuántas semanas de feriado caen dentro del ciclo completo (solo informativo, no afectan el cálculo); y la fórmula con los valores sustituidos: `valor por semana = cash_price ÷ duration_weeks` y `saldo = valor por semana × semanas restantes`. Los feriados no se cobran al alumno: no se incluyen ni en las semanas de clase ni en las semanas restantes.
* **Para CUOTAS**, la secuencia MUST incluir: qué cuota está vigente a la fecha de traslado y su monto; el periodo de esa cuota (fecha de inicio y fin, ancladas a la fecha de inicio de la propia cuota, no al calendario global); cuántos días y semanas dura ese periodo; cuántos días y semanas han transcurrido desde el inicio del periodo hasta la fecha de traslado; si alguna semana del periodo es una semana de feriado (y por tanto no cuenta como consumida); y la fórmula con los valores sustituidos: `valor residual = monto de la cuota × semanas restantes ÷ semanas totales del periodo`.
* Implementación de referencia: `traslados.py::generar_pasos_contado` / `generar_pasos_cuotas`, expuestas en `detalle.origen.pasos` / `detalle.destino.pasos` de la respuesta de `calcular_traslado`.

### AC-3.4 (Desglose CUOTAS estilo cálculo manual)

Dado un traslado CUOTAS válido (fecha 25/03/2026, ANUAL MARZO SM Presencial→Virtual — ver `test-cases.md` TC-14),

Cuando el sistema genera el desglose,

Entonces debe mostrar, en este orden: cuota vigente (cuota 1, S/ 510.00), periodo de la cuota (16/03/2026–11/04/2026, 26 días, 4 semanas), días/semanas transcurridos desde el inicio del periodo (9 días → 1 semana consumida), semanas feriado dentro del periodo (0), semanas restantes (3), y la fórmula sustituida (510.00 × 3 ÷ 4 = 382.50).

### AC-3.5 (Desglose CONTADO estilo cálculo manual)

Dado un traslado CONTADO válido (fecha 15/05/2026, SEMIANUAL MARZO SM Presencial→Virtual — ver `test-cases.md` TC-15),

Cuando el sistema genera el desglose,

Entonces debe mostrar, en este orden: fecha de inicio del ciclo y su día de semana (16/03/2026, lunes), en qué semana (por índice y rango de fechas) cae la fecha de traslado (semana 9: 11/05/2026–17/05/2026), si esa semana cuenta como consumida (15/05 es viernes → sí), semanas consumidas (9), semanas feriado del ciclo completo (1), semanas de clase (28, feriados ya excluidos), semanas restantes (28 − 9 = 19), y la fórmula sustituida (3213.00 ÷ 28 × 19 = 2180.25).

> **Nota (2026-07-09):** Corregido: antes se sumaban los feriados al denominador (28+1=29, 3213÷29×20=2215.86). Ahora los feriados se excluyen completamente: solo 28 semanas de clase, 19 restantes.

### AC-3.2 (Ajuste por feriados)

Dado un cálculo de traslado donde la fecha cae en una semana de feriado (Fiestas Patrias o Navidad),

Cuando el sistema genera el desglose de las operaciones,

Entonces el sistema debe incluir explícitamente en el detalle:

* Las semanas de feriado que se cancelan y se saltan en el calendario académico.
* La fecha ajustada usada para el cálculo de semanas consumidas.
* La aclaración de que los feriados no se cobran al alumno (no se incluyen ni en las semanas de clase ni en las semanas restantes).

### AC-3.3 (Exportación o copia rápida para atención de tickets)

Dado que el sistema ha generado el desglose de operaciones con éxito,

Cuando el analista necesita enviar la justificación del cálculo al estudiante,

Entonces la interfaz debe proporcionar un botón de "Copiar resumen" que capture todo el desglose en formato de texto plano estructurado, listo para ser pegado en un ticket de soporte.

---

## Extensión a US-3 — Campos estructurados de fecha y semana actual en el desglose

> Producida vía SDD Enterprise real (2026-07-07): elaborada por el agente **Requirement Analyst** (`.github/agents/requirement-analyst.agent.md`, Detailed Mode) a partir de un hallazgo de soporte sobre FR-010/AC-3.4/AC-3.5 — el analista necesita tabular en la UI las fechas de inicio/fin del periodo relevante y la semana en la que cae la fecha de traslado, hoy solo disponibles embebidas en el texto narrativo de `pasos`. Las decisiones de diseño quedaron resueltas por el agente **Architect** en `plan.md` → ADR-4 (ver también `decisions.md`, entrada 2026-07-07).

### FR-011 Campos estructurados de periodo y semana actual en `detalle.origen`/`detalle.destino`

El sistema MUST exponer, como campos independientes dentro de `detalle.origen` y `detalle.destino` de la respuesta de `POST /api/traslados/calcular` (no solo embebidos en el texto narrativo de `pasos`):

* `fecha_inicio_periodo` (string `DD/MM/YYYY` o `null` — ver ADR-4 §4.2/4.3)
* `fecha_fin_periodo` (string `DD/MM/YYYY` o `null`)
* `semana_actual` (integer, **1-based** — ADR-4 §4.1, o `null`)

Significado según modalidad (reutilizando exactamente los valores internos que ya usa la narrativa de FR-010 — Art. 4.4 constitución, prohibido duplicar fórmulas):

* **CONTADO**: `fecha_inicio_periodo`/`fecha_fin_periodo` = fechas del CICLO COMPLETO. `semana_actual` = `indice_semana_actual` (1-based), **con clamp a `[1, semanas_totales]`** (ADR-4 §4.4 — antes CONTADO no clampeaba, a diferencia de CUOTAS).
* **CUOTAS**: `fecha_inicio_periodo`/`fecha_fin_periodo` = fechas del PERIODO DE LA CUOTA VIGENTE (no del ciclo completo). `semana_actual` = `idx_actual + 1` de `_detalle_semanas_periodo`.
* **CUOTAS, caso `antes_primera_cuota`** (fecha anterior al vencimiento de la cuota 1): `fecha_inicio_periodo = null`, `fecha_fin_periodo` = fecha de vencimiento de la cuota 1, `semana_actual = 1` (ADR-4 §4.3).
* **CUOTAS, caso `fuera_de_ciclo`** (fecha ≥ fin del ciclo, nada pendiente): los tres campos van `null` explícito (ADR-4 §4.3) — nunca se omiten ni se rellenan con un fallback (Art. 7 NEVER DO: "asumir valores por defecto cuando falten datos obligatorios").

No modifica `semanas_totales`, `semanas_consumidas` ni `semanas_restantes` (ya existentes desde FR-010) — solo agrega estos tres campos.

### AC-3.6 (Campos de periodo y semana actual — CONTADO)

Dado un traslado CONTADO válido (fecha 15/05/2026, SEMIANUAL MARZO SM Presencial→Virtual — ver `test-cases.md` TC-15),

Cuando el sistema genera el desglose,

Entonces `detalle.origen` debe incluir `fecha_inicio_periodo: "16/03/2026"`, `fecha_fin_periodo: "02/10/2026"`, `semana_actual: 9` — coincidentes exactamente con lo ya narrado en `pasos`.

### AC-3.7 (Campos de periodo y semana actual — CUOTAS)

Dado un traslado CUOTAS válido (fecha 25/03/2026, ANUAL MARZO SM Presencial→Virtual — ver `test-cases.md` TC-14),

Cuando el sistema genera el desglose,

Entonces `detalle.origen` debe incluir `fecha_inicio_periodo: "16/03/2026"` (inicio del periodo de la cuota 1 vigente, NO el inicio del ciclo), `fecha_fin_periodo: "11/04/2026"`, `semana_actual: 2`.

### AC-3.8 (Simetría origen/destino)

Dado cualquier traslado válido (CONTADO o CUOTAS), `detalle.destino` debe exponer los mismos tres campos, calculados con la misma regla que `detalle.origen`, usando las fechas/cuota vigente del CICLO DESTINO.

## US-4 (P2)

Como analista de soporte,

quiero visualizar el resultado de la simulación de forma clara y estructurada,

para poder comunicar el resultado exacto (saldo a favor, monto a cancelar y diferencial) al estudiante de manera comprensible.

### AC-4.1 (Mostrar saldos iniciales)

Dado que se ha ejecutado el cálculo del traslado,

Cuando el sistema muestra la sección "Resultado de la Simulación",

Entonces debe mostrar claramente:

* "Saldo a favor:" con el monto calculado del ciclo origen y su modalidad.
* "Monto a cancelar:" con el costo total del ciclo destino y su modalidad.

### AC-4.2 (Mensaje conclusivo de saldo insuficiente/faltante)

Dado que el saldo a favor es menor al costo del ciclo destino,

Cuando el sistema presenta el resultado,

Entonces debe mostrar una alerta destacada en rojo indicando el monto faltante exacto. Ejemplo: "El saldo a favor del ciclo anterior no cubre el costo del nuevo ciclo. Faltan: S/ 1023.00".


# 3. Requisitos Funcionales

### FR-001 Datos de entrada requeridos

El sistema MUST solicitar los siguientes campos obligatorios:

* Fecha de traslado (formato DD/MM/YYYY, D/M/YYYY, YYYY-MM-DD, o "En la matrícula" para usar fecha de inicio del ciclo)
* Ciclo origen:
  - Nombre del ciclo
  - Universidad
  - Modalidad Académica (Presencial o Virtual)
  - Pago en (Contado o Cuotas)
* Ciclo destino:
  - Nombre del ciclo
  - Universidad
  - Modalidad Académica (Presencial o Virtual)
  - Pago en (Contado o Cuotas)


### FR-003 Modalidades disponibles

El sistema MUST aceptar únicamente las modalidades académicas que aparecen en parameters.json para cada ciclo (Presencial o Virtual).



### FR-006 Desglose de operaciones

El sistema MUST mostrar junto al resultado final el desglose de las operaciones matemáticas realizadas, incluyendo:

* Semanas totales del ciclo origen
* Semanas transcurridas a la fecha de traslado
* Semanas restantes
* Fórmula y resultado del saldo disponible
* Fórmula y resultado del costo del ciclo destino
* Operación final y resultado

### FR-006.1 Estructura de salida del cálculo

El sistema MUST devolver el resultado con la siguiente estructura:

* `saldo_origen`: valor residual del ciclo de origen
* `costo_destino`: valor residual del ciclo de destino
* `diferencia`: `saldo_origen - costo_destino`
* `estado`: uno de `SALDO_A_FAVOR`, `MONTO_PENDIENTE`, `TRASLADO_CUBIERTO`
* `mensaje`: texto amigable con el resultado
* `detalle`: objeto con `semanas_totales`, `semanas_consumidas` y `semanas_restantes` para origen y destino

### FR-007 Validación prioritaria en cascada

El sistema MUST aplicar las validaciones en orden de criticidad y detener el proceso ante el primer error válido encontrado.

El orden de validación será:

1. Existencia de ciclo origen y ciclo destino en parameters.json
2. Igualdad de modalidad de pago entre origen y destino
3. Fecha de traslado dentro del periodo académico de ambos ciclos
4. (Opcional) Integridad de los datos de entrada (tipos, formato de fecha)

### FR-008 Condiciones de pago disponibles

El sistema MUST aceptar únicamente las siguientes condiciones de pago:

* Contado
* Cuotas

### FR-009 Validación de igualdad de modalidad de pago

El sistema MUST rechazar el traslado si pago_en_origen != pago_en_destino.

Mensaje de error: "No se permiten traslados entre modalidades de pago diferentes. Si requiere este tipo de traslado, debe procesarlo manualmente."

### FR-012 Reglas de cálculo de semanas consumidas (CONTADO)

> Renumerado 2026-07-07 al fusionar con `origin/FEATURE-SDD-ENTERPRISE` (commit `37e6277`, edición manual paralela a esta sesión): originalmente etiquetado "FR-010" en esa edición, pero ese número ya lo usa el FR-010 de esta sesión ("Desglose expresado como cálculo manual"). Contenido sin cambios, solo el número.

El sistema MUST aplicar las siguientes reglas para determinar semanas consumidas en modalidad CONTADO:

* Las semanas se anclan al calendario global: cada semana empieza en lunes y termina en domingo.
* Si la fecha de traslado cae en **lunes o martes**, la semana actual NO se considera consumida.
* Si la fecha de traslado cae entre **miércoles y domingo**, la semana actual SÍ se considera consumida.
* Las semanas de feriado completas no se cuentan como consumidas y se restan del cálculo.

### FR-013 Reglas de cálculo de semanas consumidas (CUOTAS)

> Renumerado 2026-07-07 (era "FR-011" en `origin/FEATURE-SDD-ENTERPRISE`, colisionaba con el FR-011 de esta sesión). Contenido sin cambios.

El sistema MUST aplicar las siguientes reglas para determinar semanas consumidas en modalidad CUOTAS:

* Las semanas se anclan a la **fecha de inicio del periodo de la cuota**, no al lunes del calendario.
* El algoritmo calcula solo el valor residual de la **cuota vigente** en la fecha del traslado (no suma todas las cuotas futuras).
* El periodo de una cuota va desde su fecha de inicio hasta la fecha de la siguiente cuota.
* Para la última cuota, el periodo va hasta el fin del ciclo.
* Las semanas feriado dentro del periodo de la cuota no se consideran consumidas.
* Si la fecha de traslado es anterior a la primera cuota, se debe el valor completo de la primera cuota.
* Si la fecha de traslado es igual o posterior al fin del ciclo, el valor residual es `0.00`.

# 4. Requisitos No Funcionales (NFR)

### NFR-1

El cálculo deberá completarse en menos de 200 milisegundos desde el envío de los datos.

### NFR-2

El sistema MUST utilizar `decimal.Decimal` para todos los cálculos de montos en soles para evitar errores de redondeo.

---

# 5. Casos Borde

### CB-1 Fecha fuera del rango académico

Resultado esperado:

El sistema bloquea el cálculo e informa que la fecha de traslado es inválida con el mensaje exacto: "La fecha de traslado está fuera del rango del ciclo [ORIGEN/DESTINO]."

### CB-2 Ciclo origen igual a ciclo destino

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Traslado cubierto exactamente"

### CB-3 Modalidad inexistente para el ciclo seleccionado

Resultado esperado:

El sistema bloquea el cálculo e informa que la modalidad no existe para el ciclo seleccionado.

### CB-4 Semana de feriado (Fiestas Patrias)

Resultado esperado:

El sistema ajusta el cálculo saltando la semana de feriado y usa la fecha ajustada para determinar semanas consumidas.

**Feriados oficiales:**
* 28/07 (Fiestas Patrias)
* 29/07 (Fiestas Patrias)
* 25/12 (Navidad)

### CB-5 Semana de feriado (Navidad)

Resultado esperado:

El sistema ajusta el cálculo saltando la semana de feriado (25/12) y la excluye completamente del cómputo de semanas de clase.

### CB-6 Resultado exactamente igual a cero

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Traslado cubierto exactamente"

### CB-7 Traslado durante la última semana académica

Resultado esperado:

El sistema calcula el resultado utilizando únicamente las semanas académicas restantes disponibles según las reglas vigentes.

### CB-6 Ciclo inexistente

Resultado esperado:

El sistema bloquea el cálculo e informa: "Ciclo [origen/destino] no encontrado en la base de datos"

### CB-8 CUOTAS: fecha de traslado anterior al inicio de la primera cuota (FR-011)

Dado un traslado CUOTAS donde `fecha_traslado` es anterior al vencimiento de la cuota 1 (caso `antes_primera_cuota`),

Resultado esperado (ADR-4 §4.3): `fecha_inicio_periodo: null`, `fecha_fin_periodo` = fecha de vencimiento de la cuota 1, `semana_actual: 1`.

### CB-9 CUOTAS: fecha de traslado en o después del fin del ciclo (FR-011)

Dado un traslado CUOTAS donde `fecha_traslado >= fecha_fin_ciclo` (caso `fuera_de_ciclo`, nada pendiente),

Resultado esperado (ADR-4 §4.3): `fecha_inicio_periodo: null`, `fecha_fin_periodo: null`, `semana_actual: null` — explícitos, no omitidos.

### CB-10 CONTADO: `semana_actual` no debe exceder `semanas_totales` (FR-011)

Dado un traslado CONTADO donde el cálculo crudo de `indice_semana_actual` podría exceder `semanas_totales` (ciclo que no calza en semanas completas),

Resultado esperado (ADR-4 §4.4): `semana_actual` se clampea a `min(indice_semana_actual, semanas_totales)`, garantizando el invariante `semana_actual ≤ semanas_totales` en ambas modalidades.

---

# 6. Assumptions

### A-1

Asumimos que el Excel oficial proporcionado por Gerencia contiene información correcta y actualizada.

Si esta información es incorrecta, los resultados calculados serán inválidos.

### A-2

Asumimos que las fechas académicas necesarias para determinar semanas restantes se encuentran disponibles en la fuente oficial.

Si estas fechas no existen o son incorrectas, el sistema no podrá calcular correctamente los saldos.

### A-3

Asumimos que el Excel define claramente las semanas de feriados institucionales (Fiestas Patrias: 28/07 y 29/07, y Navidad: 25/12) que afectan el calendario académico.

Si esta definición cambia, será necesario actualizar las constantes en el código.

---

# 7. Decisiones de implementación adoptadas

### D-1

Los parámetros oficiales se actualizarán mediante un archivo JSON estático generado a partir del Excel aprobado por Gerencia. En esta primera versión, la actualización será manual y se realizará por el área responsable cuando exista una nueva versión oficial.

### D-2

La solución permitirá calcular traslados únicamente cuando la fecha de traslado se encuentre dentro del periodo académico vigente definido en los parámetros oficiales. Si la fecha está fuera de rango, el sistema bloqueará el cálculo y mostrará el mensaje correspondiente.

### D-3

Los resultados se mostrarán en pantalla y podrán copiarse para soporte, pero no se almacenarán en una base de datos en esta versión. El objetivo es ofrecer una herramienta operativa rápida y sencilla para el analista.

### D-4

La solución será una aplicación web monolítica en Python 3.11+. Flask servirá la interfaz (HTML, CSS y JavaScript estático en `templates/` y `static/`) y expondrá un endpoint REST para recibir los datos del traslado y devolver el resultado, el estado y el desglose del cálculo. La lógica de negocio (validaciones y cálculo) residirá en módulos Python independientes de las rutas HTTP, testeables con pytest.

> **Endpoint real (verificado en `zproyect/app.py`, 2026-07-07):** `POST /api/traslados/calcular`, no `/api/transfer-calculator` como decía esta sección antes. Rutas adicionales implementadas: `GET /health` (healthcheck) y `GET /api/ciclos` (lista los ciclos de `parameters.json`).

### D-5

Las dependencias de runtime y calidad se declararán en `requirements.txt` (Flask, pytest, pytest-cov, ruff). Los montos se manejarán con `decimal.Decimal` para evitar errores de redondeo. Las fechas de entrada del usuario se parsearán en formato DD/MM/YYYY usando `datetime` de la biblioteca estándar.

---

# 8. Scope

## DENTRO

* Cálculo automático de montos de traslado.
* Cálculo para condición de pago al contado.
* Cálculo para condición de pago en cuotas.
* Validación de modalidad académica (presencial/virtual).
* Validación de fechas académicas.
* Validación de modalidades disponibles.
* Validación de igualdad de modalidad de pago.
* Determinación de saldo a favor.
* Determinación de traslado cubierto.
* Determinación de monto pendiente.
* Cálculo de semanas con ajuste por feriados.

## FUERA

* Registro histórico de traslados.
* Integración con sistemas académicos.
* Integración con sistemas financieros.
* Generación de comprobantes.
* Envío de correos electrónicos.
* Gestión de matrículas.
* Gestión de becas.
* Gestión de descuentos.
* Modificación de información académica o financiera.

