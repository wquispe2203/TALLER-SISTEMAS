# Cambios Consolidados para Alineación con Algoritmo v4

Este archivo contiene todos los cambios necesarios para alinear los archivos de memoria con el algoritmo de traslados académicos v4. Separa cada sección con marcadores claros para que un script pueda aplicar los cambios automáticamente.

---

## ARCHIVO: spec.md

### CAMBIO 1: AC-3.2 - Reemplazar contenido sobre beneficios por feriados

**BUSCAR:**
```
### AC-3.2 (Ajuste por feriados)

Dado un cálculo de traslado donde la fecha cae en una semana de feriado (Fiestas Patrias o Navidad),

Cuando el sistema genera el desglose de las operaciones,

Entonces el sistema debe incluir explícitamente en el detalle:

* Las semanas de feriado que se cancelan y se saltan en el calendario académico.
* La tarifa regular versus la tarifa con el beneficio aplicado utilizada para calcular el saldo disponible del ciclo origen.
* La aclaración de que el ciclo destino se está cobrando con tarifa regular.
```

**REEMPLAZAR POR:**
```
### AC-3.2 (Ajuste por feriados)

Dado un cálculo de traslado donde la fecha cae en una semana de feriado (Fiestas Patrias o Navidad),

Cuando el sistema genera el desglose de las operaciones,

Entonces el sistema debe incluir explícitamente en el detalle:

* Las semanas de feriado que se cancelan y se saltan en el calendario académico.
* La fecha ajustada usada para el cálculo de semanas consumidas.
* La aclaración de que las semanas efectivas incluyen las semanas de feriado.
```

---

### CAMBIO 2: Casos Borde - Eliminar CB-4, CB-5, CB-8, CB-9

**BUSCAR:**
```
### CB-4 Estado SUSPENDIDO

Resultado esperado:

El sistema bloquea el cálculo e informa que el estado no permite realizar traslados.

### CB-5 Estado RETIRADO

Resultado esperado:

El sistema bloquea el cálculo e informa que el estado no permite realizar traslados.
```

**REEMPLAZAR POR:**
```
### CB-4 Semana de feriado (Fiestas Patrias)

Resultado esperado:

El sistema ajusta el cálculo saltando la semana de feriado y usa la fecha ajustada para determinar semanas consumidas.

### CB-5 Semana de feriado (Navidad)

Resultado esperado:

El sistema ajusta el cálculo saltando la semana de feriado y usa la fecha ajustada para determinar semanas consumidas.
```

---

### CAMBIO 3: Casos Borde - Eliminar CB-8 y CB-9

**BUSCAR:**
```
### CB-8 Estudiante con descuento activo

Resultado esperado:

El sistema utiliza el monto con descuento para calcular el saldo disponible del ciclo origen y elimina el descuento para calcular el costo del ciclo destino.

### CB-9 Estudiante con beca o beneficio activo

Resultado esperado:

El sistema utiliza el beneficio vigente únicamente para determinar el saldo disponible del ciclo origen y calcula el ciclo destino utilizando la tarifa regular sin beneficios.
```

**REEMPLAZAR POR:**
```
### CB-6 Ciclo inexistente

Resultado esperado:

El sistema bloquea el cálculo e informa: "Ciclo [origen/destino] no encontrado en la base de datos"
```

---

### CAMBIO 4: Assumptions - Eliminar A-3 y A-4

**BUSCAR:**
```
### A-3

Asumimos que los descuentos y beneficios vigentes son conocidos antes de iniciar el cálculo.

Si esta información es incorrecta o incompleta, el resultado económico será incorrecto.

### A-4

Asumimos que únicamente los estados MATRICULADO y PAGADO permiten realizar traslados.

Si esta regla cambia, será necesario actualizar las validaciones de negocio.
```

**REEMPLAZAR POR:**
```
### A-3

Asumimos que el Excel define claramente las semanas de feriado institucionales (Fiestas Patrias y Navidad) que afectan el calendario académico.

Si esta definición cambia, será necesario actualizar las constantes en el código.
```

---

### CAMBIO 5: NFR - Agregar NFR-2 sobre decimal.Decimal

**BUSCAR:**
```
### NFR-1

El cálculo deberá completarse en menos de 200 milisegundos desde el envío de los datos.

---
```

**REEMPLAZAR POR:**
```
### NFR-1

El cálculo deberá completarse en menos de 200 milisegundos desde el envío de los datos.

### NFR-2

El sistema MUST utilizar `decimal.Decimal` para todos los cálculos de montos en soles para evitar errores de redondeo.

---
```

---

### CAMBIO 6: Scope - Eliminar referencias a estados y descuentos/beneficios

**BUSCAR:**
```
## DENTRO

* Cálculo automático de montos de traslado.
* Cálculo para condición de pago al contado.
* Cálculo para condición de pago en cuotas.
* Validación de modalidad académica (presencial/virtual).
* Validación de fechas académicas.
* Validación de estados de matrícula.
* Validación de modalidades disponibles.
* Determinación de saldo a favor.
* Determinación de traslado cubierto.
* Determinación de monto pendiente.
* Aplicación de reglas de descuentos y beneficios.
```

**REEMPLAZAR POR:**
```
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
```

---

### CAMBIO 7: CB-1 - Actualizar mensaje de error

**BUSCAR:**
```
### CB-1 Fecha fuera del rango académico

Resultado esperado:

El sistema bloquea el cálculo e informa que la fecha de traslado es inválida.
```

**REEMPLAZAR POR:**
```
### CB-1 Fecha fuera del rango académico

Resultado esperado:

El sistema bloquea el cálculo e informa que la fecha de traslado es inválida con el mensaje exacto: "La fecha de traslado está fuera del rango del ciclo [ORIGEN/DESTINO]."
```

---

### CAMBIO 8: CB-2 - Actualizar estado

**BUSCAR:**
```
### CB-2 Ciclo origen igual a ciclo destino

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Sin saldo pendiente"
```

**REEMPLAZAR POR:**
```
### CB-2 Ciclo origen igual a ciclo destino

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Traslado cubierto exactamente"
```

---

## ARCHIVO: plan.md

### CAMBIO 1: Módulo de Captura de Datos - Actualizar campos

**BUSCAR:**
```
### Módulo de Captura de Datos

Responsable de recibir la información de entrada del usuario y pasarla al siguiente paso.

* Fecha de traslado
* Ciclo origen
* Ciclo destino
* Modalidad
* Estado del estudiante
* Monto pagado
* Descuentos
* Beneficios
```

**REEMPLAZAR POR:**
```
### Módulo de Captura de Datos

Responsable de recibir la información de entrada del usuario y pasarla al siguiente paso.

* Fecha de traslado
* Ciclo origen (Nombre, Universidad, Modalidad Académica, Pago en)
* Ciclo destino (Nombre, Universidad, Modalidad Académica, Pago en)
```

---

### CAMBIO 2: Eliminar módulos obsoletos

**BUSCAR:**
```
### Módulo de Normalización y Parseo

Responsable de transformar los datos crudos recibidos en un formato estructurado, consistente y tipado antes de enviarlos a validación.

* Convertir fechas a formato estándar
* Normalizar nombres de modalidades y estados
* Validar tipos numéricos de montos y descuentos
* Construir un DTO / contrato de entrada
* Rechazar entradas imposibles de parsear

Este módulo asegura que la validación y el cálculo trabajen con datos limpios y predecibles.
```

**REEMPLAZAR POR:**
```
### Módulo de Normalización y Parseo

Responsable de transformar los datos crudos recibidos en un formato estructurado, consistente y tipado antes de enviarlos a validación.

* Convertir fechas a formato estándar
* Normalizar nombres de modalidades
* Validar tipos numéricos de montos
* Construir un DTO / contrato de entrada
* Rechazar entradas imposibles de parsear

Este módulo asegura que la validación y el cálculo trabajen con datos limpios y predecibles.
```

---

### CAMBIO 3: Módulo de Validaciones - Actualizar orden

**BUSCAR:**
```
### Módulo de Validaciones

Responsable de verificar en cascada y en orden de prioridad:

1. Estado permitido
2. Existencia de ciclo origen y ciclo destino
3. Modalidad existente para el ciclo
4. Fecha válida dentro del periodo académico
5. Integridad de montos, descuentos y beneficios

El módulo debe aplicar validaciones "fail-fast" para detener el proceso tan pronto se encuentre una condición inválida.
```

**REEMPLAZAR POR:**
```
### Módulo de Validaciones

Responsable de verificar en cascada y en orden de prioridad:

1. Existencia de ciclo origen y ciclo destino en parameters.json
2. Igualdad de modalidad de pago entre origen y destino
3. Fecha válida dentro del periodo académico de ambos ciclos
4. (Opcional) Integridad de los datos de entrada (tipos, formato de fecha)

El módulo debe aplicar validaciones "fail-fast" para detener el proceso tan pronto se encuentre una condición inválida.
```

---

### CAMBIO 4: Motor de Cálculo - Agregar feriados

**BUSCAR:**
```
### Motor de Cálculo de Traslados

Responsable de:

* Calcular semanas restantes
* Calcular saldo disponible
* Calcular costo requerido del ciclo destino
* Aplicar reglas para modalidad al contado
* Aplicar reglas para modalidad en cuotas
* Determinar saldo a favor, traslado cubierto o monto pendiente
```

**REEMPLAZAR POR:**
```
### Motor de Cálculo de Traslados

Responsable de:

* Calcular semanas restantes (con ajuste por semanas de feriado)
* Calcular saldo disponible
* Calcular costo requerido del ciclo destino
* Aplicar reglas para modalidad al contado
* Aplicar reglas para modalidad en cuotas
* Determinar saldo a favor, traslado cubierto o monto pendiente
* Calcular semanas consumidas con ajuste de fecha por feriados
```

---

### CAMBIO 5: ADR-2 - Actualizar descripción

**BUSCAR:**
```
## ADR-2

### DECISIÓN

Centralizar todos los parámetros académicos y financieros en una única fuente de datos derivada del Excel oficial.

### POR QUÉ

Garantiza consistencia con la información aprobada por Gerencia y cumple el principio de Single Source of Truth (SSoT) definido en la Constitución.
```

**REEMPLAZAR POR:**
```
## ADR-2

### DECISIÓN

Centralizar todos los parámetros académicos y financieros en una única fuente de datos derivada del Excel oficial.

### POR QUÉ

Garantiza consistencia con la información aprobada por Gerencia y cumple el principio de Single Source of Truth (SSoT) definido en la Constitución. El Excel también define las fechas de feriados que afectan el conteo de semanas.
```

---

### CAMBIO 6: Riesgos - Eliminar R-4 y agregar nuevo

**BUSCAR:**
```
### R-4

Nuevos estados académicos que modifiquen las reglas actuales de traslado.

**Mitigación:** Centralizar las validaciones de estado en un único componente para facilitar actualizaciones.
```

**REEMPLAZAR POR:**
```
### R-4

Cambio en el calendario de feriados institucionales.

**Mitigación:** Actualizar las constantes de semanas de feriado en el código cuando cambie la política institucional.
```

---

### CAMBIO 7: Dependencias - Actualizar D-3

**BUSCAR:**
```
### D-3

Definición formal de políticas de descuentos y beneficios.
```

**REEMPLAZAR POR:**
```
### D-3

Definición clara de las semanas de feriado institucionales.
```

---

## ARCHIVO: test-cases.md

### CAMBIO 1: Reemplazar todo el contenido con los 12 casos del algoritmo

**REEMPLAZAR TODO EL CONTENIDO POR:**
```
# Resumen Ejecutivo

Este documento define la suite de 12 casos de prueba (Test Cases) diseñados para validar la Calculadora de Montos de Traslado Académico según el algoritmo v4. Los casos están basados en datos reales del Excel oficial y cubren escenarios de éxito, validaciones y casos borde.

# Casos de Prueba (Test Cases)

## TC-1: Traslado CONTADO con saldo a favor

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: S/ 1350, duration_weeks: 20, fecha_inicio: 05/01/2026, fecha_fin: 19/06/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 3489.75"
- Saldo origen: S/ 3557.25
- Costo destino: S/ 67.50
- Diferencia: S/ 3489.75

---

## TC-2: Traslado CONTADO con monto pendiente

**Entradas:**
- Fecha de traslado: 20/03/2026
- Ciclo Origen: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: S/ 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)
- Ciclo Destino: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: MONTO_PENDIENTE
- Mensaje: "Monto pendiente: S/ 3867.75"
- Saldo origen: S/ 607.50
- Costo destino: S/ 4475.25
- Diferencia: -S/ 3867.75

---

## TC-3: Traslado CUOTAS cubierto exactamente (mismas cuotas)

**Entradas:**
- Fecha de traslado: 20/04/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CUOTAS (10 cuotas de S/ 510)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: TRASLADO_CUBIERTO
- Mensaje: "Traslado cubierto exactamente"
- Saldo origen: S/ 4080.00
- Costo destino: S/ 4080.00
- Diferencia: S/ 0.00

---

## TC-4: Modalidad de pago diferente (bloqueo)

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CUOTAS

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Error: "No se permiten traslados entre modalidades de pago diferentes. Si requiere este tipo de traslado, debe procesarlo manualmente."

---

## TC-5: Fecha fuera del rango del ciclo origen

**Entradas:**
- Fecha de traslado: 15/01/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Error: "La fecha de traslado está fuera del rango del ciclo origen (ANUAL MARZO)"

---

## TC-6: Lunes - semana no consumida

**Entradas:**
- Fecha de traslado: 13/04/2026 (lunes)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Saldo origen: S/ 4131.00 (la semana del 13/04 no se cuenta como consumida)

---

## TC-7: Martes - semana no consumida

**Entradas:**
- Fecha de traslado: 14/04/2026 (martes)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Saldo origen: S/ 4131.00 (igual que TC-6)

---

## TC-8: Miércoles - semana SÍ consumida

**Entradas:**
- Fecha de traslado: 15/04/2026 (miércoles)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Saldo origen: S/ 4016.25 (miércoles cuenta como semana consumida)

---

## TC-9: Traslado CUOTAS con saldo a favor (cuotas diferentes)

**Entradas:**
- Fecha de traslado: 25/05/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CUOTAS (8 cuotas de S/ 400)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 1570.00"
- Saldo origen: S/ 3570.00
- Costo destino: S/ 2000.00
- Diferencia: S/ 1570.00

---

## TC-10: Ciclo no encontrado

**Entradas:**
- Fecha de traslado: 15/05/2026
- Ciclo Origen: CICLO INEXISTENTE, SM, PRESENCIAL, CONTADO
- Ciclo Destino: SEMIANUAL ENERO, SM, VIRTUAL, CONTADO

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Error: "Ciclo origen no encontrado en la base de datos"

---

## TC-11: Semana de feriado - traslado durante feriado de julio

**Entradas:**
- Fecha de traslado: 29/07/2026 (miércoles, durante Fiestas Patrias)
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
- Ciclo Destino: ANUAL MARZO, UNI, VIRTUAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Estado: TRASLADO_CUBIERTO
- Diferencia: S/ 0.00
- Semanas efectivas: 42 (40 + 2 feriados)
- Saldo = Costo = S/ 2513.57

---

## TC-12: Cuota con vencimiento en semana de feriado

**Entradas:**
- Fecha de traslado: 01/08/2026
- Ciclo Origen: ANUAL MARZO, SM, PRESENCIAL, CUOTAS
- Cuota 6: due_date 08/08/2026 (después del feriado de julio, ya ajustada en el Excel)

**Pasos:**
1. Ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
- Cuota 6 (08/08/2026) está pendiente (01/08 < 08/08)
- Valor residual incluye cuota 6 y siguientes
```

---

## ARCHIVO: constitution.md

### CAMBIO 1: Art. 7 Boundaries - ASK FIRST - Eliminar y agregar

**BUSCAR:**
```
#### ASK FIRST

* Cambios en fórmulas de negocio.
* Nuevas modalidades de pago.
* Nuevos estados de matrícula.
* Nuevos tipos de traslado.
* Cambios en políticas de descuentos o beneficios.
* Integraciones con otros sistemas institucionales.
```

**REEMPLAZAR POR:**
```
#### ASK FIRST

* Cambios en fórmulas de negocio.
* Nuevas modalidades de pago.
* Nuevos tipos de traslado.
* Cambios en la definición de semanas de feriado.
* Nuevos campos requeridos en el Excel que afecten la estructura de parameters.json.
* Integraciones con otros sistemas institucionales.
```

---

## ARCHIVO: decisions.md

### CAMBIO 1: Agregar entrada sobre adopción del algoritmo v4

**AGREGAR AL FINAL (antes de la sección de Decisiones si existe):**
```
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
```

---

## ARCHIVO: lessons.md

### CAMBIO 1: Agregar lección aprendida

**AGREGAR AL FINAL (antes de la sección de Lecciones si existe):**
```
## 2026-07-04 Feature 001: Definir el algoritmo completo antes de redactar la especificación

**Qué Pasó:** Se redactó la especificación funcional (spec.md) antes de tener el algoritmo completo validado contra el Excel oficial, lo que generó discrepancias en campos de entrada, validaciones y casos de prueba.

**Causa Raíz:** No se partió del Excel y del algoritmo acordado con el negocio como base para redactar la spec.

**Qué Aprendimos:**
- Definir el algoritmo completo antes de redactar la especificación evita discrepancias y retrabajo.
- Los artefactos deben derivarse del algoritmo y del Excel, no al revés.

**Regla de Prevención:**
- En futuros proyectos, partir del Excel y del algoritmo acordado con el negocio, y luego redactar la spec, plan y casos de prueba basándose en esa base.
```

---

## ARCHIVO: session-state.md

### CAMBIO 1: Actualizar fase actual y archivos modificados

**BUSCAR:**
```
- **Fase Actual:** Implementación
- **Último Gate Aprobado:** Requerimientos aclarados
- **Marca de Tiempo del Último Gate:** 2026-07-01
```

**REEMPLAZAR POR:**
```
- **Fase Actual:** Implementación (alineación de artefactos con algoritmo v4)
- **Último Gate Aprobado:** Requerimientos aclarados
- **Marca de Tiempo del Último Gate:** 2026-07-04
```

---

### CAMBIO 2: Actualizar archivos modificados

**BUSCAR:**
```
## Archivos Modificados (En esta Sesión)

- .specify/memory/spec.md
- .specify/memory/plan.md
- .specify/memory/decisions.md
- .specify/memory/constitution.md
- .specify/memory/session-state.md
- .specify/memory/memory-index.md
- requirements.txt
- resumen_proyect.md
- faltantes_a_revisar.md
```

**REEMPLAZAR POR:**
```
## Archivos Modificados (En esta Sesión)

- .specify/memory/spec.md (alineación con algoritmo v4)
- .specify/memory/plan.md (actualización de módulos y riesgos)
- .specify/memory/test-cases.md (reemplazo por 12 casos del algoritmo)
- .specify/memory/constitution.md (actualización de Boundaries)
- .specify/memory/decisions.md (entrada sobre adopción del algoritmo v4)
- .specify/memory/lessons.md (lección sobre definición previa del algoritmo)
- .specify/memory/session-state.md (actualización de fase)
```

---

### CAMBIO 3: Actualizar siguiente paso

**BUSCAR:**
```
## Siguiente Paso

- Definir esquema de `data/parameters.json`
- Implementar módulos `validation.py`, `calculator.py` y `app.py` (futuro)
- Añadir pruebas básicas con pytest para escenarios felices y de error
```

**REEMPLAZAR POR:**
```
## Siguiente Paso

- Verificar que todos los artefactos referencien los mismos campos de entrada, las mismas validaciones y los mismos casos de prueba.
- Ejecutar la suite de tests actualizada contra el algoritmo implementado para confirmar la coherencia.
- Implementar módulos `validation.py`, `calculator.py` y `app.py` (futuro)
```

---

## FIN DE LOS CAMBIOS

Todos los cambios están organizados por archivo. Un script puede procesar este archivo aplicando cada cambio secuencialmente usando búsqueda y reemplazo de texto.
