# Resumen Ejecutivo

Este documento define la suite de 16 casos de prueba (Test Cases) diseñados para validar la Calculadora de Montos de Traslado Académico. El alcance comprende la verificación de escenarios de éxito ("camino feliz"), validaciones en cascada del estado y condiciones de pago, desglose matemático de operaciones y el comportamiento ante casos borde definidos en `spec.md`. El objetivo es asegurar que la lógica de cálculo y sus restricciones operen de forma correcta según las reglas institucionales vigentes.

# Casos de Prueba (Test Cases)

Este documento contiene los casos de prueba derivados de las Historias de Usuario (US) y los Casos Borde (CB) definidos en el documento `spec.md`.

## Historia de Usuario 1 (US-1) - Cálculo de Montos

### TC-1 (AC-1.1, Caso Saldo a favor)
**Datos:**
* Datos de entrada de un estudiante cuyo saldo disponible parametrizado (S/ 700) supera al costo del ciclo destino (S/ 500).
* Condición de Pago: Contado.
* Estado: MATRICULADO.

**Pasos:**
1. Ingresar en el formulario: Ciclo origen, Ciclo destino, Fecha de traslado, Condición de pago, Estado del estudiante y Monto pagado.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 200 de saldo a favor
* Estado: "Saldo a favor"

### TC-2 (AC-1.2, Caso Traslado cubierto)
**Datos:**
* Datos de entrada de un estudiante cuyo saldo disponible parametrizado (S/ 500) es igual al costo del ciclo destino (S/ 500).
* Condición de Pago: Contado.
* Estado: MATRICULADO.

**Pasos:**
1. Ingresar en el formulario: Ciclo origen, Ciclo destino, Fecha de traslado, Condición de pago, Estado del estudiante y Monto pagado.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### TC-3 (AC-1.3, Caso Monto pendiente)
**Datos:**
* Datos de entrada de un estudiante cuyo saldo disponible parametrizado (S/ 500) es menor al costo del ciclo destino (S/ 800).
* Condición de Pago: Contado.
* Estado: MATRICULADO.

**Pasos:**
1. Ingresar en el formulario: Ciclo origen, Ciclo destino, Fecha de traslado, Condición de pago, Estado del estudiante y Monto pagado.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 300 pendiente de pago
* Estado: "Monto pendiente por cancelar"

---

## Historia de Usuario 2 (US-2) - Validación de Reglas

### TC-4 (AC-2.0, Validación en cascada)
**Datos:**
* Estado del estudiante: SUSPENDIDO (Inválido, regla 1)
* Ciclo origen: C01
* Ciclo destino: C02
* Condición de Pago: Cuotas
* Fecha de traslado: 25/12/2026 (Fuera de rango académico, regla 4)
* Monto pagado: S/ 500

**Pasos:**
1. Ingresar en el formulario los datos anteriores del estudiante.
2. Ejecutar el cálculo.

**Esperado:**
El sistema bloquea la operación y se detiene en el primer error encontrado (Estado del estudiante), mostrando:
"El estado actual no permite realizar traslados."

### TC-5 (AC-2.1, Caso Error - Fecha Inválida)
**Datos:**
* Estado del estudiante: MATRICULADO
* Fecha de traslado: 25/12/2026 (No pertenece al periodo académico válido)
* Ciclo origen: C01
* Ciclo destino: C02
* Condición de Pago: Contado

**Pasos:**
1. Ingresar en el formulario los datos anteriores del estudiante.
2. Ejecutar el cálculo.

**Esperado:**
El sistema bloquea la operación y muestra:
"Fecha de traslado inválida para los ciclos seleccionados."

### TC-6 (AC-2.2, Caso Error - Estado no permitido)
**Datos:**
* Estado del estudiante: SUSPENDIDO o RETIRADO
* Ciclo origen: C01
* Ciclo destino: C02
* Condición de Pago: Contado
* Fecha de traslado: 15/05/2026 (Fecha válida)

**Pasos:**
1. Ingresar en el formulario los datos anteriores del estudiante.
2. Ejecutar el cálculo.

**Esperado:**
El sistema bloquea la operación y muestra:
"El estado actual no permite realizar traslados."

### TC-7 (AC-2.3, Caso Error - Modalidad inexistente)
**Datos:**
* Ciclo origen: C01 (el cual solo ofrece condición de pago "Contado")
* Condición de Pago: Cuotas (No existente para el ciclo origen)
* Estado del estudiante: MATRICULADO
* Fecha de traslado: 15/05/2026

**Pasos:**
1. Ingresar en el formulario los datos anteriores del estudiante.
2. Ejecutar el cálculo.

**Esperado:**
El sistema bloquea la operación y muestra:
"La modalidad seleccionada no existe para el ciclo indicado."

---

## Historia de Usuario 3 (US-3) - Desglose de Operaciones

### TC-8 (AC-3.1, Mostrar desglose completo)
**Datos:**
* Ciclo origen: C01
* Ciclo destino: C02
* Fecha de traslado: 15/05/2026
* Condición de Pago: Contado
* Estado: MATRICULADO
* Monto pagado: S/ 2000

**Pasos:**
1. Ingresar en el formulario los datos del traslado.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra, además del resultado final, el siguiente desglose:
* Semanas totales del ciclo origen
* Semanas transcurridas a la fecha de traslado
* Semanas restantes
* Fórmula y resultado del saldo disponible
* Fórmula y resultado del costo del ciclo destino
* Operación final y resultado

### TC-9 (AC-3.2, Visibilidad de beneficios y descuentos aplicados)
**Datos:**
* Ciclo origen: C01
* Ciclo destino: C02
* Fecha de traslado: 15/05/2026
* Condición de Pago: Contado
* Estado: MATRICULADO
* Beneficio: 1/4 beca (25%)
* Monto pagado en origen: S/ 750 (Tarifa con beneficio aplicado)

**Pasos:**
1. Seleccionar el beneficio "1/4 beca" e ingresar los datos del traslado en el formulario.
2. Ejecutar el cálculo haciendo clic en el botón correspondiente.

**Esperado:**
El sistema incluye explícitamente en el desglose:
* El porcentaje o tipo de descuento/beneficio aplicado.
* La tarifa regular vs tarifa con beneficio usada para calcular el saldo disponible.
* La aclaración de que el ciclo destino usa tarifa regular.

### TC-10 (AC-3.3, Exportación o copia rápida)
**Datos:**
* Simulación de traslado del caso TC-8 ejecutada con éxito.

**Pasos:**
1. Visualizar los resultados de la simulación de TC-8.
2. Hacer clic en el botón "Copiar resumen".

**Esperado:**
El sistema copia todo el desglose en formato texto plano estructurado al portapapeles del usuario, dejándolo listo para pegar.

---

## Historia de Usuario 4 (US-4) - Visualización de Resultados

### TC-11 (AC-4.1, Mostrar saldos iniciales)
**Datos:**
* Simulación ejecutada (cuyos montos resultantes corresponden a S/ 324.00 de saldo a favor y S/ 1347.00 de costo destino).
* Condición de Pago: Contado.

**Pasos:**
1. Ejecutar el cálculo.
2. Observar la sección "Resultado de la Simulación".

**Esperado:**
El sistema muestra los montos claramente con su respectiva modalidad:
* "Saldo a favor: S/ 324.00 (Valor al Contado)"
* "Monto a cancelar: S/ 1347.00 (Valor al Contado)"

### TC-12 (AC-4.2, Mensaje conclusivo de saldo insuficiente/faltante)
**Datos:**
* Simulación ejecutada (cuyos montos resultantes corresponden a S/ 324.00 de saldo a favor y S/ 1347.00 de costo destino, generando una diferencia de S/ 1023.00).

**Pasos:**
1. Ejecutar el cálculo.
2. Observar la sección de resultados.

**Esperado:**
Aparece una alerta destacada en rojo con el texto exacto:
"El saldo a favor del ciclo anterior no cubre el costo del nuevo ciclo. Faltan: S/ 1023.00"

---

## Casos Borde (CB)

### TC-13 (CB-2, Ciclo origen igual a ciclo destino)
**Datos:**
* Ciclo origen: C01
* Ciclo destino: C01
* Condición de Pago: Contado

**Pasos:**
1. Seleccionar el mismo ciclo "C01" tanto para el origen como para el destino en el formulario.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### TC-14 (CB-7, Última Semana Académica)
**Datos:**
* Ciclo origen: C01
* Fecha de traslado: 15/07/2026 (Semana 16 de 16)
* Condición de Pago: Contado

**Pasos:**
1. Ingresar una fecha correspondiente a la última semana académica, seleccionando el ciclo origen "C01" y Condición de Pago "Contado".
2. Ejecutar el cálculo.

**Esperado:**
El sistema calcula el resultado utilizando únicamente las semanas académicas restantes disponibles (semana 16).

### TC-15 (CB-8, Descuento Activo)
**Datos:**
* Ciclo origen: C01
* Ciclo destino: C02
* Descuento vigente: 20%
* Condición de Pago: Cuotas

**Pasos:**
1. Ingresar el descuento del 20% y completar el formulario con el ciclo origen C01 y destino C02 en modalidad "Cuotas".
2. Ejecutar el cálculo.

**Esperado:**
El sistema utiliza el monto con descuento para calcular el saldo disponible del ciclo origen y elimina el descuento para calcular el costo del ciclo destino (tarifa regular).

### TC-16 (CB-9, Beca Activa)
**Datos:**
* Ciclo origen: C01
* Ciclo destino: C02
* Beneficio vigente: 25% (Beca)
* Condición de Pago: Contado

**Pasos:**
1. Ingresar el beneficio de beca del 25% y completar el formulario con el ciclo origen C01 y destino C02 en modalidad "Contado".
2. Ejecutar el cálculo.

**Esperado:**
El sistema utiliza el beneficio vigente únicamente para determinar el saldo disponible del ciclo origen y calcula el costo del ciclo destino utilizando la tarifa regular sin beneficios.
