# spec.md

## Resumen

El proceso de traslado de estudiantes entre ciclos académicos de Vonex permite reubicar a un estudiante que solicita formalmente su cambio a través del correo `helpdesk@vonex.edu.pe`. Para calcular y ejecutar este traslado, se procesa la información de programación académica proveniente de un Excel institucional oficial, determinando el saldo residual del ciclo de origen, el costo residual del ciclo de destino y la aplicación de los costos administrativos correspondientes. El resultado de este cálculo financiero (saldo positivo, exacto o negativo) define las acciones a seguir y requiere una estricta trazabilidad de auditoría.

## Objetivo

Permitir que el personal de Helpdesk calcule, apruebe, ejecute y registre traslados entre ciclos académicos respetando las reglas financieras y de calendario institucional de Vonex, garantizando exactitud financiera y la trazabilidad de cada estado en el ciclo de vida del traslado.

## Alcance

Esta especificación detalla las reglas de cálculo de residuales, la aplicación de prorrateos, los calendarios correspondientes, y las siguientes dos historias de usuario:
* **US-1: Calcular traslado**: Registro de la fecha efectiva de solicitud, cálculo de saldo residual origen, costo residual destino, costo administrativo y determinación del resultado financiero.
* **US-2: Ejecutar y registrar traslado**: Confirmación de la ejecución del traslado, registro inmutable de auditoría y la capacidad de anulación a solicitud posterior del estudiante.

## User Stories

### US-1: Calcular traslado
**Como** agente de Helpdesk,
**quiero** calcular el saldo residual del estudiante y el costo del ciclo destino,
**para** determinar si el traslado puede realizarse y conocer el resultado financiero correspondiente.

### US-2: Ejecutar y registrar traslado
**Como** agente de Helpdesk,
**quiero** ejecutar, registrar y eventualmente anular un traslado aprobado,
**para** mantener trazabilidad y control institucional del proceso.

## Reglas de negocio

* **RN-01 Fecha efectiva**: El cálculo del traslado debe realizarse utilizando exclusivamente la fecha efectiva de traslado indicada por el estudiante en su solicitud de correo. No se debe emplear la fecha del correo, de aprobación ni de ejecución.
* **RN-02 Compatibilidad**: Cualquier ciclo académico es compatible con cualquier otro ciclo de destino. No existen restricciones por carrera, programa, modalidad o universidad de origen/destino.
* **RN-03 Modalidades**: La modalidad de pago registrada como "partes" equivale a la modalidad "cuotas".
* **RN-04 Modalidad contado**: 
  - Se calcula a partir del monto efectivamente pagado por el estudiante (respetando los descuentos aplicados al pago al contado).
  - La semana marketera consume valor dentro del prorrateo en modalidad contado.
  - *Fórmula*: `Saldo residual = Monto pagado contado ÷ semanas totales del ciclo × semanas restantes`
* **RN-05 Modalidad cuotas**: Cada cuota cobrable equivale a un periodo de 4 semanas académicas.
* **RN-06 Calendario académico**: Define la duración académica del ciclo, semanas consumidas y validaciones académicas. Se rige de lunes a viernes (5 días laborables).
* **RN-07 Calendario administrativo**: Utilizado de manera exclusiva para el cálculo de prorrateo. Se rige de jueves a miércoles (7 días calendario). Los cambios de porcentaje/avances administrativos para prorrateo ocurren los días jueves.
* **RN-08 Prorrateo sin semana marketera**: En ciclos que no contemplen semana marketera, el descuento por avance administrativo se aplica de forma regular a lo largo del tiempo.
* **RN-09 Prorrateo con semana marketera**: En ciclos con modalidad cuotas que incluyan semana marketera:
  - La semana marketera no descuenta valor.
  - El estudiante conserva el valor completo de la cuota hasta el miércoles de la segunda semana administrativa.
  - A partir del jueves de la segunda semana administrativa inicia el prorrateo de forma regular.
* **RN-10 Resultado financiero**: Se obtiene mediante la ecuación:
  `Resultado = Saldo residual origen − costo residual destino − costo administrativo`
* **RN-11 Saldo positivo**: Si el resultado financiero es mayor a cero, el traslado se considera cubierto y el excedente se abonará automáticamente como saldo a favor en futuras cuotas del estudiante en el ciclo de destino.
* **RN-12 Saldo exacto**: Si el resultado financiero es igual a cero, el traslado se considera completamente cubierto sin saldo pendiente ni excedentes.
* **RN-13 Saldo negativo**: Si el resultado financiero es menor a cero, se genera una deuda. El estudiante debe decidir si pagar la diferencia. Si acepta pagar, el traslado procede; si la rechaza, el traslado no debe ejecutarse.
* **RN-14 Costo administrativo**: Todo proceso de traslado tiene un cargo administrativo estipulado de S/20.
* **RN-15 Exoneración**: El costo administrativo de S/20 no se cobrará (S/0) si la fecha efectiva del traslado coincide con:
  - La semana marketera del ciclo de destino.
  - La primera semana académica del ciclo de destino.
* **RN-16 Anulación**: Un traslado previamente ejecutado podrá anularse únicamente cuando el estudiante responda de forma posterior al hilo de correo solicitando dicha anulación. El sistema revertirá los saldos y registrará el evento.
* **RN-17 Auditoría**: Cada registro de ejecución o anulación debe almacenar los siguientes datos:
  - Estudiante (ID/Nombre)
  - Correo del solicitante
  - Fecha de solicitud
  - Fecha efectiva
  - Ciclo origen y ciclo destino
  - Modalidad origen y modalidad destino
  - Saldo origen calculado
  - Costo destino calculado
  - Costo administrativo aplicado o exonerado
  - Diferencia final (Resultado financiero)
  - Decisión del estudiante frente a la deuda (Acepta pagar / Rechaza)
  - Usuario de Helpdesk que operó el registro
  - Observaciones
  - Fecha y hora del registro de auditoría
  - Estado final del traslado (Simulado, Ejecutado, Anulado, Rechazado)

## Criterios de aceptación

### Cálculo con saldo positivo
```gherkin
Dado que un estudiante solicita un traslado con modalidad contado
Y su saldo residual de origen es S/500
Y el costo residual del ciclo destino es S/400
Y aplica un costo administrativo de S/20
Cuando el sistema realiza el cálculo del traslado
Entonces el resultado financiero determinado es S/80 a favor (Saldo positivo)
Y el sistema registra que el excedente se aplicará automáticamente a futuras cuotas del ciclo destino.
```

### Cálculo con saldo exacto
```gherkin
Dado que un estudiante solicita un traslado
Y su saldo residual de origen es S/420
Y el costo residual del ciclo destino es S/400
Y aplica un costo administrativo de S/20
Cuando el sistema realiza el cálculo del traslado
Entonces el resultado financiero determinado es S/0 (Saldo exacto)
Y el traslado se marca como completamente cubierto.
```

### Cálculo con saldo negativo
```gherkin
Dado que un estudiante solicita un traslado
Y su saldo residual de origen es S/300
Y el costo residual del ciclo destino es S/400
Y aplica un costo administrativo de S/20
Cuando el sistema realiza el cálculo del traslado
Entonces el resultado financiero determinado es -S/120 (Saldo negativo)
Y el sistema requiere la confirmación de la decisión del estudiante ante la deuda para proceder.
```

### Aceptación de deuda
```gherkin
Dado que el cálculo del traslado del estudiante arroja un saldo negativo de -S/120
Cuando el estudiante confirma por correo que acepta pagar la diferencia
Entonces el agente de Helpdesk puede proceder con la ejecución del traslado en el sistema.
```

### Rechazo de deuda
```gherkin
Dado que el cálculo del traslado del estudiante arroja un saldo negativo de -S/120
Cuando el estudiante rechaza pagar la diferencia o no brinda respuesta
Entonces el agente de Helpdesk registra el rechazo y el traslado queda cancelado y no se ejecuta.
```

### Traslado exonerado
```gherkin
Dado que un estudiante solicita un traslado con una fecha efectiva que cae dentro de la primera semana académica del ciclo de destino
Cuando el sistema calcula los costos del traslado
Entonces el costo administrativo se calcula como S/0 (Exonerado).
```

### Traslado con costo administrativo
```gherkin
Dado que un estudiante solicita un traslado con una fecha efectiva posterior a la primera semana académica y fuera de la semana marketera del ciclo de destino
Cuando el sistema calcula los costos del traslado
Entonces el costo administrativo se establece en S/20.
```

### Modalidad contado
```gherkin
Dado que un estudiante pagó S/1200 al contado en un ciclo de origen de 12 semanas totales
Y solicita traslado con fecha efectiva que deja 6 semanas restantes en el ciclo
Cuando el sistema aplica la fórmula de modalidad contado
Entonces el saldo residual de origen se calcula exactamente en S/600.
```

### Modalidad cuotas
```gherkin
Dado que un ciclo de origen en cuotas posee cuotas donde cada una representa 4 semanas académicas cobrables (28 días administrativos)
Cuando el sistema calcula el prorrateo de una cuota en curso
Entonces el avance se computa en base a las semanas consumidas y restantes según el calendario de jueves a miércoles.
```

### Semana marketera (Modalidad Cuotas con Semana Marketera)
```gherkin
Dado que un estudiante se traslada desde un ciclo con cuotas y semana marketera
Y la fecha efectiva se encuentra entre el inicio del ciclo y el miércoles de la segunda semana administrativa
Cuando el sistema evalúa el prorrateo de la cuota en curso
Entonces el estudiante conserva el 100% del valor de la cuota sin ningún descuento por avance administrativo.
```

### Ejecución del traslado
```gherkin
Dado que un cálculo de traslado ha sido revisado por Helpdesk
Y cumple con las condiciones financieras de aprobación (saldo positivo, exacto, o negativo aceptado y pagado)
Cuando el agente de Helpdesk confirma la ejecución del traslado
Entonces el estudiante es asignado al ciclo destino
Y el saldo/excedente es aplicado al ciclo destino
Y el estado del traslado cambia a "Ejecutado".
```

### Anulación del traslado
```gherkin
Dado que un traslado fue previamente ejecutado y registrado en el sistema con estado "Ejecutado"
Cuando el estudiante solicita la anulación vía correo electrónico y el agente de Helpdesk ejecuta la acción de anular
Entonces el sistema revierte todos los movimientos financieros del traslado
And el estado del traslado cambia a "Anulado" en el registro histórico.
```

### Registro de auditoría
```gherkin
Dado que se ejecuta o anula un traslado de estudiantes
Cuando la transacción se completa con éxito
Entonces el sistema guarda de forma inmutable un registro en la tabla de auditoría con la fecha y hora, ID del estudiante, correos de respaldo, montos exactos calculados, usuario de Helpdesk que operó y el estado final del proceso.
```

## Fuera de alcance

* Integración automática o sincronización directa con bandejas de entrada de correo electrónico (los correos se revisan y registran manualmente por Helpdesk).
* Procesamiento de pagos, pasarelas de pago online o validación bancaria de transacciones.
* Devoluciones de dinero físico o transferencias bancarias a estudiantes en caso de saldos a favor excedentes (el saldo se aplica únicamente a futuras cuotas).
* Sincronización en tiempo real o lectura directa automatizada del archivo Excel institucional de programación académica (el archivo se asume importado o cargado previamente en el sistema).
* Envío automatizado de correos de notificación de resultados a los estudiantes.
