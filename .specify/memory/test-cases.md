# Correcciones al test-cases.md

## TC-1 (AC-1.1, Caso Saldo a favor)

### Datos
* Saldo disponible calculado: S/700
* Costo requerido del ciclo destino: S/500
* Traslado: Valido

### Pasos
1. Ingresar los datos.
2. Ejecutar el cálculo.

### Esperado 
El sistema muestra:

* Resultado: S/ 200 de saldo a favor
* Estado: "Saldo a favor"

## TC-2 (AC-1.2, Caso Traslado Cubierto)

### Datos
* Saldo disponible calculado: S/ 500
* Costo requerido del ciclo destino: S/ 500


### Pasos
1. Ingresar los datos.
2. Ejecutar el cálculo.

### Esperado 
El sistema muestra:

* Resultado: S/0
* Estado: “Sin saldo pendiente”



## TC-4 (AC-2.1, Caso Error - Fecha Inválida)

### Datos

* Estado: MATRICULADO
* Fecha de traslado: 25/12/2026
* Ciclo origen: C01
* Ciclo destino: C02

### Pasos

1. Ingresar los datos.
2. Ejecutar el cálculo.

### Esperado

El sistema bloquea el cálculo y muestra:

"Fecha de traslado inválida para los ciclos seleccionados."

---

## TC-11 (CB-7, Última Semana Académica)

### Datos

* Ciclo origen: C01
* Fecha de traslado: 15/07/2026
* Total de semanas del ciclo: 16
* Semana actual: 16
* Semanas restantes: 1
* Modalidad: Contado
* Monto del ciclo: S/ 800

### Pasos

1. Ingresar los datos.
2. Ejecutar el cálculo.

### Esperado

El sistema calcula:

Saldo disponible = (800 / 16) × 1

Saldo disponible = S/ 50

El resultado mostrado utiliza únicamente la última semana académica disponible.

---

## TC-12 (CB-8, Descuento Activo)

### Datos

* Descuento vigente: 20%
* Monto cuota origen: S/ 400
* Monto con descuento: S/ 320
* Costo requerido ciclo destino: S/ 400

### Pasos

1. Ingresar los datos.
2. Ejecutar el cálculo.

### Esperado

El sistema calcula:

Saldo disponible = S/ 320

Costo destino = S/ 400

Resultado = S/ 80 pendiente

El sistema muestra:

* Resultado: S/ 80 pendiente
* Estado: "Monto pendiente por cancelar"

---

## TC-13 (CB-9, Beca Activa)

### Datos

* Beca vigente: 25%
* Tarifa regular ciclo origen: S/ 1000
* Saldo disponible calculado: S/ 750
* Tarifa regular ciclo destino: S/ 1000

### Pasos

1. Ingresar los datos.
2. Ejecutar el cálculo.

### Esperado

El sistema calcula:

Saldo disponible = S/ 750

Costo destino = S/ 1000

Resultado = S/ 250 pendiente

El sistema muestra:

* Resultado: S/ 250 pendiente
* Estado: "Monto pendiente por cancelar"

Además, el cálculo utiliza tarifa regular para el ciclo destino, sin aplicar la beca previamente existente.

```
```
