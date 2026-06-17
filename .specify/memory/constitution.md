# Constitution.md

## Feature: Calculadora de Montos de Traslado Académico

### Art. 3 · Quality Standards

#### 3.1 Exactitud de cálculos

Todo cálculo realizado por la herramienta deberá producir el mismo resultado que el procedimiento manual vigente basado en el Excel oficial proporcionado por Gerencia.

#### 3.2 Validación obligatoria de entradas

Antes de ejecutar cualquier cálculo, el sistema deberá validar:

* Estado de matrícula válido para realizar el traslado.
* Fecha de traslado válida dentro del periodo académico correspondiente.
* Existencia del ciclo origen.
* Existencia del ciclo destino.
* Existencia de la modalidad seleccionada.


Si alguna validación falla, el sistema deberá mostrar una observación clara y detener el procesamiento.

#### 3.3 Tiempo de respuesta

El resultado del cálculo deberá mostrarse al usuario en menos de 2 segundos desde el envío de los datos.

---

### Art. 4 · Architecture Principles

#### 4.1 Fuente única de verdad

La información oficial de ciclos, semanas académicas, cuotas, montos al contado, montos por cuota y demás parámetros de cálculo será la definida por el Excel autorizado por Gerencia.

#### 4.2 Separación de reglas de negocio

Las reglas de cálculo deberán mantenerse separadas de la interfaz de usuario para permitir modificaciones futuras sin afectar la experiencia del usuario.

#### 4.3 Trazabilidad de resultados

Todo resultado deberá mostrar claramente:

* Fecha de traslado utilizada.
* Ciclo origen.
* Ciclo destino.
* Modalidad de pago.
* Resultado final del cálculo.
* Estado final del traslado (saldo a favor, traslado cubierto o monto pendiente).

---

### Art. 7 · Boundaries

#### ALWAYS DO

* Validar todas las entradas antes de realizar cualquier cálculo.
* Utilizar únicamente la información oficial aprobada por Gerencia.
* Aplicar las fórmulas de cálculo vigentes para las modalidades al contado y en cuotas.
* Validar que el estado del estudiante sea MATRICULADO o PAGADO antes de procesar un traslado.
* Mostrar mensajes claros cuando un traslado no pueda procesarse.
* Mantener consistencia con los resultados obtenidos mediante el procedimiento manual actual.

#### ASK FIRST

* Cambios en las fórmulas de cálculo.
* Nuevas modalidades de pago.
* Nuevos estados de matrícula.
* Nuevos tipos de traslado.
* Cambios en las reglas de becas o descuentos.
* Integración con otros sistemas institucionales.

#### NEVER DO

* Procesar traslados de estudiantes con estado SUSPENDIDO o RETIRADO.
* Realizar cálculos con datos incompletos.
* Asumir valores por defecto cuando falte información requerida.
* Modificar fórmulas sin validación del área de negocio.
* Procesar traslados con fechas fuera del periodo académico válido.
* Mostrar resultados cuando exista una validación fallida.
* Mantener beneficios, becas o descuentos después de un traslado cuando la política institucional indique su pérdida.
* Permitir resultados inconsistentes con las reglas oficiales definidas por Gerencia.

```
