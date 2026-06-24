Calculadora de Montos de Traslado Académico

Este proyecto implementa una calculadora para automatizar el cálculo de montos de traslado académico entre ciclos, reemplazando el proceso manual actual que utiliza Excel. El sistema determina si un traslado genera saldo a favor, traslado cubierto o monto pendiente de pago, aplicando reglas institucionales para modalidades al contado y en cuotas.

## Contexto y Objetivo

Actualmente, el área de TI realiza este cálculo manualmente, lo que toma entre 10 y 20 minutos por solicitud y depende del conocimiento individual del analista, aumentando el riesgo de errores. Durante campañas académica tiles, el volumen de solicitudes puede duplicarse o triplicarse.

El objetivo principal es reducir errores operativos, disminuir el tiempo de atención y estandarizar el proceso.

## Funcionalidades Core (User Stories)uiltinsCaptura de Datos
Permite ingresar: fecha de traslado, ciclo origen, ciclo destino, modalidad (Presencial o Virtual), estado del estudiante, monto pagado, descuentos y beneficios.

Validaciones en Cascada (Fail-Fast)
Verifica en orden de criticidad: estado del estudiante, existencia de ciclos, modalidad válida, fecha dentro del periodo académico, e integridad de montos. Detiene el proceso ante el primer error.

Motor de Cálculo Automatizado
Calcula semanas restantes, saldo disponible del ciclo origen, y costo requerido del ciclo destino para determinar el resultado económico final.

Presentación de Resultados con Desglose
Muestra el estado final (Saldo a favor, Sin saldo pendiente, o Monto pendiente) junto al desglose completo de las operaciones realizadas para la auditoría del cálculo.

## Abreviaturas Utilizadas

- US: User Story (Historia de Usuario)
- AC: Acceptance Criteria (Criterio de Aceptación)
- FR: Functional Requirement (Requisito Funcional)
- NFR: Non-Functional Requirement (Requisito No Funcional)
- CB: Caso Borde
- TC: Test Case (Caso de Prueba)
- ADR: Architectural Decision Record
- SSoT: Single Source of Truth (Fuente Única de Verdad)
- DTO: Data Transfer Object
- P1/P2: Prioridad 1 (alta) / Prioridad 2 (media)

## Decisiones de Arquitectura Clave

- Separación de responsabilidades: La lógica de cálculo está desacoplada de la interfaz de usuario para facilitar el mantenimiento y la prueba del código.
- Fuente única de verdad (SSoT): Los parámetros académicos se centralizan en un archivo `parameters.json`, generado a partir del Excel oficial de Gerencia.
- Validación previa: Las validaciones se ejecutan antes de cualquier cálculo para evitar procesar información inválida.

## Reglas de Negocio Principales

- Estados permitidos: MATRICULADO y PAGADO. Bloqueados: SUSPENDIDO y RETIRADO.
- Descuentos y beneficios aplican ÚNICAMENTE al saldo disponible del ciclo origen.
- El ciclo destino siempre usa la tarifa regular, sin descuentos ni beneficios previos.

## Requisitos y Restricciones

- Rendimiento: El cálculo debe completarse en menos de 2 segundos.
- Cobertura de Pruebas: Mínimo del 80% en la lógica de cálculo.
- Calidad de Código: Debe cumplir con el estándar PEP8.
- Alcance Externo: No se incluye almacenamiento histórico, integraciones con otros sistemas, ni generación de comprobantes.
