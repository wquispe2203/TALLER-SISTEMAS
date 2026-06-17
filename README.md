# 🎓 Entregable Taller 2: Calculadora de Montos de Traslado Académico

## 💻 Miembros del Equipo - Grupo V1

| Integrante | Rol en el Taller | Especialidad / Función Principal |
| ---------- | ---------------- | -------------------------------- |
| **Walter Quispe** | Product Owner (PO) | Definición de requerimientos, análisis de negocio y dirección de producto. |
| **Luis Seminario** | Tech Lead | Desarrollo de arquitectura frontend y backend, integraciones y lógica de negocio. |
| **Daniel Estrella** | Tech Lead | Desarrollo de arquitectura frontend y backend, integraciones y lógica de negocio. |
| **Alonso Ponce** | QA Tester | Control de calidad, diseño y ejecución de planes de pruebas y soporte técnico. |
| **Carlos la Torre** | QA / Apoyo | Soporte de infraestructura, pruebas funcionales y asistencia en control de calidad. |

---

## 🎯 Matriz de Cobertura de Criterios de Aceptación

Mapeo de trazabilidad entre las reglas de negocio de traslados, los componentes del plan técnico y sus respectivos escenarios de prueba.

| Requisito (US / AC / Borde) | Módulo de Destino | Código de Test (TC) | Estado |
| --------------------------- | ----------------- | ------------------- | :----: |
| **US-1 / AC-1.1** (Saldo a favor) | Sí → `Módulo de Resultados` | - | ⏳ |
| **US-1 / AC-1.2** (Traslado cubierto) | Sí → `Módulo de Resultados` | - | ⏳ |
| **US-1 / AC-1.3** (Monto pendiente) | Sí → `Módulo de Resultados` | - | ⏳ |
| **US-2 / AC-2.1** (Fecha inválida) | Sí → `Módulo de Validaciones` | TC-4 | 🔹 |
| **US-2 / AC-2.2** (Estado no permitido) | Sí → `Módulo de Validaciones` | - | ⏳ |
| **US-2 / AC-2.3** (Modalidad inexistente) | Sí → `Módulo de Validaciones` | - | ⏳ |
| **CB-1** (Fecha fuera del rango) | Sí → `Módulo de Validaciones` | - | ⏳ |
| **CB-2** (Ciclo origen igual destino) | Sí → `Motor de Cálculo` | - | ⏳ |
| **CB-3** (Modalidad inexistente) | Sí → `Módulo de Validaciones` | - | ⏳ |
| **CB-4** (Estado SUSPENDIDO) | Sí → `Módulo de Validaciones` | - | ⏳ |
| **CB-5** (Estado RETIRADO) | Sí → `Módulo de Validaciones` | - | ⏳ |
| **CB-6** (Resultado cero) | Sí → `Motor de Cálculo` | - | ⏳ |
| **CB-7** (Traslado última semana) | Sí → `Motor de Cálculo` | TC-11 | 🔹 |
| **CB-8** (Descuento activo) | Sí → `Motor de Cálculo` | TC-12 | 🔹 |
| **CB-9** (Beca activa) | Sí → `Motor de Cálculo` | TC-13 | 🔹 |

---

## 🔍 Resultado del Control de Calidad de Requisitos

El grupo revisor ha sometido la especificación (`spec.md`) a evaluación en las siguientes 4 categorías:

| Dimensión | Evaluación | Detalles de la Validación |
| :-------- | :--------: | :------------------------ |
| **Completitud** | ✔️ | Todos los casos borde (CB-1 a CB-9) y NFRs (`< 200 ms`) están definidos. |
| **Claridad** | ✔️ | Exclusión de términos ambiguos. Reglas de cálculo de saldos y descuentos explícitas. |
| **Consistencia** | ✔️ | Alineación entre `spec.md`, módulos en `plan.md` y `test-cases.md`. |
| **Testabilidad** | ✔️ | Criterios bajo el formato estándar *Dado / Cuando / Entonces*. |

<br>

**Veredicto:** 🟢 **TODO PASA (Aprobado)**

*Se cuenta con un nivel de especificación robusto y verificado por el equipo para proceder con la implementación.*