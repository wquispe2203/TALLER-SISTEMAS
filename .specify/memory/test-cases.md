# test-cases.md

## Estrategia de pruebas

La estrategia de pruebas para el traslado de estudiantes Vonex adopta un enfoque basado en riesgos financieros y de cumplimiento operacional. Las prioridades se asignan de acuerdo al impacto directo en la caja e integridad contable institucional.
*   **Pruebas del Motor Financiero**: Enfoque determinista con pruebas unitarias exhaustivas y simulaciones de precisión decimal.
*   **Pruebas de Transición y Negocio**: Validación en flujos de aceptación y rechazo de saldo, exoneraciones de costos administrativos y control de estados.
*   **Pruebas de Integridad de Datos (Auditoría)**: Asegurar el registro inmutable de transacciones para revisiones financieras.

## Matriz de cobertura

| ID Caso de Prueba | Regla de Negocio / US | Área Temática | Severidad / Riesgo |
|---|---|---|---|
| TC-001 - TC-003 | RN-10, RN-11, RN-12, RN-13 | Cálculo Financiero | Crítico - Financiero |
| TC-004 - TC-005 | RN-14, RN-15 | Costo Administrativo | Alto - Financiero |
| TC-006 - TC-009 | RN-04 | Modalidad Contado | Alto - Financiero |
| TC-010 - TC-013 | RN-03, RN-05, RN-07 | Modalidad Cuotas | Alto - Financiero |
| TC-014 - TC-017 | RN-09 | Semana Marketera | Crítico - Financiero |
| TC-018 - TC-020 | US-2, RN-13 | Ejecución del Traslado | Crítico - Operativo |
| TC-021 - TC-023 | RN-16 | Anulación de Traslado | Alto - Contable |
| TC-024 | RN-17 | Auditoría y Trazabilidad | Alto - Cumplimiento |
| TC-025 - TC-033 | Casos Borde y Límites | Límites y Redondeos | Crítico - Financiero |

---

## Casos de prueba – Cálculo financiero

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-001 | Happy Path | Alta | Validar cálculo financiero con resultado de saldo positivo (excedente) | Estudiante registrado con saldo a favor mayor que el costo destino + costo administrativo. | - Saldo Origen: S/510.00<br>- Costo Destino: S/255.00<br>- Costo Administrativo: S/20.00 | 1. Ingresar datos de origen y destino en el módulo de cálculo.<br>2. Presionar "Simular cálculo". | - Resultado neto es S/255.00 a favor.<br>- Estado: Aprobado sin deuda.<br>- Mensaje de excedente para aplicación futura. |
| TC-002 | Happy Path | Alta | Validar cálculo financiero con resultado de saldo exacto (S/0.00) | Estudiante con saldo igual al costo destino + administrativo. | - Saldo Origen: S/382.50<br>- Costo Destino: S/362.50<br>- Costo Administrativo: S/20.00 | 1. Ingresar datos origen y destino.<br>2. Presionar "Simular cálculo". | - Resultado neto es S/0.00.<br>- Estado: Aprobado (Saldo exacto). |
| TC-003 | Happy Path | Alta | Validar cálculo financiero con resultado de saldo negativo (deuda) | Estudiante con saldo menor al costo destino + administrativo. | - Saldo Origen: S/382.50<br>- Costo Destino: S/510.00<br>- Costo Administrativo: S/20.00 | 1. Ingresar datos origen y destino.<br>2. Presionar "Simular cálculo". | - Resultado neto es -S/147.50.<br>- Estado: Deuda pendiente.<br>- Se requiere aceptación del alumno para ejecutar. |
| TC-004 | Happy Path | Alta | Validar aplicación correcta del costo administrativo estándar | Fecha del traslado fuera de la primera semana y de la semana marketera. | - Costo Administrativo estándar: S/20.00 | 1. Simular traslado con fecha efectiva en la semana 3 del ciclo destino. | - Se adiciona un costo administrativo de S/20.00 en la diferencia final. |
| TC-005 | Happy Path | Alta | Validar exoneración del costo administrativo en semana marketera y primera semana académica | Fecha del traslado en los rangos indicados. | - Exoneración según RN-15 | 1. Simular traslado con fecha efectiva coincidente con la primera semana académica del ciclo destino. | - Costo administrativo es calculado como S/0.00. |

---

## Casos de prueba – Modalidad contado

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-006 | Happy Path | Alta | Validar uso del monto efectivamente pagado con descuento | Estudiante pagó con descuento contado. | - Precio lista: S/1000.00<br>- Monto pagado real: S/800.00 | 1. Cargar el registro del alumno.<br>2. Ejecutar simulación de traslado. | - El cálculo de saldo residual origen utiliza S/800.00 como base, no S/1000.00. |
| TC-007 | Happy Path | Alta | Validar prorrateo contado consumiendo semana marketera | El ciclo origen posee semana marketera. | - Duración ciclo: 10 semanas (incluye 1 marketera) | 1. Simular traslado con fecha efectiva en semana 2 de un ciclo origen con modalidad contado. | - La semana marketera se contabiliza como consumida para el prorrateo contado de saldo residual. |
| TC-008 | Happy Path | Alta | Validar cálculo de saldo residual contado a mitad de ciclo | Ciclo origen regular de 12 semanas. | - Monto pagado: S/1200.00<br>- Semanas transcurridas: 6<br>- Semanas restantes: 6 | 1. Simular traslado a la mitad exacta de la programación del ciclo. | - Saldo residual de origen es calculado exactamente en S/600.00. |
| TC-009 | Borde | Alta | Validar cálculo de saldo residual contado el último día del ciclo | El estudiante solicita traslado al finalizar las clases. | - Semanas restantes: 0 | 1. Simular traslado con fecha efectiva igual al último día del calendario del ciclo origen. | - Saldo residual de origen es S/0.00. |

---

## Casos de prueba – Modalidad cuotas

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-010 | Happy Path | Alta | Validar equivalencia estricta de cuotas ("partes") | El sistema registra modalidad "partes" para el alumno. | - Cuotas mensuales equivalentes a partes. | 1. Consultar estado de pagos del alumno en modalidad partes. | - El sistema interpreta que el estudiante tiene modalidad cuotas y aplica las reglas financieras de cuotas. |
| TC-011 | Happy Path | Alta | Validar prorrateo estándar de cuota por semanas transcurridas | Alumno se traslada a mitad de cuota (semana 2 de 4). | - Cuota de 4 semanas: S/300.00<br>- Semanas académicas restantes de la cuota: 2 | 1. Ingresar fecha efectiva del traslado en la semana 2 de la cuota activa. | - Saldo residual de la cuota pagada equivale a S/150.00 (el 50% restante). |
| TC-012 | Happy Path | Alta | Validar transición entre cuotas vencidas y cuotas por vencer | El alumno pagó 2 cuotas de 4 contratadas. | - 2 cuotas de 4 pagadas en origen. | 1. Simular el traslado al término exacto de la semana 8 (fin de la segunda cuota). | - El saldo residual origen se calcula sobre el valor no consumido de las cuotas pagadas. Las cuotas no pagadas no suman saldo residual. |
| TC-013 | Borde | Alta | Validar cambio de porcentaje los días jueves según calendario administrativo | Calendario administrativo de prorrateo corre de jueves a miércoles. | - Fecha efectiva: Jueves del cambio de semana. | 1. Simular traslado el día miércoles (antes del cambio).<br>2. Simular traslado el jueves (día del cambio). | - La simulación del jueves refleja una semana académica adicional consumida frente a la simulación del miércoles previo. |

---

## Casos de prueba – Semana marketera

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-014 | Happy Path | Alta | Validar conservación completa del valor de la cuota en semana marketera | Ciclo destino/origen con semana marketera en cuotas. | - Fecha efectiva dentro de semana marketera. | 1. Simular traslado con fecha efectiva en semana marketera. | - El saldo residual o costo de la cuota en curso conserva el 100% de su valor, sin deducción por prorrateo. |
| TC-015 | Borde | Alta | Validar conservación de valor hasta el miércoles de la segunda semana administrativa | Límite de no descuento en ciclos con semana marketera. | - Fecha efectiva: Miércoles de la 2da semana administrativa. | 1. Ingresar fecha efectiva del traslado el miércoles de la semana 2. | - El prorrateo de la cuota sigue indicando 0% consumido (se conserva el 100% del valor de la cuota). |
| TC-016 | Borde | Alta | Validar inicio del prorrateo desde el jueves de la segunda semana administrativa | Límite del inicio del descuento. | - Fecha efectiva: Jueves de la 2da semana administrativa. | 1. Ingresar fecha efectiva del traslado el jueves de la semana 2. | - Inicia el prorrateo y se calcula el descuento correspondiente al avance administrativo. |
| TC-017 | Negativo | Media | Validar que la regla de semana marketera no se aplique a modalidades contado de forma errónea | Configuración de ciclo origen en contado con semana marketera. | - Modalidad: Contado | 1. Simular traslado en la semana marketera de un ciclo contado. | - La semana marketera se prorratea y consume valor de acuerdo con la fórmula estándar de contado (RN-04). |

---

## Casos de prueba – Ejecución

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-018 | Happy Path | Alta | Validar ejecución exitosa con saldo a favor | Simulación previa con saldo neto positivo. | - Excedente: S/80.00 | 1. Completar simulación.<br>2. Presionar "Ejecutar traslado". | - El traslado se registra con estado "Ejecutado".<br>- Se genera el abono automático de S/80.00 a futuras cuotas en destino. |
| TC-019 | Happy Path | Alta | Validar ejecución exitosa de traslado con saldo negativo tras confirmación de pago | El estudiante acepta y paga la deuda. | - Deuda: S/100.00<br>- Decisión: Aceptada y confirmada. | 1. Seleccionar "Estudiante acepta y paga deuda".<br>2. Registrar y ejecutar traslado. | - El traslado cambia a estado "Ejecutado".<br>- El registro de auditoría almacena la aceptación de la deuda. |
| TC-020 | Negativo | Alta | Impedir la ejecución de un traslado con deuda cuando el alumno la rechaza | El estudiante rechaza pagar el saldo negativo. | - Deuda: S/100.00<br>- Decisión: Rechazada. | 1. Registrar "Rechazado por el estudiante".<br>2. Intentar hacer click en "Ejecutar traslado". | - El sistema deshabilita el botón de ejecución o retorna error de validación.<br>- El traslado queda en estado "Cancelado/No Aprobado". |

---

## Casos de prueba – Anulación

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-021 | Happy Path | Alta | Validar anulación exitosa por respuesta posterior del estudiante | Traslado previo en estado "Ejecutado". | - ID Traslado: TR-9988 | 1. Ingresar al traslado TR-9988.<br>2. Presionar "Anular traslado".<br>3. Registrar ID del correo del alumno que solicita anulación. | - El estado del traslado cambia a "Anulado".<br>- Se revierten los saldos de forma atómica en origen y destino.<br>- El registro histórico guarda la auditoría de la anulación. |
| TC-022 | Negativo | Media | Impedir la anulación de un traslado que no ha sido ejecutado previamente | Traslado en estado "Simulado" o "Rechazado". | - ID Traslado: TR-9989 (Simulado) | 1. Intentar acceder a la acción de anulación del traslado. | - La acción de anulación no está disponible o retorna un mensaje de error ("Solo se pueden anular traslados ejecutados"). |
| TC-023 | Negativo | Alta | Rechazar anulación si no se proporciona el ID del correo de respaldo | Operador no ingresa la evidencia en observaciones/correo. | - Campo correo/evidencia vacío. | 1. Intentar confirmar la anulación sin ingresar el correo de respaldo. | - El sistema arroja error de validación requiriendo el ID del correo del solicitante. |

---

## Casos de prueba – Auditoría

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-024 | Happy Path | Alta | Validar persistencia completa e inmutable de todos los campos de auditoría | Se completa una ejecución de traslado con éxito. | - Usuario Helpdesk: "usr_helpdesk1"<br>- Datos financieros calculados. | 1. Ejecutar el traslado.<br>2. Consultar el log de auditoría del traslado generado. | - Se verifica que el registro contiene exactamente todos los campos de RN-17 poblados y correctos.<br>- No se permite modificar este registro. |

---

## Casos de prueba – Casos borde

| ID | Tipo | Prioridad | Objetivo | Precondiciones | Datos de prueba | Pasos | Resultado esperado |
|---|---|---|---|---|---|---|---|
| TC-025 | Borde | Alta | Traslado exactamente un día jueves (cambio de prorrateo) | Día de cambio administrativo. | - Fecha efectiva: Jueves a las 00:00:01 | 1. Simular traslado con fecha de un jueves de inicio de semana administrativa. | - Se aplica el nuevo porcentaje de descuento correspondiente a la semana que inicia. |
| TC-026 | Borde | Alta | Traslado exactamente el miércoles previo a las 23:59:59 | Fin de la semana administrativa. | - Fecha efectiva: Miércoles a las 23:59:59 | 1. Simular traslado con fecha del miércoles por la noche. | - Se mantiene el porcentaje de la semana administrativa en curso, sin pasar al del jueves. |
| TC-027 | Borde | Alta | Traslado durante la semana marketera de destino | Validación de exoneración. | - Fecha efectiva: Coincidente con semana marketera de destino. | 1. Simular traslado. | - El costo administrativo es S/0.00 (Exonerado). |
| TC-028 | Borde | Alta | Traslado durante la primera semana académica de destino | Validación de exoneración. | - Fecha efectiva: Primera semana académica de destino. | 1. Simular traslado. | - El costo administrativo es S/0.00 (Exonerado). |
| TC-029 | Borde | Alta | Traslado el último día del ciclo | Validación de fin de ciclo. | - Fecha efectiva: Último día de clases de destino. | 1. Simular traslado con fecha final del ciclo. | - El cálculo de residual de destino se ajusta a 0 semanas restantes o al cobro mínimo estipulado. |
| TC-030 | Borde | Media | Ciclo de corta duración con una sola cuota | Ciclo origen tiene una única cuota de 4 semanas. | - Cuotas totales: 1 | 1. Simular traslado de estudiante en este ciclo a la semana 2. | - El prorrateo calcula correctamente sobre las 4 semanas de la única cuota. |
| TC-031 | Borde | Alta | Saldo residual de origen es exactamente cero | Estudiante no ha pagado nada o ya consumió todo su valor. | - Saldo Origen: S/0.00 | 1. Simular traslado de estudiante. | - El sistema calcula Saldo Residual Origen = S/0.00 sin generar errores de división por cero. |
| TC-032 | Borde | Alta | Diferencia mínima a pagar de S/0.01 | El balance neto da una deuda insignificante. | - Saldo Neto: -S/0.01 | 1. Realizar simulación. | - El sistema arroja saldo negativo de -S/0.01 y requiere la decisión del estudiante. |
| TC-033 | Borde | Alta | Diferencia positiva mínima de S/0.01 | El balance neto da un excedente insignificante. | - Saldo Neto: S/0.01 | 1. Realizar simulación. | - El sistema aprueba el traslado y destina S/0.01 de excedente a futuras cuotas. |
| TC-034 | Borde | Alta | Validar exoneración de S/20 durante la primera semana de clases del estudiante | El ciclo inicia el 01/06 y el estudiante se matricula el 03/06. | - Fecha matrícula: 03/06<br>- Fecha inicio ciclo: 01/06<br>- Fecha efectiva traslado: 10/06 (dentro de los 7 días calendario tras su matrícula) | 1. Ingresar fecha efectiva del traslado como 10/06 para un estudiante matriculado el 03/06.<br>2. Ejecutar la simulación de cálculo de traslado. | - El costo administrativo es calculado como S/0.00 (Exonerado). |
| TC-035 | Borde | Alta | Validar cobro de S/20 pasado los 7 días de clases del estudiante | El ciclo inicia el 01/06 y el estudiante se matricula el 03/06. | - Fecha matrícula: 03/06<br>- Fecha inicio ciclo: 01/06<br>- Fecha efectiva traslado: 11/06 (después de los 7 días calendario tras su matrícula) | 1. Ingresar fecha efectiva del traslado como 11/06 para un estudiante matriculado el 03/06.<br>2. Ejecutar la simulación de cálculo de traslado. | - El costo administrativo se establece en S/20.00. |

---

## Suite de regresión recomendada

Para asegurar la integridad del motor financiero de traslados en actualizaciones del sistema, se debe ejecutar de manera automatizada en cada release la siguiente sub-suite de regresión:
1.  **TC-001 (Saldo positivo)**: Asegura que el flujo de excedente no se rompa.
2.  **TC-003 (Saldo negativo)**: Asegura que no se omitan deudas pendientes.
3.  **TC-005 (Exoneración)**: Valida que las reglas especiales de semana marketera/primera semana sigan aplicando correctamente S/0.00 de costo administrativo.
4.  **TC-008 (Cálculo Contado)**: Asegura la correcta aplicación matemática de la fórmula de contado.
5.  **TC-015 y TC-016 (Límites de Semana Marketera en Cuotas)**: Monitorea que no ocurran desfases en las fechas de prorrateo entre los días miércoles y jueves administrativos.
6.  **TC-021 (Anulación)**: Garantiza que la reversión atómica de movimientos no sufra de efectos secundarios (side effects) financieros.
7.  **TC-024 (Inmutabilidad de Auditoría)**: Confirma que las modificaciones al código de la aplicación no expongan o permitan alterar los logs de auditoría preexistentes.
