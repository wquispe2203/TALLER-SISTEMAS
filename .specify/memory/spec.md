# spec.md

# Resumen Ejecutivo

Se propone implementar una Calculadora de Montos de Traslado Académico para automatizar el cálculo actualmente realizado de forma manual por el área de TI utilizando un Excel oficial proporcionado por Gerencia. La solución permitirá determinar automáticamente si una solicitud de traslado genera saldo a favor, traslado cubierto o monto pendiente de pago, aplicando las reglas institucionales vigentes para modalidades al contado y en cuotas. El objetivo es reducir errores operativos, disminuir el tiempo de atención y estandarizar el proceso. Quedan pendientes definiciones relacionadas con la actualización de parámetros oficiales, el almacenamiento de resultados calculados y posibles restricciones institucionales adicionales para la ejecución de traslados.

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

Dado un traslado válido donde:

* Saldo disponible calculado = S/ 700
* Costo requerido del ciclo destino = S/ 500

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:

* Resultado: S/ 200 de saldo a favor
* Estado: "Saldo a favor"

### AC-1.2 (Traslado cubierto)

Dado un traslado válido donde:

* Saldo disponible calculado = S/ 500
* Costo requerido del ciclo destino = S/ 500

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:

* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### AC-1.3 (Monto pendiente)

Dado un traslado válido donde:

* Saldo disponible calculado = S/ 500
* Costo requerido del ciclo destino = S/ 800

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:

* Resultado: S/ 300 pendiente de pago
* Estado: "Monto pendiente por cancelar"

---

## US-2 (P1)

Como analista de soporte,

quiero que el sistema valide las reglas de negocio antes de ejecutar el cálculo,

para evitar resultados incorrectos.

### AC-2.0 (Validación en cascada)

Dado una solicitud de traslado,

Cuando el usuario inicia el cálculo,

Entonces el sistema debe validar en el siguiente orden y detenerse en el primer error encontrado:

1. Estado del estudiante
2. Existencia de ciclo origen y ciclo destino
3. Modalidad válida para el ciclo seleccionado
4. Fecha de traslado dentro del periodo académico
5. Monto pagado, descuentos y beneficios

### AC-2.1 (Fecha inválida)

Dado una fecha que no pertenece al periodo académico válido del ciclo origen o destino,

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"Fecha de traslado inválida para los ciclos seleccionados."

### AC-2.2 (Estado no permitido)

Dado un estado diferente de:

* MATRICULADO
* PAGADO

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"El estado actual no permite realizar traslados."

### AC-2.3 (Modalidad inexistente)

Dado que el ciclo seleccionado no posee la modalidad indicada,

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"La modalidad seleccionada no existe para el ciclo indicado."

## US-3 (P2)

Como analista de soporte,

quiero que el sistema muestre el desglose de las operaciones realizadas para obtener el resultado,

para poder analizar y validar cómo se llegó al monto final.

### AC-3.1 (Mostrar desglose completo)

Dado un traslado válido,

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra además del resultado final:

* Semanas totales del ciclo origen
* Semanas transcurridas a la fecha de traslado
* Semanas restantes
* Fórmula y resultado del saldo disponible
* Fórmula y resultado del costo del ciclo destino
* Operación final y resultado

### AC-3.2 (Visibilidad de beneficios y descuentos aplicados)

Dado un cálculo de traslado donde el estudiante tiene un descuento o beneficio activo,

Cuando el sistema genera el desglose de las operaciones,

Entonces el sistema debe incluir explícitamente en el detalle:

* El porcentaje o tipo de descuento/beneficio aplicado.
* La tarifa regular versus la tarifa con el beneficio aplicado utilizada para calcular el saldo disponible del ciclo origen.
* La aclaración de que el ciclo destino se está cobrando con tarifa regular.

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

* Fecha de traslado (formato DD/MM/YYYY)
* Ciclo origen (ciclo donde está matriculado actualmente)
* Ciclo destino (ciclo al que desea trasladarse)
* Modalidad (Presencial o Virtual)
* Estado del estudiante
* Monto pagado (valor numérico en soles, mayor a 0)
* Descuentos (opcional, Ninguno por defecto)
* Beneficios (opcional, Ninguno por defecto)

### FR-002 Estados permitidos

El sistema MUST aceptar únicamente los siguientes estados:

* MATRICULADO
* PAGADO

El sistema MUST bloquear el cálculo para los siguientes estados:

* SUSPENDIDO
* RETIRADO

### FR-003 Modalidades disponibles

El sistema MUST aceptar únicamente las siguientes modalidades:

* Presencial
* Virtual

### FR-004 Descuentos aplicables

El sistema MUST reconocer los siguientes tipos de descuento:

* 15% (descuento estándar)
* Descuento familiar
* Ninguno (valor por defecto cuando no aplica)

Regla: el descuento aplica únicamente al saldo disponible 
del ciclo origen. El ciclo destino siempre usa tarifa regular.

### FR-005 Beneficios aplicables

El sistema MUST reconocer los siguientes beneficios:

* 1/2 beca (50% de descuento sobre la tarifa)
* 1/4 beca (25% de descuento sobre la tarifa)
* Ninguno (valor por defecto cuando no aplica)

Regla: el beneficio aplica únicamente al saldo disponible 
del ciclo origen. El ciclo destino siempre usa tarifa regular.

### FR-006 Desglose de operaciones

El sistema MUST mostrar junto al resultado final el desglose 
de las operaciones matemáticas realizadas, incluyendo:

* Semanas totales del ciclo origen
* Semanas transcurridas a la fecha de traslado
* Semanas restantes
* Fórmula y resultado del saldo disponible
* Fórmula y resultado del costo del ciclo destino
* Operación final y resultado

### FR-007 Validación prioritaria en cascada

El sistema MUST aplicar las validaciones en orden de criticidad y detener el proceso ante el primer error válido encontrado.

El orden de validación será:

1. Estado del estudiante
2. Ciclo origen y ciclo destino válidos
3. Modalidad disponible para el ciclo
4. Fecha dentro del periodo académico
5. Monto pagado, descuentos y beneficios

# 4. Requisitos No Funcionales (NFR)

### NFR-1

El cálculo deberá completarse en menos de 200 milisegundos desde el envío de los datos.

---

# 5. Casos Borde

### CB-1 Fecha fuera del rango académico

Resultado esperado:

El sistema bloquea el cálculo e informa que la fecha de traslado es inválida.

### CB-2 Ciclo origen igual a ciclo destino

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### CB-3 Modalidad inexistente para el ciclo seleccionado

Resultado esperado:

El sistema bloquea el cálculo e informa que la modalidad no existe para el ciclo seleccionado.

### CB-4 Estado SUSPENDIDO

Resultado esperado:

El sistema bloquea el cálculo e informa que el estado no permite realizar traslados.

### CB-5 Estado RETIRADO

Resultado esperado:

El sistema bloquea el cálculo e informa que el estado no permite realizar traslados.

### CB-6 Resultado exactamente igual a cero

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### CB-7 Traslado durante la última semana académica

Resultado esperado:

El sistema calcula el resultado utilizando únicamente las semanas académicas restantes disponibles según las reglas vigentes.

### CB-8 Estudiante con descuento activo

Resultado esperado:

El sistema utiliza el monto con descuento para calcular el saldo disponible del ciclo origen y elimina el descuento para calcular el costo del ciclo destino.

### CB-9 Estudiante con beca o beneficio activo

Resultado esperado:

El sistema utiliza el beneficio vigente únicamente para determinar el saldo disponible del ciclo origen y calcula el ciclo destino utilizando la tarifa regular sin beneficios.

---

# 6. Assumptions

### A-1

Asumimos que el Excel oficial proporcionado por Gerencia contiene información correcta y actualizada.

Si esta información es incorrecta, los resultados calculados serán inválidos.

### A-2

Asumimos que las fechas académicas necesarias para determinar semanas restantes se encuentran disponibles en la fuente oficial.

Si estas fechas no existen o son incorrectas, el sistema no podrá calcular correctamente los saldos.

### A-3

Asumimos que los descuentos y beneficios vigentes son conocidos antes de iniciar el cálculo.

Si esta información es incorrecta o incompleta, el resultado económico será incorrecto.

### A-4

Asumimos que únicamente los estados MATRICULADO y PAGADO permiten realizar traslados.

Si esta regla cambia, será necesario actualizar las validaciones de negocio.

---

# 7. Decisiones de implementación adoptadas

### D-1

Los parámetros oficiales se actualizarán mediante un archivo JSON estático generado a partir del Excel aprobado por Gerencia. En esta primera versión, la actualización será manual y se realizará por el área responsable cuando exista una nueva versión oficial.

### D-2

La solución permitirá calcular traslados únicamente cuando la fecha de traslado se encuentre dentro del periodo académico vigente definido en los parámetros oficiales. Si la fecha está fuera de rango, el sistema bloqueará el cálculo y mostrará el mensaje correspondiente.

### D-3

Los resultados se mostrarán en pantalla y podrán copiarse para soporte, pero no se almacenarán en una base de datos en esta versión. El objetivo es ofrecer una herramienta operativa rápida y sencilla para el analista.

### D-4

La solución será una aplicación web simple. La interfaz se implementará en HTML y CSS, mientras que la lógica de negocio se expondrá a través de un backend en Node.js con un endpoint para recibir los datos de traslado y devolver el resultado, el estado y el desglose del cálculo.

---

# 8. Scope

## DENTRO

* Cálculo automático de montos de traslado.
* Cálculo para modalidad al contado.
* Cálculo para modalidad en cuotas.
* Validación de fechas académicas.
* Validación de estados de matrícula.
* Validación de modalidades disponibles.
* Determinación de saldo a favor.
* Determinación de traslado cubierto.
* Determinación de monto pendiente.
* Aplicación de reglas de descuentos y beneficios.

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

```
```
