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
* Resultado: S/ 1060.72 de saldo a favor
* Estado: "Saldo a favor"

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
* Resultado: S/ 1060.72 pendiente de pago
* Estado: "Monto pendiente"

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

* Semanas totales del ciclo origen (incluyendo semanas de feriado)
* Semanas transcurridas a la fecha de traslado (ajustado por feriados)
* Semanas restantes
* Fórmula y resultado del saldo disponible (con valor residual de contado/cuotas)
* Fórmula y resultado del costo del ciclo destino
* Operación final y resultado

### AC-3.2 (Ajuste por feriados)

Dado un cálculo de traslado donde la fecha cae en una semana de feriado (Fiestas Patrias o Navidad),

Cuando el sistema genera el desglose de las operaciones,

Entonces el sistema debe incluir explícitamente en el detalle:

* Las semanas de feriado que se cancelan y se saltan en el calendario académico.
* La fecha ajustada usada para el cálculo de semanas consumidas.
* La aclaración de que las semanas efectivas incluyen las semanas de feriado.

### AC-3.3 (Exportación o copia rápida para atención de tickets)

Dado que el sistema ha generado el desglose de operaciones con éxito,

Cuando el analista necesita enviar la justificación del cálculo al estudiante,

Entonces la interfaz debe proporcionar un botón de "Copiar resumen" que capture todo el desglose en formato de texto plano estructurado, listo para ser pegado en un ticket de soporte.

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

### FR-010 Reglas de cálculo de semanas consumidas (CONTADO)

El sistema MUST aplicar las siguientes reglas para determinar semanas consumidas en modalidad CONTADO:

* Las semanas se anclan al calendario global: cada semana empieza en lunes y termina en domingo.
* Si la fecha de traslado cae en **lunes o martes**, la semana actual NO se considera consumida.
* Si la fecha de traslado cae entre **miércoles y domingo**, la semana actual SÍ se considera consumida.
* Las semanas de feriado completas no se cuentan como consumidas y se restan del cálculo.

### FR-011 Reglas de cálculo de semanas consumidas (CUOTAS)

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

El sistema ajusta el cálculo saltando la semana de feriado y usa la fecha ajustada para determinar semanas consumidas.

**Feriados oficiales:**
* 28/07 (Fiestas Patrias)
* 29/07 (Fiestas Patrias)
* 25/12 (Navidad)

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

La solución será una aplicación web monolítica en Python 3.11+. Flask servirá la interfaz (HTML, CSS y JavaScript estático en `templates/` y `static/`) y expondrá un endpoint REST, por ejemplo `POST /api/transfer-calculator`, para recibir los datos del traslado y devolver el resultado, el estado y el desglose del cálculo. La lógica de negocio (validaciones y cálculo) residirá en módulos Python independientes de las rutas HTTP, testeables con pytest.

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

