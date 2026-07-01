# Constitution.md

# Constitución del Proyecto

## Feature: Calculadora de Montos de Traslado Académico

### Art. 3 · Quality Standards

#### 3.1 Exactitud de resultados

Todo cálculo generado por la herramienta deberá coincidir con el resultado obtenido mediante el procedimiento manual vigente utilizando el Excel oficial aprobado por Gerencia.

#### 3.2 Cobertura mínima de pruebas

La lógica de cálculo deberá mantener una cobertura mínima del 80% mediante pruebas unitarias que validen escenarios felices, errores y casos borde.

#### 3.3 Rendimiento

La herramienta deberá generar el resultado del cálculo en menos de 200 milisegundos desde que el usuario envía los datos requeridos.

#### 3.4 Calidad del código

El código deberá cumplir el estándar PEP8 y superar la validación automática de estilo antes de ser considerado listo para entrega.

---

### Art. 4 · Architecture Principles

#### 4.1 Fuente única de verdad

Los parámetros académicos y financieros deberán obtenerse de una representación digital controlada cuyo origen sea el Excel oficial aprobado por Gerencia.

#### 4.2 Separación de responsabilidades

La lógica de cálculo deberá mantenerse separada de la interfaz de usuario para facilitar mantenimiento, pruebas y futuras modificaciones.

#### 4.3 Arquitectura por capas

La solución deberá separar claramente:

* Captura de datos de entrada.
* Reglas de negocio y cálculos.
* Presentación de resultados.

#### 4.4 Anti-patrones prohibidos

No se permitirá:

* Duplicar fórmulas de cálculo en múltiples componentes.
* Mezclar reglas de negocio con código de interfaz.
* Modificar directamente la fuente oficial de datos desde la aplicación.

#### 4.5 Stack Tecnológico

El stack tecnológico de implementación será Python 3.11+, lo que justifica el requisito PEP8 definido en Art. 3.4 de la Constitución.

---

### Art. 7 · Boundaries

#### ALWAYS DO

* Utilizar únicamente información oficial aprobada por Gerencia.
* Validar todas las entradas antes de ejecutar cálculos.
* Mantener consistencia con los resultados del procedimiento manual vigente.
* Mostrar mensajes de error estandarizados indicando el campo inválido y la causa de la validación fallida.
* Registrar y documentar cualquier cambio en las reglas de cálculo.

#### ASK FIRST

* Cambios en fórmulas de negocio.
* Nuevas modalidades de pago.
* Nuevos estados de matrícula.
* Nuevos tipos de traslado.
* Cambios en políticas de descuentos o beneficios.
* Integraciones con otros sistemas institucionales.

#### NEVER DO

* Realizar cálculos con información incompleta.
* Asumir valores por defecto cuando falten datos obligatorios.
* Modificar fórmulas sin validación del área de negocio.
* Procesar operaciones que no cumplan las validaciones definidas.
* Mostrar resultados cuando exista una validación fallida.
* Duplicar reglas de negocio en diferentes componentes del sistema.

