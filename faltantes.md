# Especificaciones asumidas y pendientes de implementación

Este documento recopila las reglas de negocio, criterios visuales y comportamientos que se asumieron para completar la primera versión de la calculadora de traslado académico.

## 1. Reglas de negocio asumidas

- La calculadora debe evaluar si el traslado genera saldo a favor, cubre el costo del ciclo destino o deja un monto pendiente.
- El cálculo se basa en el monto pagado por el estudiante, proporcional al tiempo transcurrido o restante del ciclo de origen.
- El saldo disponible se obtiene con la fórmula:
  - saldo_disponible = monto_pagado × semanas_restantes ÷ semanas_totales
- El resultado final se obtiene con:
  - resultado = saldo_disponible - costo_destino
- Si el ciclo de origen y destino son iguales, no se genera saldo ni monto pendiente.
- La condición de pago puede ser Contado o Cuotas.
- El costo del ciclo destino puede verse afectado por descuentos aplicables, como 20%, 1/2 beca, 1/4 beca o descuento familiar.
- Los estados del estudiante permitidos son MATRICULADO y PAGADO; los bloqueados son SUSPENDIDO y RETIRADO.
- La modalidad aceptada por la calculadora es Presencial o Virtual.

## 2. Comportamiento visual asumido

- La interfaz debe mostrar un estado visual claro según el resultado:
  - Verde: saldo a favor
  - Azul: sin saldo pendiente
  - Naranja: monto pendiente
  - Rojo: error de validación o cálculo
- La pantalla debe incluir una leyenda de colores para que el usuario entienda el significado de cada estado.
- El resultado debe mostrar los valores clave del cálculo en tarjetas compactas.
- La vista debe incluir la fórmula aplicada y los pasos del cálculo para que el resultado sea transparente.
- Los campos del formulario deben estar organizados de forma más clara y con mejor jerarquía visual.

## 3. Operaciones que ahora se reflejan en la calculadora

- Cálculo proporcional del saldo disponible según el ciclo de origen.
- Cálculo del costo del ciclo destino con descuento aplicado.
- Presentación del resultado con detalle numérico y texto explicativo.
- Mostrar la fórmula y los pasos utilizados en el cálculo.
- Validación de estados, modalidades, condiciones de pago y ciclos registrados.

## 4. Pendientes recomendados para la siguiente iteración

- Integrar reglas más finas de fechas académicas y vigencia de ciclos.
- Ajustar la lógica para considerar descuentos y beneficios con reglas más específicas del negocio.
- Añadir mensajes más detallados según el tipo de estudiante, condición de pago y modalidad.
- Ampliar las pruebas automatizadas con casos de descuento, beca y monto pendiente.
