# Plan de alineación del proyecto con el Algoritmo v4

**Objetivo:** Hacer que la especificación (`spec.md`), el plan (`plan.md`), los casos de prueba (`test-cases.md`) y la documentación de memoria sean 100 % coherentes con el algoritmo de traslados académicos v4, el cual se considera la implementación definitiva.

**Principio rector:** El algoritmo y el archivo `parameters.json` (generado desde el Excel oficial) son la única fuente de verdad. Todo artefacto debe derivarse de ellos.

---

## 1. Cambios en `spec.md`

### 1.1 Eliminar entradas que el algoritmo no usa
**¿Qué?** Quitar los campos: *Estado del estudiante*, *Monto pagado*, *Descuentos*, *Beneficios*.  
**¿Por qué?** El algoritmo no los solicita ni los necesita. Los descuentos ya vienen incorporados en `cash_price` y los beneficios no forman parte de la lógica actual.

**Acción:**
- Eliminar de FR-001 los ítems *Estado del estudiante*, *Monto pagado*, *Descuentos*, *Beneficios*.
- Eliminar FR-002 (Estados permitidos), FR-004 (Descuentos aplicables) y FR-005 (Beneficios aplicables) porque dejan de tener sentido.
- Eliminar las referencias a descuentos/beneficios en las US y AC (US-1, US-3, US-4).

### 1.2 Agregar nuevos campos de entrada
**¿Qué?** Incluir *Universidad* (origen y destino) y separar *Pago en* para origen y destino.  
**¿Por qué?** El algoritmo necesita estos datos para buscar el ciclo en `parameters.json` y para validar que las modalidades de pago coincidan.

**Acción:**
- Modificar FR-001 para listar:
  - Fecha de traslado
  - Ciclo origen: Nombre, Universidad, Modalidad Académica, Pago en
  - Ciclo destino: Nombre, Universidad, Modalidad Académica, Pago en
- Agregar FR-009: **Validación de igualdad de modalidad de pago**. El sistema debe rechazar el traslado si `pago_en_origen != pago_en_destino`.

### 1.3 Ajustar reglas de validación (FR-007)
**¿Qué?** Reemplazar el orden de validación en cascada por el que usa el algoritmo.  
**¿Por qué?** El algoritmo valida en este orden: existencia de ciclos → igualdad de modalidad de pago → fecha dentro de rango. No hay validación de estado ni de montos.

**Acción:**
- Redefinir FR-007:
  1. Existencia de ciclo origen y ciclo destino en `parameters.json`.
  2. Igualdad de modalidad de pago entre origen y destino.
  3. Fecha de traslado dentro del periodo académico de ambos ciclos.
  4. (Opcional) Integridad de los datos de entrada (tipos, formato de fecha).
- Eliminar FR-003 (Modalidades disponibles) si ya está implícito en los datos del JSON, o mantenerlo como nota de que solo existen las modalidades que aparecen en el JSON.

### 1.4 Actualizar los criterios de aceptación (US-1 a US-4)
**¿Qué?** Reescribir los AC usando los casos de prueba del algoritmo (TC-1 a TC-12) como ejemplos concretos.  
**¿Por qué?** Los AC originales usaban datos ficticios (S/ 700, S/ 500) que no corresponden a ningún ciclo real. Los nuevos AC deben reflejar los cálculos verificables con el Excel.

**Acción:**
- US-1: cambiar los tres escenarios (saldo a favor, cubierto, pendiente) por los TC-1, TC-2 y TC-3 del algoritmo.
- US-2: alinear los mensajes de error con los del algoritmo (p.ej., “No se permiten traslados entre modalidades de pago diferentes…”).
- US-3 (desglose): mantener la idea de mostrar semanas y fórmulas, pero ahora las fórmulas incluyen el ajuste por feriados y el valor residual de contado/cuotas.
- US-4 (visualización): ajustar los ejemplos de montos (S/ 324.00 y S/ 1347.00) a los que resultan de los nuevos TC.

### 1.5 Actualizar casos borde (CB)
**¿Qué?** Sustituir los CB antiguos por los nuevos que surgen del algoritmo (feriados, ciclo no encontrado, etc.).  
**¿Por qué?** El algoritmo introduce comportamientos no previstos (feriados, bloqueo por modalidad distinta).

**Acción:**
- CB-1 (fecha fuera de rango) se mantiene pero con el mensaje exacto del algoritmo.
- CB-2 (ciclo origen = destino) se mantiene (resultado cero).
- Agregar CB relacionado con semanas de feriado (traslado en semana de Fiestas Patrias o Navidad).
- Agregar CB de ciclo inexistente.
- Eliminar CB de estado SUSPENDIDO/RETIRADO porque ya no aplica.

### 1.6 Actualizar requisitos no funcionales (NFR)
**¿Qué?** Mantener el NFR-1 (tiempo de respuesta < 200ms) y agregar uno sobre el uso obligatorio de `decimal.Decimal` para todos los montos.  
**¿Por qué?** El algoritmo ya lo exige para evitar errores de redondeo.

---

## 2. Cambios en `plan.md`

### 2.1 Arquitectura de componentes
**¿Qué?** Revisar los módulos para que coincidan con la implementación del algoritmo.  
**¿Por qué?** El plan original mencionaba módulos de normalización, validación de estado, descuentos, etc. Ahora esos módulos no son necesarios.

**Acción:**
- **Eliminar** los módulos de *Normalización de beneficios/descuentos* y *Validación de estados de matrícula*.
- **Mantener** los módulos de *Captura de datos*, *Validación en cascada* (con la nueva lógica), *Motor de cálculo* (que ahora incluye semanas de feriado y ajuste de fecha) y *Fuente de parámetros académicos*.
- **Agregar** un submódulo para el cálculo de semanas consumidas con ajuste de feriados.
- Actualizar la estructura de archivos propuesta si es necesario (por ejemplo, incluir un archivo `feriados.py` o integrarlo en `calculator.py`).

### 2.2 Actualizar las decisiones de arquitectura (mini-ADR)
**¿Qué?** Reflejar que la fuente única de verdad ahora incluye explícitamente los feriados y que el cálculo de semanas se basa en el calendario ajustado.  
**¿Por qué?** Para que el ADR-2 (Single Source of Truth) contemple todos los datos que el algoritmo usa del Excel.

**Acción:**
- ADR-2: añadir que el Excel también define las fechas de feriados que afectan el conteo de semanas (aunque el algoritmo las tenga como constantes, provienen de la política institucional reflejada en el Excel).

### 2.3 Riesgos y dependencias
**¿Qué?** Revisar riesgos.  
**¿Por qué?** Al eliminar estado del estudiante y monto pagado, algunos riesgos desaparecen, pero aparecen otros como el correcto manejo de feriados.

**Acción:**
- Eliminar R-4 (nuevos estados académicos).
- Agregar riesgo: “Cambio en el calendario de feriados institucionales” (mitigación: actualizar las constantes en el código).
- Dependencia D-3 (políticas de descuentos) deja de ser relevante; reemplazar por “Definición clara de las semanas de feriado”.

---

## 3. Cambios en `test-cases.md`

**¿Qué?** Reemplazar completamente la suite de 16 casos de prueba por los casos de prueba del algoritmo (TC-1 a TC-12).  
**¿Por qué?** Los casos actuales están basados en la especificación antigua y no son ejecutables con el algoritmo real. La nueva suite ya fue calculada manualmente y validada contra los datos del Excel.

**Acción:**
- Copiar los 12 casos de prueba del documento del algoritmo al archivo `test-cases.md`, incluyendo los datos de entrada exactos, los pasos y los resultados esperados.
- Asegurarse de cubrir:
  - Contado con saldo a favor, pendiente, cubierto (TC-1, TC-2, TC-3)
  - Cuotas con diferentes estructuras (TC-9)
  - Errores de modalidad diferente (TC-4)
  - Fecha fuera de rango (TC-5)
  - Días de la semana (lunes/martes vs miércoles) (TC-6, TC-7, TC-8)
  - Feriados (TC-11, TC-12)
  - Ciclo inexistente (TC-10)
- Eliminar los TC antiguos (TC-4 a TC-16) que ya no aplican.

---

## 4. Cambios en `constitution.md`

**¿Qué?** Ajustar los principios para que no entren en conflicto con el nuevo alcance.  
**¿Por qué?** La constitución actual menciona “descuentos y beneficios” y “estados de matrícula” en los ejemplos de ASK FIRST. Como ahora no se manejan, esos ejemplos pueden confundir.

**Acción:**
- En Art. 7 (Boundaries), sección ASK FIRST, eliminar las líneas:
  - “Nuevos estados de matrícula.”
  - “Cambios en políticas de descuentos o beneficios.”
- Agregar en su lugar:
  - “Cambios en la definición de semanas de feriado.”
  - “Nuevos campos requeridos en el Excel que afecten la estructura de parameters.json.”
- Mantener el resto de los principios de calidad y arquitectura intactos (siguen siendo válidos).

---

## 5. Cambios en otros archivos de memoria

### `decisions.md`
Añadir una entrada documentando la decisión de adoptar el algoritmo v4 como referencia canónica, indicando que los artefactos anteriores quedan obsoletos y que cualquier cambio futuro debe partir de esta base.

### `lessons.md`
Registrar la lección aprendida: “Definir el algoritmo completo antes de redactar la especificación funcional evita discrepancias y retrabajo.” Prevención: en futuros proyectos, partir del Excel y del algoritmo acordado con el negocio, y luego redactar la spec.

### `session-state.md`
Actualizar el estado de la funcionalidad: fase actual = “Implementación (alineación de artefactos)”, e indicar que los archivos modificados incluyen spec, plan, test-cases, constitution, decisions.

---

## 6. Resumen de la implementación

1. **Aprobar este plan** con el equipo (o el responsable del proyecto).
2. **Modificar los archivos** en el orden sugerido:
   - `spec.md`
   - `plan.md`
   - `test-cases.md`
   - `constitution.md`
   - `decisions.md`, `lessons.md`, `session-state.md`
3. **Verificar** que todos los artefactos referencien los mismos campos de entrada, las mismas validaciones y los mismos casos de prueba.
4. **Ejecutar** la suite de tests actualizada contra el algoritmo implementado para confirmar la coherencia.

Con esto, el proyecto quedará completamente alineado con el algoritmo v4 y `parameters.json`, eliminando cualquier ambigüedad y garantizando que los estándares de calidad (exactitud, cobertura de pruebas, rendimiento) se midan sobre la base correcta.