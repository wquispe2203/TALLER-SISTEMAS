# Casos de Prueba (Test Cases)

Este documento contiene los casos de prueba derivados de las Historias de Usuario (US) y los Casos Borde (CB) definidos en el documento `spec.md`.

## Historia de Usuario 1 (US-1) - Cálculo de Montos

### TC-1 (AC-1.1, Caso Saldo a favor)
**Datos:**
* Saldo disponible calculado: S/ 700
* Costo requerido del ciclo destino: S/ 500
* Traslado: Válido

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 200 de saldo a favor
* Estado: "Saldo a favor"

### TC-2 (AC-1.2, Caso Traslado cubierto)
**Datos:**
* Saldo disponible calculado: S/ 500
* Costo requerido del ciclo destino: S/ 500
* Traslado: Válido

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### TC-3 (AC-1.3, Caso Monto pendiente)
**Datos:**
* Saldo disponible calculado: S/ 500
* Costo requerido del ciclo destino: S/ 800
* Traslado: Válido

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 300 pendiente de pago
* Estado: "Monto pendiente por cancelar"

---

## Historia de Usuario 2 (US-2) - Validación de Reglas

### TC-4 (AC-2.0, Validación en cascada)
**Datos:**
* Solicitud de traslado incompleta o inválida.

**Pasos:**
1. Ingresar los datos.
2. Iniciar el cálculo.

**Esperado:**
El sistema debe validar en el siguiente orden y detenerse en el primer error encontrado:
1. Estado del estudiante
2. Existencia de ciclo origen y ciclo destino
3. Modalidad válida para el ciclo seleccionado
4. Fecha de traslado dentro del periodo académico
5. Monto pagado, descuentos y beneficios

### TC-5 (AC-2.1, Caso Error - Fecha Inválida)
**Datos:**
* Estado: MATRICULADO
* Fecha de traslado: 25/12/2026 (No pertenece al periodo académico válido)
* Ciclo origen: C01
* Ciclo destino: C02

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema bloquea la operación y muestra:
"Fecha de traslado inválida para los ciclos seleccionados."

### TC-6 (AC-2.2, Caso Error - Estado no permitido)
**Datos:**
* Estado: SUSPENDIDO o RETIRADO

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema bloquea la operación y muestra:
"El estado actual no permite realizar traslados."

### TC-7 (AC-2.3, Caso Error - Modalidad inexistente)
**Datos:**
* Modalidad: Virtual (pero el ciclo seleccionado no posee dicha modalidad)

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema bloquea la operación y muestra:
"La modalidad seleccionada no existe para el ciclo indicado."

---

## Historia de Usuario 3 (US-3) - Desglose de Operaciones

### TC-8 (AC-3.1, Mostrar desglose completo)
**Datos:**
* Traslado: Válido

**Pasos:**
1. Ingresar los datos.
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
* Traslado: Válido
* Estudiante tiene descuento o beca activa

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema incluye explícitamente en el desglose:
* El porcentaje o tipo de descuento/beneficio aplicado.
* La tarifa regular vs tarifa con beneficio usada para calcular saldo disponible.
* La aclaración de que el ciclo destino usa tarifa regular.

### TC-10 (AC-3.3, Exportación o copia rápida)
**Datos:**
* Cálculo ejecutado exitosamente.

**Pasos:**
1. Visualizar resultados.
2. Hacer clic en el botón "Copiar resumen".

**Esperado:**
El sistema copia todo el desglose en formato texto plano estructurado al portapapeles del usuario, dejándolo listo para pegar.

---

## Historia de Usuario 4 (US-4) - Visualización de Resultados

### TC-11 (AC-4.1, Mostrar saldos iniciales)
**Datos:**
* Cálculo de traslado ejecutado.
* Saldo a favor calculado: S/ 324.00
* Costo de ciclo destino: S/ 1347.00

**Pasos:**
1. Ejecutar el cálculo.
2. Observar la sección "Resultado de la Simulación".

**Esperado:**
El sistema muestra los montos claramente con su respectiva modalidad:
* "Saldo a favor: S/ 324.00 (Valor al Contado)"
* "Monto a cancelar: S/ 1347.00 (Valor al Contado)"

### TC-12 (AC-4.2, Mensaje conclusivo de saldo insuficiente/faltante)
**Datos:**
* Saldo a favor: S/ 324.00
* Costo destino: S/ 1347.00
* Faltante: S/ 1023.00

**Pasos:**
1. Ejecutar el cálculo.
2. Observar la sección de resultados.

**Esperado:**
Aparece una alerta destacada en rojo con el texto exacto:
"El saldo a favor del ciclo anterior no cubre el costo del nuevo ciclo. Faltan: S/ 1023.00"

### TC-13 (AC-4.3, Nota sobre cobro adicional de traslado)
**Datos:**
* Cálculo ejecutado correctamente.

**Pasos:**
1. Observar la parte inferior de la tarjeta de resultados.

**Esperado:**
Aparece el texto informativo en tamaño menor:
"* Recordar que se añade los S/ 20 por proceso de traslado si ya pasó una semana académica después de su fecha de matrícula."

---

## Casos Borde (CB)

### TC-14 (CB-2, Ciclo origen igual a ciclo destino)
**Datos:**
* Ciclo origen: C01
* Ciclo destino: C01

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema muestra:
* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### TC-15 (CB-7, Última Semana Académica)
**Datos:**
* Ciclo origen: C01
* Fecha de traslado: 15/07/2026
* Total de semanas del ciclo: 16
* Semana actual: 16
* Semanas restantes: 1
* Modalidad: Contado
* Monto del ciclo: S/ 800

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema calcula:
* Saldo disponible = (800 / 16) × 1 = S/ 50
El resultado mostrado utiliza únicamente la última semana académica disponible.

### TC-16 (CB-8, Descuento Activo)
**Datos:**
* Descuento vigente: 20%
* Monto cuota origen: S/ 400
* Monto con descuento: S/ 320
* Costo requerido ciclo destino: S/ 400

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema calcula:
* Saldo disponible = S/ 320
* Costo destino = S/ 400
* Resultado = S/ 80 pendiente
El sistema muestra:
* Resultado: S/ 80 pendiente
* Estado: "Monto pendiente por cancelar"

### TC-17 (CB-9, Beca Activa)
**Datos:**
* Beca vigente: 25%
* Tarifa regular ciclo origen: S/ 1000
* Saldo disponible calculado: S/ 750
* Tarifa regular ciclo destino: S/ 1000

**Pasos:**
1. Ingresar los datos.
2. Ejecutar el cálculo.

**Esperado:**
El sistema calcula:
* Saldo disponible = S/ 750
* Costo destino = S/ 1000
* Resultado = S/ 250 pendiente
El sistema muestra:
* Resultado: S/ 250 pendiente
* Estado: "Monto pendiente por cancelar"
Además, el cálculo utiliza tarifa regular para el ciclo destino, sin aplicar la beca previamente existente.
