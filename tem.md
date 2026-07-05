# Algoritmo del Sistema de Traslados Académicos - Academia Vonex (v4 - Datos del Excel)

## 1. Descripción General

Sistema de cálculo de traslados académicos que determina el saldo a favor o monto pendiente cuando un alumno se traslada de un ciclo a otro. El sistema valida las fechas, calcula el valor residual de ambos ciclos y determina la diferencia económica.

**Todos los datos vienen del Excel:** fechas de inicio, fin, vencimiento de cuotas, montos, descuentos.

---

## 2. Entradas del Sistema (9 campos)

### Campo único:
| # | Campo | Tipo | Ejemplo |
|---|---|---|---|
| 1 | Fecha de traslado | Fecha (DD/MM/YYYY) | 15/05/2026 |

### Ciclo Origen (4 campos):
| # | Campo | Tipo | Ejemplo |
|---|---|---|---|
| 2 | Ciclo | Texto | ANUAL MARZO |
| 3 | Universidad | Texto | SM |
| 4 | Modalidad Académica | Enum (PRESENCIAL/VIRTUAL) | PRESENCIAL |
| 5 | Pago en | Enum (CONTADO/CUOTAS) | CONTADO |

### Ciclo Destino (4 campos):
| # | Campo | Tipo | Ejemplo |
|---|---|---|---|
| 6 | Ciclo | Texto | ANUAL MARZO |
| 7 | Universidad | Texto | UNI |
| 8 | Modalidad Académica | Enum (PRESENCIAL/VIRTUAL) | VIRTUAL |
| 9 | Pago en | Enum (CONTADO/CUOTAS) | CONTADO |

---

## 3. Reglas de Negocio

### Regla 1: Validación de modalidad de pago
```
SI pago_en_origen != pago_en_destino:
    → BLOQUEAR
    → Mensaje: "No se permiten traslados entre modalidades de pago diferentes. 
                Si requiere este tipo de traslado, debe procesarlo manualmente."
```

### Regla 2: Validación de fecha dentro del ciclo
```
SI fecha_traslado < fecha_inicio_ciclo O fecha_traslado > fecha_fin_ciclo:
    → BLOQUEAR
    → Mensaje: "La fecha de traslado está fuera del rango del ciclo [ORIGEN/DESTINO]."
```

### Regla 3: Semanas de feriados (Julio 28-29 y Diciembre 25)
```
Las semanas de feriados son:
- Semana que contiene el 28 de julio (Fiestas Patrias)
- Semana que contiene el 29 de julio (Fiestas Patrias)
- Semana que contiene el 25 de diciembre (Navidad)

Regla: Una "semana de feriado" se CANCELA y se toma la SIGUIENTE semana para:
  - Cálculos de semanas consumidas
  - Cálculos de semanas restantes
  - Determinación de la semana a calcular

Esto significa que el calendario académico "salta" las semanas de feriado.
```

### Regla 4: Consumo de semana (Lunes/Martes) - AJUSTADO CON FERIADOS
```
Primero: ajustar la fecha de traslado restando las semanas de feriado que ya transcurrieron.

semanas_feriado_transcurridas = contar_semanas_feriado_entre(fecha_inicio, fecha_traslado)
fecha_traslado_ajustada = fecha_traslado - (semanas_feriado_transcurridas * 7 días)

Luego aplicar la regla de Lunes/Martes sobre la fecha ajustada:

SI día_semana(fecha_traslado_ajustada) es LUNES (0) o MARTES (1):
    → La semana actual NO se ha consumido
    → semanas_consumidas = semanas_completas_transcurridas_ajustadas

SI día_semana(fecha_traslado_ajustada) es MIÉRCOLES (2), JUEVES (3), VIERNES (4), SÁBADO (5) o DOMINGO (6):
    → La semana actual SÍ se ha consumido
    → semanas_consumidas = semanas_completas_transcurridas_ajustadas + 1
```

### Regla 5: Cálculo de valor residual - CONTADO
```
# El precio de contado YA viene con descuento del Excel
monto_contado = cash_price  # Ej: 4590 (ya es 5100 - 10%)

# Calcular semanas efectivas (incluyendo feriados)
semanas_feriado_en_ciclo = contar_semanas_feriado_entre(fecha_inicio, fecha_fin)
semanas_efectivas = duration_weeks + semanas_feriado_en_ciclo

semanas_restantes = semanas_efectivas - semanas_consumidas
valor_semana = monto_contado / semanas_efectivas
valor_residual = valor_semana * semanas_restantes
```

### Regla 6: Cálculo de valor residual - CUOTAS
```
# Las fechas de vencimiento y montos VIENEN DEL EXCEL
Para cada cuota en installments[]:
    SI fecha_traslado < due_date_cuota:
        → Esta cuota y las siguientes están pendientes
        → valor_residual = suma de amount de cuotas pendientes
```

### Regla 7: Cálculo de diferencia
```
saldo_origen = valor_residual(ciclo_origen)
costo_destino = valor_residual(ciclo_destino)
diferencia = saldo_origen - costo_destino

SI diferencia > 0:
    → "Saldo a favor: S/ [diferencia]"
SI diferencia < 0:
    → "Monto pendiente: S/ [valor_absoluto(diferencia)]"
SI diferencia == 0:
    → "Traslado cubierto exactamente"
```

---

## 4. Estructura de Datos (parameters.json) - DESDE EL EXCEL

**Principio:** TODAS las fechas y montos vienen del Excel. No se calcula nada.

```json
{
  "ciclos": [
    {
      "nombre": "ANUAL MARZO",
      "universidad": "SM",
      "modalidad_academica": "PRESENCIAL",
      "fecha_inicio": "2026-03-16",
      "fecha_fin": "2026-12-31",
      "duration_weeks": 40,
      "observation": "Sillabus de 30 semanas. En lugar del último FB se hará la última semana de clases.",
      "payment_plans": {
        "Contado": {
          "num_installments": 10,
          "total": 5100,
          "discount_percent": 10,
          "cash_price": 4590,
          "installments": [
            {"number": 1, "amount": 510, "due_date": "2026-03-16"},
            {"number": 2, "amount": 510, "due_date": "2026-04-11"},
            {"number": 3, "amount": 510, "due_date": "2026-05-09"},
            {"number": 4, "amount": 510, "due_date": "2026-06-06"},
            {"number": 5, "amount": 510, "due_date": "2026-07-04"},
            {"number": 6, "amount": 510, "due_date": "2026-08-08"},
            {"number": 7, "amount": 510, "due_date": "2026-09-05"},
            {"number": 8, "amount": 510, "due_date": "2026-10-03"},
            {"number": 9, "amount": 510, "due_date": "2026-10-31"},
            {"number": 10, "amount": 510, "due_date": "2026-11-28"}
          ]
        },
        "Cuotas": {
          "num_installments": 10,
          "total": 5100,
          "discount_percent": 0,
          "cash_price": 5100,
          "installments": [
            {"number": 1, "amount": 510, "due_date": "2026-03-16"},
            {"number": 2, "amount": 510, "due_date": "2026-04-11"},
            {"number": 3, "amount": 510, "due_date": "2026-05-09"},
            {"number": 4, "amount": 510, "due_date": "2026-06-06"},
            {"number": 5, "amount": 510, "due_date": "2026-07-04"},
            {"number": 6, "amount": 510, "due_date": "2026-08-08"},
            {"number": 7, "amount": 510, "due_date": "2026-09-05"},
            {"number": 8, "amount": 510, "due_date": "2026-10-03"},
            {"number": 9, "amount": 510, "due_date": "2026-10-31"},
            {"number": 10, "amount": 510, "due_date": "2026-11-28"}
          ]
        }
      }
    }
  ]
}
```

**Notas importantes:**
- `fecha_inicio` y `fecha_fin` vienen del Excel
- `duration_weeks` viene del Excel (40 semanas)
- Las cuotas con sus `due_date` y `amount` vienen del Excel
- `Contado` tiene `cash_price` (monto con descuento) y `discount_percent`
- `Cuotas` tiene `cash_price` = `total` (sin descuento)
- El sistema busca el plan según el campo "Pago en" (CONTADO → "Contado", CUOTAS → "Cuotas")

---

## 5. Algoritmo Completo (Pseudocódigo)

```python
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

# Constantes de semanas de feriado
SEMANAS_FERIADO = [
    {"mes": 7, "dia_inicio": 28, "dia_fin": 29},  # Fiestas Patrias
    {"mes": 12, "dia_inicio": 25, "dia_fin": 25},  # Navidad
]

def es_semana_feriado(fecha):
    # Determina si una fecha cae en una semana de feriado
    for feriado in SEMANAS_FERIADO:
        feriado_fecha = date(fecha.year, feriado["mes"], feriado["dia_inicio"])
        lunes_feriado = feriado_fecha - timedelta(days=feriado_fecha.weekday())
        domingo_feriado = lunes_feriado + timedelta(days=6)
        
        if lunes_feriado <= fecha <= domingo_feriado:
            return True
    return False

def contar_semanas_feriado_entre(fecha_inicio, fecha_fin):
    # Cuenta cuántas semanas de feriado hay entre dos fechas
    contador = 0
    for feriado in SEMANAS_FERIADO:
        feriado_fecha = date(fecha_inicio.year, feriado["mes"], feriado["dia_inicio"])
        lunes_feriado = feriado_fecha - timedelta(days=feriado_fecha.weekday())
        
        if fecha_inicio <= lunes_feriado <= fecha_fin:
            contador += 1
    return contador

def calcular_traslado(fecha_traslado, ciclo_origen_data, ciclo_destino_data, parametros):
    # Calcula el resultado económico de un traslado académico
    
    # PASO 1: Validar que ambos ciclos existan en parámetros
    ciclo_origen = buscar_ciclo(parametros, ciclo_origen_data)
    if ciclo_origen is None:
        raise ValueError("Ciclo origen no encontrado en la base de datos")
    
    ciclo_destino = buscar_ciclo(parametros, ciclo_destino_data)
    if ciclo_destino is None:
        raise ValueError("Ciclo destino no encontrado en la base de datos")
    
    # PASO 2: Validar modalidad de pago (deben ser iguales)
    pago_en = ciclo_origen_data['pago_en']  # CONTADO o CUOTAS
    if pago_en != ciclo_destino_data['pago_en']:
        raise ValueError(
            "No se permiten traslados entre modalidades de pago diferentes. "
            "Si requiere este tipo de traslado, debe procesarlo manualmente."
        )
    
    # PASO 3: Validar fecha dentro del rango de ambos ciclos
    fecha_inicio_origen = date.fromisoformat(ciclo_origen['fecha_inicio'])
    fecha_fin_origen = date.fromisoformat(ciclo_origen['fecha_fin'])
    fecha_inicio_destino = date.fromisoformat(ciclo_destino['fecha_inicio'])
    fecha_fin_destino = date.fromisoformat(ciclo_destino['fecha_fin'])
    
    if not (fecha_inicio_origen <= fecha_traslado <= fecha_fin_origen):
        raise ValueError(f"La fecha de traslado está fuera del rango del ciclo origen ({ciclo_origen['nombre']})")
    
    if not (fecha_inicio_destino <= fecha_traslado <= fecha_fin_destino):
        raise ValueError(f"La fecha de traslado está fuera del rango del ciclo destino ({ciclo_destino['nombre']})")
    
    # PASO 4: Calcular semanas consumidas para ambos ciclos (con ajuste de feriados)
    semanas_consumidas_origen = calcular_semanas_consumidas(fecha_traslado, fecha_inicio_origen)
    semanas_consumidas_destino = calcular_semanas_consumidas(fecha_traslado, fecha_inicio_destino)
    
    # PASO 5: Calcular valor residual según modalidad de pago
    if pago_en == 'CONTADO':
        plan_origen = ciclo_origen['payment_plans']['Contado']
        plan_destino = ciclo_destino['payment_plans']['Contado']
        
        saldo_origen = calcular_valor_contado(
            Decimal(str(plan_origen['cash_price'])),
            ciclo_origen['duration_weeks'],
            semanas_consumidas_origen,
            fecha_inicio_origen,
            fecha_fin_origen
        )
        costo_destino = calcular_valor_contado(
            Decimal(str(plan_destino['cash_price'])),
            ciclo_destino['duration_weeks'],
            semanas_consumidas_destino,
            fecha_inicio_destino,
            fecha_fin_destino
        )
    else:  # CUOTAS
        plan_origen = ciclo_origen['payment_plans']['Cuotas']
        plan_destino = ciclo_destino['payment_plans']['Cuotas']
        
        saldo_origen = calcular_valor_cuotas(
            plan_origen['installments'],
            fecha_traslado
        )
        costo_destino = calcular_valor_cuotas(
            plan_destino['installments'],
            fecha_traslado
        )
    
    # PASO 6: Calcular diferencia
    diferencia = saldo_origen - costo_destino
    
    # PASO 7: Generar mensaje según resultado
    if diferencia > 0:
        mensaje = f"Saldo a favor: S/ {diferencia:.2f}"
        estado = "SALDO_A_FAVOR"
    elif diferencia < 0:
        mensaje = f"Monto pendiente: S/ {abs(diferencia):.2f}"
        estado = "MONTO_PENDIENTE"
    else:
        mensaje = "Traslado cubierto exactamente"
        estado = "TRASLADO_CUBIERTO"
    
    return {
        'saldo_origen': float(saldo_origen),
        'costo_destino': float(costo_destino),
        'diferencia': float(diferencia),
        'estado': estado,
        'mensaje': mensaje,
        'detalle': {
            'origen': {
                'semanas_totales': ciclo_origen['duration_weeks'],
                'semanas_consumidas': semanas_consumidas_origen,
                'semanas_restantes': ciclo_origen['duration_weeks'] - semanas_consumidas_origen
            },
            'destino': {
                'semanas_totales': ciclo_destino['duration_weeks'],
                'semanas_consumidas': semanas_consumidas_destino,
                'semanas_restantes': ciclo_destino['duration_weeks'] - semanas_consumidas_destino
            }
        }
    }


def buscar_ciclo(parametros, datos_ciclo):
    # Busca un ciclo en los parámetros según nombre, universidad y modalidad
    # El plan de pago se selecciona después según datos_ciclo['pago_en']
    for ciclo in parametros['ciclos']:
        if (ciclo['nombre'] == datos_ciclo['nombre'] and
            ciclo['universidad'] == datos_ciclo['universidad'] and
            ciclo['modalidad_academica'] == datos_ciclo['modalidad_academica']):
            return ciclo
    return None


def calcular_semanas_consumidas(fecha_traslado, fecha_inicio):
    # Calcula cuántas semanas se han consumido desde la fecha de inicio
    # Ajusta por semanas de feriado que se saltan en el calendario académico
    # 
    # Regla: 
    # - Lunes/Martes: la semana actual NO se ha consumido
    # - Miércoles a Domingo: la semana actual SÍ se ha consumido
    # - Las semanas de feriado NO se cuentan como semanas consumidas
    
    # Contar semanas de feriado entre inicio y traslado
    semanas_feriado = contar_semanas_feriado_entre(fecha_inicio, fecha_traslado)
    
    # Ajustar la fecha de traslado restando las semanas de feriado
    fecha_traslado_ajustada = fecha_traslado - timedelta(weeks=semanas_feriado)
    
    dias_transcurridos = (fecha_traslado_ajustada - fecha_inicio).days
    semanas_completas = dias_transcurridos // 7
    
    dia_semana = fecha_traslado_ajustada.weekday()  # 0=Lunes, 1=Martes, 2=Miércoles...
    
    if dia_semana in [0, 1]:  # Lunes o Martes
        return semanas_completas
    else:  # Miércoles a Domingo
        return semanas_completas + 1


def calcular_valor_contado(cash_price, duration_weeks, semanas_consumidas, fecha_inicio, fecha_fin):
    # Calcula el valor residual para modalidad CONTADO
    # El cash_price YA viene con descuento del Excel
    
    # Calcular semanas efectivas (incluyendo feriados)
    semanas_feriado = contar_semanas_feriado_entre(fecha_inicio, fecha_fin)
    semanas_efectivas = duration_weeks + semanas_feriado
    
    # Calcular valor residual
    semanas_restantes = semanas_efectivas - semanas_consumidas
    valor_semana = cash_price / semanas_efectivas
    valor = valor_semana * semanas_restantes
    
    return valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_valor_cuotas(installments, fecha_traslado):
    # Calcula el valor residual para modalidad CUOTAS
    # Las fechas de vencimiento y montos VIENEN DEL EXCEL
    
    cuotas_pendientes = Decimal('0.00')
    
    for cuota in installments:
        fecha_vencimiento = date.fromisoformat(cuota['due_date'])
        if fecha_vencimiento > fecha_traslado:
            cuotas_pendientes += Decimal(str(cuota['amount']))
    
    return cuotas_pendientes.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

---

## 6. Casos de Prueba (actualizados con datos del Excel)

### TC-1: Traslado CONTADO con saldo a favor
**Entradas:**
- **Fecha de traslado:** 15/05/2026
- **Ciclo Origen:**
  - Ciclo: ANUAL MARZO, Universidad: SM, Modalidad: PRESENCIAL, Pago: CONTADO
  - (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
- **Ciclo Destino:**
  - Ciclo: SEMIANUAL ENERO, Universidad: SM, Modalidad: VIRTUAL, Pago: CONTADO
  - (cash_price: S/ 1350, duration_weeks: 20, fecha_inicio: 05/01/2026, fecha_fin: 19/06/2026)

**Cálculo:**
- Origen: 15/05/2026 es viernes → semana consumida
- Semanas transcurridas: (15/05 - 16/03) = 60 días = 8 semanas + 4 días → 9 semanas consumidas
- No hay feriados entre marzo y mayo
- Semanas restantes: 40 - 9 = 31
- Saldo origen: (4590/40) × 31 = S/ 3557.25

- Destino: 15/05/2026 es viernes → semana consumida
- Semanas transcurridas: (15/05 - 05/01) = 130 días = 18 semanas + 4 días → 19 semanas consumidas
- Semanas restantes: 20 - 19 = 1
- Costo destino: (1350/20) × 1 = S/ 67.50

- Diferencia: 3557.25 - 67.50 = S/ 3489.75

**Resultado esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 3489.75"

---

### TC-2: Traslado CONTADO con monto pendiente
**Entradas:**
- **Fecha de traslado:** 20/03/2026
- **Ciclo Origen:**
  - Ciclo: SEMIANUAL ENERO, Universidad: SM, Modalidad: VIRTUAL, Pago: CONTADO
  - (cash_price: S/ 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)
- **Ciclo Destino:**
  - Ciclo: ANUAL MARZO, Universidad: SM, Modalidad: PRESENCIAL, Pago: CONTADO
  - (cash_price: S/ 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)

**Cálculo:**
- Origen: 20/03/2026 es viernes → semana consumida
- Semanas transcurridas: (20/03 - 05/01) = 74 días = 10 semanas + 4 días → 11 semanas consumidas
- Semanas restantes: 20 - 11 = 9
- Saldo origen: (1350/20) × 9 = S/ 607.50

- Destino: 20/03/2026 es viernes → semana consumida
- Semanas transcurridas: (20/03 - 16/03) = 4 días → 1 semana consumida
- Semanas restantes: 40 - 1 = 39
- Costo destino: (4590/40) × 39 = S/ 4475.25

- Diferencia: 607.50 - 4475.25 = -S/ 3867.75

**Resultado esperado:**
- Estado: MONTO_PENDIENTE
- Mensaje: "Monto pendiente: S/ 3867.75"

---

### TC-3: Traslado CUOTAS cubierto exactamente (mismas cuotas)
**Entradas:**
- **Fecha de traslado:** 20/04/2026
- **Ciclo Origen:**
  - Ciclo: ANUAL MARZO, Universidad: SM, Modalidad: PRESENCIAL, Pago: CUOTAS
  - Cuotas del Excel (10 cuotas de S/ 510)
- **Ciclo Destino:**
  - Ciclo: ANUAL MARZO, Universidad: UNI, Modalidad: VIRTUAL, Pago: CUOTAS
  - Mismas cuotas del Excel (10 cuotas de S/ 510)

**Cálculo:**
- Origen: Cuotas pendientes después del 20/04/2026:
  - Cuota 1: 16/03/2026 → vencida
  - Cuota 2: 11/04/2026 → vencida (20/04 > 11/04)
  - Cuota 3: 09/05/2026 → pendiente
  - Cuotas 3 a 10: 8 cuotas × 510 = S/ 4080.00

- Destino: Mismas cuotas → S/ 4080.00

- Diferencia: 4080 - 4080 = S/ 0.00

**Resultado esperado:**
- Estado: TRASLADO_CUBIERTO
- Mensaje: "Traslado cubierto exactamente"

---

### TC-4: Modalidad de pago diferente (bloqueo)
**Entradas:**
- **Fecha de traslado:** 15/05/2026
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CONTADO
- **Ciclo Destino:** ANUAL MARZO, UNI, VIRTUAL, CUOTAS

**Resultado esperado:**
- Error: "No se permiten traslados entre modalidades de pago diferentes. Si requiere este tipo de traslado, debe procesarlo manualmente."

---

### TC-5: Fecha fuera del rango del ciclo origen
**Entradas:**
- **Fecha de traslado:** 15/01/2026
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CONTADO (fecha_inicio: 16/03/2026)
- **Ciclo Destino:** SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (fecha_inicio: 05/01/2026)

**Resultado esperado:**
- Error: "La fecha de traslado está fuera del rango del ciclo origen (ANUAL MARZO)"

---

### TC-6: Lunes - semana no consumida
**Entradas:**
- **Fecha de traslado:** 13/04/2026 (lunes)
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- **Ciclo Destino:** SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Cálculo:**
- Origen: 13/04/2026 es lunes → semana NO consumida
- Semanas transcurridas: (13/04 - 16/03) = 28 días = 4 semanas → 4 semanas consumidas
- Semanas restantes: 40 - 4 = 36
- Saldo origen: (4590/40) × 36 = S/ 4131.00

**Resultado esperado:**
- Saldo origen: S/ 4131.00 (la semana del 13/04 no se cuenta como consumida)

---

### TC-7: Martes - semana no consumida
**Entradas:**
- **Fecha de traslado:** 14/04/2026 (martes)
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- **Ciclo Destino:** SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Cálculo:**
- Origen: 14/04/2026 es martes → semana NO consumida
- Semanas transcurridas: (14/04 - 16/03) = 29 días = 4 semanas + 1 día → 4 semanas consumidas
- Semanas restantes: 40 - 4 = 36
- Saldo origen: (4590/40) × 36 = S/ 4131.00

**Resultado esperado:**
- Saldo origen: S/ 4131.00 (igual que TC-6)

---

### TC-8: Miércoles - semana SÍ consumida
**Entradas:**
- **Fecha de traslado:** 15/04/2026 (miércoles)
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026)
- **Ciclo Destino:** SEMIANUAL ENERO, SM, VIRTUAL, CONTADO (cash_price: 1350, duration_weeks: 20, fecha_inicio: 05/01/2026)

**Cálculo:**
- Origen: 15/04/2026 es miércoles → semana SÍ consumida
- Semanas transcurridas: (15/04 - 16/03) = 30 días = 4 semanas + 2 días → 5 semanas consumidas
- Semanas restantes: 40 - 5 = 35
- Saldo origen: (4590/40) × 35 = S/ 4016.25

**Resultado esperado:**
- Saldo origen: S/ 4016.25 (miércoles cuenta como semana consumida)

---

### TC-9: Traslado CUOTAS con saldo a favor (cuotas diferentes)
**Entradas:**
- **Fecha de traslado:** 25/05/2026
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CUOTAS (10 cuotas de S/ 510)
- **Ciclo Destino:** ANUAL MARZO, UNI, VIRTUAL, CUOTAS (8 cuotas de S/ 400)

**Cálculo:**
- Origen: Cuotas pendientes después del 25/05/2026:
  - Cuota 1: 16/03 → vencida
  - Cuota 2: 11/04 → vencida
  - Cuota 3: 09/05 → vencida (25/05 > 09/05)
  - Cuota 4: 06/06 → pendiente
  - Cuotas 4 a 10: 7 cuotas × 510 = S/ 3570.00

- Destino: Cuotas pendientes después del 25/05/2026:
  - Cuota 1: 16/03 → vencida
  - Cuota 2: 11/04 → vencida
  - Cuota 3: 09/05 → vencida
  - Cuota 4: 06/06 → pendiente
  - Cuotas 4 a 8: 5 cuotas × 400 = S/ 2000.00

- Diferencia: 3570 - 2000 = S/ 1570.00

**Resultado esperado:**
- Estado: SALDO_A_FAVOR
- Mensaje: "Saldo a favor: S/ 1570.00"

---

### TC-10: Ciclo no encontrado
**Entradas:**
- **Fecha de traslado:** 15/05/2026
- **Ciclo Origen:** CICLO INEXISTENTE, SM, PRESENCIAL, CONTADO
- **Ciclo Destino:** SEMIANUAL ENERO, SM, VIRTUAL, CONTADO

**Resultado esperado:**
- Error: "Ciclo origen no encontrado en la base de datos"

---

### TC-11: Semana de feriado - traslado durante feriado de julio
**Entradas:**
- **Fecha de traslado:** 29/07/2026 (miércoles, durante Fiestas Patrias)
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)
- **Ciclo Destino:** ANUAL MARZO, UNI, VIRTUAL, CONTADO (cash_price: 4590, duration_weeks: 40, fecha_inicio: 16/03/2026, fecha_fin: 31/12/2026)

**Cálculo:**
- La semana del 29/07 es semana de feriado → se salta
- Fecha ajustada: 29/07 - 7 días = 22/07/2026
- 22/07 es miércoles → semana SÍ consumida
- Semanas transcurridas: (22/07 - 16/03) = 128 días = 18 semanas + 2 días → 19 semanas consumidas
- Semanas efectivas: 40 + 1 (julio) + 1 (diciembre) = 42
- Semanas restantes: 42 - 19 = 23
- Saldo = Costo = (4590/42) × 23 = S/ 2513.57

**Resultado esperado:**
- Estado: TRASLADO_CUBIERTO
- Diferencia: S/ 0.00

---

### TC-12: Cuota con vencimiento en semana de feriado (datos del Excel)
**Entradas:**
- **Fecha de traslado:** 01/08/2026
- **Ciclo Origen:** ANUAL MARZO, SM, PRESENCIAL, CUOTAS
- **Cuota 6:** due_date 08/08/2026 (después del feriado de julio, ya ajustada en el Excel)

**Nota:**
- El Excel YA tiene las fechas ajustadas. Si una cuota cayera en semana de feriado, el Excel la habría movido.
- El sistema usa las fechas del Excel directamente, no las recalcula.

**Resultado esperado:**
- Cuota 6 (08/08/2026) está pendiente (01/08 < 08/08)
- Valor residual incluye cuota 6 y siguientes

---

## 7. Validaciones en Cascada

El sistema debe validar en el siguiente orden y detenerse en el primer error:

1. **Existencia de ciclos**
   - Validar que ciclo origen exista en parameters.json
   - Validar que ciclo destino exista en parameters.json

2. **Modalidad de pago igual**
   - Validar que pago_en_origen == pago_en_destino

3. **Fecha dentro del rango**
   - Validar que fecha_traslado esté entre fecha_inicio y fecha_fin del ciclo origen
   - Validar que fecha_traslado esté entre fecha_inicio y fecha_fin del ciclo destino

4. **Cálculo exitoso**
   - Ejecutar el algoritmo de cálculo
   - Retornar resultado

---

## 8. Salida del Sistema

```json
{
  "success": true,
  "resultado": {
    "saldo_origen": 3557.25,
    "costo_destino": 67.50,
    "diferencia": 3489.75,
    "estado": "SALDO_A_FAVOR",
    "mensaje": "Saldo a favor: S/ 3489.75",
    "detalle": {
      "origen": {
        "semanas_totales": 40,
        "semanas_consumidas": 9,
        "semanas_restantes": 31
      },
      "destino": {
        "semanas_totales": 20,
        "semanas_consumidas": 19,
        "semanas_restantes": 1
      }
    }
  }
}
```

---

## 9. Consideraciones Finales

### Datos del Excel
- **`fecha_inicio`** y **`fecha_fin`** vienen del Excel directamente
- **`duration_weeks`** viene del Excel (puede ser diferente a las semanas reales del calendario)
- **`payment_plans`** contiene los planes "Contado" y "Cuotas" con sus cuotas respectivas
- **`cash_price`** en Contado ya incluye el descuento (ej: 4590 = 5100 - 10%)
- **`total`** es la suma de todas las cuotas (sin descuento)
- Las **`due_date`** de cada cuota vienen del Excel, ya ajustadas por feriados si aplica

### Semanas de feriado
- Julio 28-29 (Fiestas Patrias): 1 semana cancelada
- Diciembre 25 (Navidad): 1 semana cancelada
- Estas semanas se "saltan" en los cálculos de semanas consumidas/restantes
- Las cuotas del Excel ya vienen con fechas ajustadas (si aplica)

### Descuento del 10% al contado
- El Excel ya entrega el `cash_price` con descuento aplicado
- No es necesario calcular el descuento en el sistema
- Ejemplo: total=5100, discount_percent=10, cash_price=4590

### Redondeo
- Todos los montos usan `decimal.Decimal` para evitar errores de punto flotante
- Redondeo: `ROUND_HALF_UP` a 2 decimales (0.5 sube, 0.49 baja)

### Manejo de errores
- Todos los errores deben retornar mensajes claros al usuario
- No procesar cálculos si hay validaciones fallidas

### Extensibilidad
- La estructura de parameters.json permite agregar nuevos ciclos sin modificar el código
- Las semanas de feriado están definidas como constantes
- El algoritmo es independiente de la interfaz de usuario

---

## 10. Referencias

- **Constitución del Proyecto**: Art. 3 (Quality Standards), Art. 4 (Architecture Principles), Art. 7 (Boundaries)
- **Especificación**: spec.md (US-1, US-2, FR-001 a FR-008)
- **Plan**: plan.md (Módulos de Captura, Validación, Cálculo, Resultados)
- **Decisiones**: decisions.md (Stack Python + Flask, separación de responsabilidades)
