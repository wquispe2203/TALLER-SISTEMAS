# constitution.md

## Art. 3 · Quality Standards

- **Precisión de cálculos financieros**: Los cálculos del saldo residual del ciclo origen y del costo residual del ciclo destino deben realizarse con precisión de dos decimales de sol (S/.), empleando aritmética decimal de punto fijo para evitar errores de redondeo de punto flotante.
- **Trazabilidad**: Todo traslado debe registrar su ciclo de vida completo (fecha efectiva solicitada por el estudiante, marca de tiempo de la transacción, usuario del Helpdesk que procesa, ID del correo de solicitud, estados financieros origen/destino y estado de aceptación de saldo negativo).
- **Cobertura mínima de pruebas**: La lógica del motor de cálculo de prorrateo y los validadores de reglas de negocio de traslados deben tener una cobertura mínima de pruebas del 95% para asegurar el correcto comportamiento ante calendarios académicos (lunes a viernes) y administrativos (jueves a miércoles).
- **Consistencia de resultados**: Una simulación de traslado y su posterior ejecución física con los mismos datos de entrada deben arrojar idénticos resultados financieros sin margen de desviación.
- **Validación obligatoria de reglas críticas**: El sistema debe validar de manera automática y obligatoria la exoneración del costo administrativo de S/20 bajo las condiciones explícitas de semana marketera o primera semana académica antes de registrar el traslado.

## Art. 4 · Architecture Principles

- **Separación entre reglas de negocio y presentación**: La lógica de cálculo financiero (prorrateo, residuales, exoneraciones) debe estar desacoplada de la interfaz de usuario de Helpdesk o de los servicios de recepción de correo electrónico, implementándose en un núcleo de dominio puro.
- **Centralización del motor de cálculo**: Existirá un único componente encargado de resolver la matemática del traslado (`TrasladoCalculator`). Ninguna otra parte de la aplicación o módulo de presentación duplicará o simulará estas fórmulas.
- **Prohibición de duplicar fórmulas financieras**: Las reglas que determinan la equivalencia de cuotas ("partes" = 4 semanas académicas cobrables), la duración de ciclos, y el prorrateo de días en base al calendario administrativo (jueves a miércoles) deben definirse una única vez en el dominio financiero y ser reutilizadas en origen y destino.
- **Uso exclusivo de fuentes oficiales**: La programación académica, las tarifas de los ciclos y las fechas de los calendarios oficiales se obtendrán exclusivamente a partir de la ingesta del archivo Excel institucional. Queda estrictamente prohibido persistir o modificar de forma manual o ad-hoc estos parámetros dentro del flujo de traslados.

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
