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

---

## Historia de Usuario 4 (US-4) - Actualización de Tarifario

### TC-9 (AC-4.1, Visualización en la interfaz principal)
**Datos:**
* Sistema accesible.
* Tarifario vigente cargado.

**Pasos:**
1. Acceder a la pantalla de la calculadora de traslados.
2. Esperar a que la interfaz se cargue completamente.

**Esperado:**
El sistema muestra en un lugar visible (cabecera o pie de página) un indicador con la fecha de última actualización y versión del tarifario activo. Ejemplo: "Tarifario vigente: Actualizado al DD/MM/YYYY - v1.2"

### TC-10 (AC-4.2, Alerta por parámetros vencidos/sin conexión)
**Datos:**
* Sistema no puede cargar el archivo de parámetros oficial o la fecha excede vigencia.

**Pasos:**
1. Ingresar a la pantalla de cálculo.

**Esperado:**
El sistema bloquea los campos de entrada, deshabilita el botón de cálculo y muestra un mensaje de advertencia destacado:
"Advertencia: No se pudo verificar la vigencia de los parámetros oficiales. Por seguridad, la calculadora ha sido deshabilitada."

### TC-11 (AC-4.3, Trazabilidad en el desglose de resultados)
**Datos:**
* Cálculo ejecutado con éxito.

**Pasos:**
1. Ejecutar el cálculo.
2. Revisar el desglose detallado de las operaciones matemáticas.

**Esperado:**
El sistema incluye en el desglose y en el reporte final un campo con la versión y fecha del tarifario utilizado para asegurar la validez del cálculo.

---

## Casos Borde (CB)

### TC-12 (CB-2, Ciclo origen igual a ciclo destino)
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

### TC-13 (CB-7, Última Semana Académica)
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

### TC-14 (CB-8, Descuento Activo)
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

### TC-15 (CB-9, Beca Activa)
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
