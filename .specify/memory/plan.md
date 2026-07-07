# plan.md

# Resumen Ejecutivo

Este plan describe la implementación conceptual de una Calculadora de Montos de Traslado Académico basada en las reglas definidas en spec.md y gobernada por los principios establecidos en constitution.md. La decisión técnica principal consiste en desacoplar la lógica de cálculo, las validaciones y la presentación de resultados, utilizando una fuente única de parámetros académicos derivada del Excel oficial de Gerencia. Esto permitirá adaptar cambios en ciclos, montos y fechas sin modificar las reglas de negocio. La solución prioriza mantenibilidad, trazabilidad y consistencia de resultados. Permanecen abiertas las definiciones relacionadas con futuras reglas académicas, frecuencia de actualización de parámetros y posibles ampliaciones del alcance.

---

# 1. Enfoque Técnico (Alto Nivel)

La solución se implementará mediante componentes independientes responsables de captura de datos, validaciones, cálculo y presentación de resultados.

La interfaz será una aplicación web sencilla con HTML, CSS y JavaScript vanilla servidos por Flask desde `templates/` y `static/`. El backend se desarrollará en Python 3.11+ con Flask y expondrá un endpoint HTTP `POST /api/transfer-calculator` que recibe JSON, valida en cascada, ejecuta el motor de cálculo y devuelve resultado, estado y desglose. Los parámetros académicos y financieros se cargarán desde `data/parameters.json`, generado a partir del Excel oficial aprobado por Gerencia. Antes de calcular, el sistema aplicará validaciones fail-fast. El motor determinará semanas restantes, saldo disponible y costo del ciclo destino usando `decimal.Decimal` para montos. Las pruebas unitarias usarán pytest con cobertura mínima del 80% sobre validación y cálculo; el estilo de código se validará con ruff (PEP8).

No se contempla almacenamiento histórico de cálculos en esta fase.

---

# 2. Stack y Estructura de Archivos

Estructura planificada (documentada; implementación pendiente):

```
TALLER-SISTEMAS/
├── app.py                  # Rutas Flask (UI + API en un solo archivo al inicio)
├── validation.py           # Validaciones en cascada
├── calculator.py           # Motor de cálculo (sin Flask)
├── data/parameters.json    # Parámetros oficiales
├── templates/index.html
├── static/css/styles.css
├── static/js/app.js
├── tests/
└── requirements.txt
```

Convención de rutas (mismo origen, sin CORS):

* `GET /` → página del formulario
* `POST /api/transfer-calculator` → cálculo
* Assets en `/static/...`
* `fetch` con rutas relativas desde el frontend

Dependencias (`requirements.txt`): Flask, pytest, pytest-cov, ruff.

---

# 3. Componentes / Archivos Afectados

### Módulo de Captura de Datos

Responsable de recibir la información de entrada del usuario y pasarla al siguiente paso.

* Fecha de traslado
* Ciclo origen (Nombre, Universidad, Modalidad Académica, Pago en)
* Ciclo destino (Nombre, Universidad, Modalidad Académica, Pago en)

---

### Módulo de Normalización y Parseo

Responsable de transformar los datos crudos recibidos en un formato estructurado, consistente y tipado antes de enviarlos a validación.

* Convertir fechas a formato estándar
* Normalizar nombres de modalidades
* Validar tipos numéricos de montos
* Construir un DTO / contrato de entrada
* Rechazar entradas imposibles de parsear

Este módulo asegura que la validación y el cálculo trabajen con datos limpios y predecibles.

---

### Módulo de Validaciones

Responsable de verificar en cascada y en orden de prioridad:

1. Existencia de ciclo origen y ciclo destino en parameters.json
2. Igualdad de modalidad de pago entre origen y destino
3. Fecha válida dentro del periodo académico de ambos ciclos
4. (Opcional) Integridad de los datos de entrada (tipos, formato de fecha)

El módulo debe aplicar validaciones "fail-fast" para detener el proceso tan pronto se encuentre una condición inválida.

---

### Motor de Cálculo de Traslados

Responsable de:

* Calcular semanas restantes (con ajuste por semanas de feriado)
* Calcular saldo disponible
* Calcular costo requerido del ciclo destino
* Aplicar reglas para modalidad al contado
* Aplicar reglas para modalidad en cuotas
* Determinar saldo a favor, traslado cubierto o monto pendiente
* Calcular semanas consumidas con ajuste de fecha por feriados

#### Reglas específicas para CONTADO

* Las semanas se anclan al **calendario global** (lunes-domingo).
* Si la fecha de traslado cae en **lunes o martes**, la semana actual NO se considera consumida.
* Si la fecha de traslado cae entre **miércoles y domingo**, la semana actual SÍ se considera consumida.
* Las semanas de feriado completas no se cuentan como consumidas.

#### Reglas específicas para CUOTAS

* Las semanas se anclan a la **fecha de inicio del periodo de la cuota**, no al lunes del calendario.
* El algoritmo calcula solo el **valor residual de la cuota vigente** (no suma todas las cuotas futuras).
* El periodo de una cuota va desde su fecha de inicio hasta la fecha de la siguiente cuota.
* Las semanas feriado dentro del periodo de la cuota no se consideran consumidas.

---

### Fuente de Parámetros Académicos (`data/parameters.json`)

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

# 4. Decisiones de Arquitectura (Mini-ADR)

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

Garantiza consistencia con la información aprobada por Gerencia y cumple el principio de Single Source of Truth (SSoT) definido en la Constitución. El Excel también define las fechas de feriados que afectan el conteo de semanas.

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

# 5. Riesgos y Dependencias

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

Cambio en el calendario de feriados institucionales.

**Mitigación:** Los feriados están definidos en el código como `FERIADOS_DIAS = [(7, 28), (7, 29), (12, 25)]`. Actualizar estas constantes cuando cambie la política institucional.

---

## Dependencias

### D-1

Disponibilidad del Excel oficial actualizado.

### D-2

Disponibilidad de las fechas académicas necesarias para calcular semanas restantes.

### D-3

Definición clara de las semanas de feriados institucionales.

---

# 6. Trazabilidad

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
