# constitution.md

## Art. 1 · Purpose & Scope

- **Propósito**: Esta constitución establece los principios fundamentales, directrices de diseño y límites operacionales no negociables para el desarrollo, pruebas y mantenimiento de la feature **"Traslado de Estudiantes Vonex"**. Su objetivo es salvaguardar la integridad financiera de la institución, asegurar la transparencia operativa y garantizar la consistencia en el tratamiento de los traslados de estudiantes.
- **Ámbito de Aplicación**: Todos los componentes de software (servicios, motores de cálculo, repositorios, controladores e interfaces de usuario) que participen directa o indirectamente en el cálculo, ejecución, auditoría o anulación de un traslado de estudiante entre ciclos académicos están sujetos a las normas de este documento. Ninguna regla de negocio o requerimiento técnico podrá contradecir los artículos aquí descritos.
- **Filosofía SDD**: El desarrollo de esta feature se guiará estrictamente por la especificación previa de comportamiento. Toda funcionalidad implementada debe ser observable, defendible mediante pruebas e identificable directamente en los criterios de aceptación formales.

## Art. 2 · Core Domain Definitions

- **Traslado**: Proceso administrativo y financiero mediante el cual un estudiante cambia su matrícula activa desde un ciclo académico de origen hacia un ciclo de destino.
- **Saldo Residual de Origen**: Valor neto correspondiente a la fracción de servicio educativo pagado por el estudiante en el ciclo de origen que aún no ha sido devengado por la institución académica a la fecha efectiva del traslado.
- **Costo Residual de Destino**: Monto correspondiente al valor del servicio educativo que el estudiante deberá cubrir en el ciclo de destino desde la fecha efectiva de traslado hasta la finalización del ciclo.
- **Costo Administrativo**: Tasa fija de S/20 cobrada por concepto de gastos de procesamiento del traslado. Esta tasa se exonera automáticamente si el traslado ocurre durante la semana marketera, durante la primera semana académica del ciclo, o durante la primera semana de clases del propio estudiante (definida como los primeros 7 días calendario desde su fecha de matrícula; por ejemplo, si el ciclo inició el 01/06 y el estudiante se matriculó el 03/06, no se le cobrarán los S/20 si solicita el traslado hasta el 10/06 inclusive. Pasada esa fecha, se le cobrará el gasto administrativo).
- **Calendario Académico**: Calendario de lunes a viernes utilizado exclusivamente para definir la duración formal del ciclo, control de asistencias, notas y validaciones académicas.
- **Calendario Administrativo**: Calendario de jueves a miércoles utilizado de forma exclusiva para la determinación y el prorrateo financiero de las cuotas y saldos devengados.

## Art. 3 · Quality Standards

- **Precisión de cálculos financieros**: Los cálculos del saldo residual del ciclo origen y del costo residual del ciclo destino deben realizarse con precisión de dos decimales de sol (S/.), empleando aritmética decimal de punto fijo (`BigDecimal` o equivalente) para evitar errores de redondeo de punto flotante.
- **Trazabilidad**: Todo traslado debe registrar su ciclo de vida completo (fecha efectiva solicitada por el estudiante, marca de tiempo de la transacción, usuario del Helpdesk que procesa, ID del correo de solicitud, estados financieros origen/destino y estado de aceptación de saldo negativo).
- **Cobertura mínima de pruebas**: La lógica del motor de cálculo de prorrateo y los validadores de reglas de negocio de traslados deben tener una cobertura mínima de pruebas unitarias del 95%, abarcando todas las combinaciones de modalidades (contado/cuotas) y calendarios.
- **Consistencia de resultados**: Una simulación de traslado y su posterior ejecución física con los mismos datos de entrada deben arrojar idénticos resultados financieros sin margen de desviación.
- **Validación obligatoria de reglas críticas**: El sistema debe validar de manera automática y obligatoria la exoneración del costo administrativo de S/20 bajo las condiciones explícitas de semana marketera, primera semana académica del ciclo, o la primera semana de clases del estudiante (los primeros 7 días calendario tras su matrícula) antes de registrar el traslado.

## Art. 4 · Architecture Principles

- **Separación entre reglas de negocio y presentación**: La lógica de cálculo financiero (prorrateo, residuales, exoneraciones) debe estar desacoplada de la interfaz de usuario de Helpdesk o de los servicios de recepción de correo electrónico, implementándose en un núcleo de dominio puro.
- **Centralización del motor de cálculo**: Existirá un único componente encargado de resolver la matemática del traslado (`TrasladoCalculator`). Ninguna otra parte de la aplicación o módulo de presentación duplicará o simulará estas fórmulas.
- **Prohibición de duplicar fórmulas financieras**: Las reglas que determinan la equivalencia de cuotas ("partes" = 4 semanas académicas cobrables), la duración de ciclos, y el prorrateo de días en base al calendario administrativo (jueves a miércoles) deben definirse una única vez en el dominio financiero y ser reutilizadas en origen y destino.
- **Uso exclusivo de fuentes oficiales**: La programación académica, las tarifas de los ciclos y las fechas de los calendarios oficiales se obtendrán exclusivamente a partir de la ingesta del archivo Excel institucional. Queda estrictamente prohibido persistir o modificar de forma manual o ad-hoc estos parámetros dentro del flujo de traslados.

## Art. 5 · Spec-Driven Development Workflow

- **Flujo de Trabajo SDD**: El ciclo de vida de cualquier cambio en la funcionalidad del traslado debe cumplir la secuencia inalterable de: Especificación (`spec.md`) -> Plan de Implementación (`plan.md`) -> Casos de Prueba (`test-cases.md`) -> Tareas de Código (`tasks.md`) -> Implementación -> Verificación.
- **Defensa de Requisitos**: No se escribirá ninguna línea de código de producción que no responda a un criterio de aceptación previamente detallado y aprobado por los "Three Amigos" (Negocio/PO, Desarrollo/Tech Lead, Calidad/QA).
- **Pruebas como Especificación Activa**: Los casos de prueba y los criterios de aceptación gherkin definidos en `test-cases.md` y `spec.md` actúan como la especificación viva del sistema. Cualquier desviación del comportamiento esperado será tratada como un fallo crítico de calidad.

## Art. 6 · Financial & Governance Rules

- **Control de Versiones**: Cualquier modificación en el comportamiento financiero del traslado o sus reglas de prorrateo requiere un incremento de versión de la constitución según el estándar SemVer (Mayor para cambios incompatibles de políticas, Menor para nuevas modalidades o exoneraciones, Parche para aclaraciones o corrección de textos).
- **Inmutabilidad de Parámetros**: Los datos importados desde el Excel institucional (calendarios, costos y semanas) son inmutables para el sistema de traslados. No se construirán pantallas ni APIs que permitan la alteración discrecional de estos valores.
- **Auditoría Contable**: Toda ejecución de traslado debe emitir un registro contable y de auditoría de solo inserción (Append-Only) que no pueda ser alterado ni eliminado, garantizando la trazabilidad histórica ante cualquier revisión de Tesorería.

## Art. 7 · Boundaries

### ALWAYS DO

- Usar la fecha efectiva solicitada por el estudiante en su correo electrónico como el ancla temporal de todos los cálculos de prorrateo y cobro.
- Aplicar de manera automática y directa los saldos positivos excedentes del traslado como abono en las cuotas futuras del estudiante en el ciclo de destino.
- Generar un registro de auditoría inmutable e histórico por cada traslado aprobado o anulado, que contenga el detalle financiero completo del cálculo y el ID del correo origen.
- Utilizar el monto neto efectivamente pagado por el estudiante (incluyendo los descuentos reales aplicados en su historial de pagos) para el cálculo del saldo residual en origen, en lugar del precio de lista.
- Permitir la anulación completa del traslado únicamente a través de la relación explícita con un correo de anulación del estudiante, revirtiendo todos los movimientos de saldos a su estado original de manera atómica.

### ASK FIRST

- Solicitar autorización a la Dirección Académica si se requiere procesar un traslado para un estudiante que presenta deudas morosas previas no relacionadas con el ciclo de origen.
- Consultar con el área de Finanzas si se presenta una solicitud de traslado con saldo neto negativo donde el estudiante solicita una prórroga de pago o un compromiso de pago diferido para la diferencia.
- Validar con el Administrador de Programación Académica si el Excel institucional importado carece de marcas explícitas de "semana marketera" o si las fechas de inicio/fin de ciclo se superponen de forma anómala.

### NEVER DO

- Permitir la edición manual de las tarifas oficiales, fechas de ciclos o la exoneración discrecional de la tasa administrativa de S/20 fuera de las reglas automáticas establecidas.
- Confirmar o dar por ejecutado un traslado con saldo neto negativo en el sistema sin la confirmación verificada del pago de la diferencia por parte del estudiante.
- Eliminar o modificar registros históricos de traslados realizados o de solicitudes anuladas; toda transacción financiera y operativa debe ser de solo lectura una vez guardada.

***

**Version**: 1.1.0 | **Ratified**: 2026-06-16 | **Last Amended**: 2026-06-16
