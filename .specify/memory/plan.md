# plan.md

# Resumen Ejecutivo

Este plan describe la implementación conceptual de una Calculadora de Montos de Traslado Académico basada en las reglas definidas en spec.md y gobernada por los principios establecidos en constitution.md. La decisión técnica principal consiste en desacoplar la lógica de cálculo, las validaciones y la presentación de resultados, utilizando una fuente única de parámetros académicos derivada del Excel oficial de Gerencia. Esto permitirá adaptar cambios en ciclos, montos y fechas sin modificar las reglas de negocio. La solución prioriza mantenibilidad, trazabilidad y consistencia de resultados. Permanecen abiertas las definiciones relacionadas con futuras reglas académicas, frecuencia de actualización de parámetros y posibles ampliaciones del alcance.

---

# 1. Enfoque Técnico (Alto Nivel)

La solución se implementará mediante componentes independientes responsables de captura de datos, validaciones, cálculo y presentación de resultados.

Los parámetros académicos y financieros se obtendrán desde un archivo estático `parameters.json`, generado previamente a partir del Excel oficial aprobado por Gerencia. Antes de ejecutar cualquier cálculo, el sistema validará estados, fechas y modalidades. Posteriormente, el motor de cálculo determinará semanas restantes, saldo disponible y costo requerido del ciclo destino. Finalmente, el módulo de resultados presentará el estado económico correspondiente.

No se contempla almacenamiento histórico de cálculos.

---

# 2. Componentes / Archivos Afectados

### Módulo de Captura de Datos

Responsable de recibir:

* Fecha de traslado
* Ciclo origen
* Ciclo destino
* Modalidad
* Estado del estudiante
* Monto pagado
* Descuentos
* Beneficios

---

### Módulo de Validaciones

Responsable de verificar en cascada y en orden de prioridad:

1. Estado permitido
2. Existencia de ciclo origen y ciclo destino
3. Modalidad existente para el ciclo
4. Fecha válida dentro del periodo académico
5. Integridad de montos, descuentos y beneficios

El módulo debe aplicar validaciones "fail-fast" para detener el proceso tan pronto se encuentre una condición inválida.

---

### Motor de Cálculo de Traslados

Responsable de:

* Calcular semanas restantes
* Calcular saldo disponible
* Calcular costo requerido del ciclo destino
* Aplicar reglas para modalidad al contado
* Aplicar reglas para modalidad en cuotas
* Determinar saldo a favor, traslado cubierto o monto pendiente

---

### Fuente de Parámetros Académicos (`parameters.json`)

Responsable de almacenar:

* Ciclos académicos
* Fechas académicas
* Semanas por ciclo
* Cuotas por ciclo
* Montos al contado
* Montos por cuota
* Modalidades disponibles

El contenido será generado a partir del Excel oficial aprobado por Gerencia.

---

### Módulo de Resultados

Responsable de presentar:

* Saldo a favor
* Traslado cubierto
* Monto pendiente
* Mensajes de validación
* Observaciones de negocio
* Operaciones del resultado
---

# 3. Decisiones de Arquitectura (Mini-ADR)

## ADR-1

### DECISIÓN

Separar la lógica de cálculo de la interfaz de usuario.

### POR QUÉ

Las reglas de negocio poseen mayor probabilidad de cambio que la forma de captura o visualización de datos. El desacoplamiento facilita pruebas, mantenimiento y evolución de la solución.

### ALTERNATIVA DESCARTADA

Implementar las reglas directamente dentro de la interfaz.

### MOTIVO DEL DESCARTE

Genera alto acoplamiento entre presentación y negocio, dificulta las pruebas unitarias y aumenta el costo de mantenimiento.

---

## ADR-2

### DECISIÓN

Centralizar todos los parámetros académicos y financieros en una única fuente de datos derivada del Excel oficial.

### POR QUÉ

Garantiza consistencia con la información aprobada por Gerencia y cumple el principio de Single Source of Truth (SSoT) definido en la Constitución.

### ALTERNATIVA DESCARTADA

Mantener valores codificados manualmente dentro de la solución.

### MOTIVO DEL DESCARTE

Viola el principio de Single Source of Truth, incrementa el riesgo de inconsistencias y obliga a modificar la solución cada vez que Gerencia publique nuevas tarifas o ciclos.

---

## ADR-3

### DECISIÓN

Aplicar validaciones antes de ejecutar cualquier cálculo.

### POR QUÉ

Evita procesar información inválida y garantiza que únicamente se ejecuten cálculos sobre datos consistentes.

### ALTERNATIVA DESCARTADA

Realizar cálculos antes de validar.

### MOTIVO DEL DESCARTE

Puede generar resultados inconsistentes, incrementar la complejidad del flujo y dificultar la identificación de errores operativos.

---

# 4. Riesgos y Dependencias

## Riesgos

### R-1

Cambios en las reglas de negocio definidos por Gerencia.

**Mitigación:** Mantener las reglas de cálculo centralizadas y documentadas para facilitar modificaciones futuras.

### R-2

Errores o inconsistencias en el Excel oficial.

**Mitigación:** Validar la estructura e integridad de `parameters.json` antes de permitir cálculos.

### R-3

Interpretaciones ambiguas de fechas académicas o semanas restantes.

**Mitigación:** Documentar explícitamente las reglas de conteo de semanas y validarlas con el área usuaria.

### R-4

Nuevos estados académicos que modifiquen las reglas actuales de traslado.

**Mitigación:** Centralizar las validaciones de estado en un único componente para facilitar actualizaciones.

---

## Dependencias

### D-1

Disponibilidad del Excel oficial actualizado.

### D-2

Disponibilidad de las fechas académicas necesarias para calcular semanas restantes.

### D-3

Definición formal de políticas de descuentos y beneficios.

---

# 5. Trazabilidad

## US-1 (Obtener resultado económico del traslado)

Implementación:

* Módulo de Captura de Datos
* Motor de Cálculo de Traslados
* Fuente de Parámetros Académicos
* Módulo de Resultados

---

## US-2 (Validar reglas de negocio antes del cálculo)

Implementación:

* Módulo de Validaciones
* Fuente de Parámetros Académicos
* Módulo de Resultados

---

```
```
