# spec.md

# Resumen ejecutivo

Actualmente el área de TI realiza cálculos manuales para determinar el monto correspondiente a un traslado académico utilizando información proporcionada por Gerencia mediante un archivo Excel oficial. El proceso requiere entre 10 y 20 minutos por solicitud y depende de la correcta interpretación de reglas relacionadas con fechas académicas, modalidad de pago, semanas restantes, descuentos y beneficios.

La presente feature propone una Calculadora de Montos de Traslado Académico que permita ingresar los parámetros necesarios y obtener automáticamente el resultado económico del traslado, reduciendo errores operativos, disminuyendo tiempos de atención y estandarizando la aplicación de las reglas de negocio.

---

# 1. Contexto de negocio

## Problema que resuelve

El cálculo actual de traslados se realiza manualmente utilizando fórmulas contenidas en un Excel oficial. Esto genera dependencia del conocimiento del analista, riesgo de errores humanos y tiempos elevados de atención.

## Impacto

La solución beneficiará al área de TI reduciendo el tiempo promedio de cálculo y garantizando consistencia en la aplicación de las reglas de negocio, especialmente durante campañas donde el volumen de solicitudes aumenta significativamente.

---

# 2. User Stories y criterios de aceptación

## US-1

Como analista de soporte,

quiero ingresar los datos requeridos para un traslado académico,

para obtener automáticamente el resultado económico del traslado.

### AC-1.1 Saldo a favor

Dado un traslado válido donde:

* Saldo disponible calculado = S/ 700
* Costo requerido del ciclo destino = S/ 500

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:

* Resultado: S/ 200 de saldo a favor
* Estado: "Saldo a favor"

### AC-1.2 Traslado cubierto

Dado un traslado válido donde:

* Saldo disponible calculado = S/ 500
* Costo requerido del ciclo destino = S/ 500

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:

* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### AC-1.3 Monto pendiente

Dado un traslado válido donde:

* Saldo disponible calculado = S/ 500
* Costo requerido del ciclo destino = S/ 800

Cuando el usuario ejecuta el cálculo,

Entonces el sistema muestra:

* Resultado: S/ 300 pendiente de pago
* Estado: "Monto pendiente por cancelar"

---

## US-2

Como analista de soporte,

quiero que el sistema valide las reglas de negocio antes de calcular,

para evitar resultados incorrectos.

### AC-2.1 Fecha inválida

Dado una fecha que no pertenece al periodo válido del ciclo origen o destino,

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"Fecha de traslado inválida para los ciclos seleccionados."

### AC-2.2 Estado no permitido

Dado cualquier estado diferente de:

* MATRICULADO
* PAGADO

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"El estado actual no permite realizar traslados."

### AC-2.3 Modalidad inexistente

Dado que el ciclo seleccionado no posee la modalidad indicada,

Cuando el usuario intenta calcular,

Entonces el sistema bloquea la operación y muestra:

"La modalidad seleccionada no existe para el ciclo indicado."

---

# 3. Requisitos no funcionales

### NFR-1

La generación del resultado deberá completarse en menos de 2 segundos.

---

# 4. Casos borde

### CB-1 Fecha fuera del rango académico

Resultado esperado:

El sistema bloquea el cálculo e informa que la fecha es inválida.

### CB-2 Ciclo origen igual a ciclo destino

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### CB-3 Modalidad inexistente

Resultado esperado:

El sistema bloquea el cálculo e informa que la modalidad no existe para el ciclo seleccionado.

### CB-4 Estado SUSPENDIDO

Resultado esperado:

El sistema bloquea el cálculo e informa que el estado no permite traslados.

### CB-5 Estado RETIRADO

Resultado esperado:

El sistema bloquea el cálculo e informa que el estado no permite traslados.

### CB-6 Resultado exactamente igual a cero

Resultado esperado:

El sistema muestra:

* Resultado: S/ 0
* Estado: "Sin saldo pendiente"

### CB-7 Traslado durante la última semana académica

Resultado esperado:

El cálculo utiliza únicamente las semanas restantes efectivamente disponibles según las reglas de negocio.

### CB-8 Estudiante con descuento activo

Resultado esperado:

El sistema utiliza el monto descontado para calcular el saldo disponible del ciclo origen y elimina el beneficio para el cálculo del ciclo destino.

### CB-9 Estudiante con beca activa

Resultado esperado:

El sistema utiliza el beneficio vigente únicamente para determinar el saldo disponible del ciclo origen y aplica la tarifa regular del ciclo destino.

---

# 5. Assumptions

### A-1

El Excel oficial proporcionado por Gerencia contiene información correcta y actualizada.

### A-2

Las fechas académicas necesarias para determinar semanas restantes están disponibles en la fuente oficial.

### A-3

Los descuentos y beneficios vigentes se encuentran correctamente identificados antes de ejecutar el cálculo.

### A-4

Únicamente los estados MATRICULADO y PAGADO permiten realizar traslados. Cualquier otro estado deberá bloquear el cálculo.

---

# 6. NEEDS_CLARIFICATION

### NC-1

¿Cómo se actualizarán los parámetros cuando Gerencia publique una nueva versión del Excel oficial?

### NC-2

¿Existe una fecha límite institucional previa al cierre de un ciclo para permitir traslados?

### NC-3

¿Los resultados calculados deben almacenarse para auditoría o únicamente mostrarse al usuario?

---

# 7. Scope

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

```
```
