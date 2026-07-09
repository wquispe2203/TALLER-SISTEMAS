# -*- coding: utf-8 -*-
import os
import sys
from datetime import date
from decimal import Decimal

# Permite ejecutar este archivo directamente como "python test_traslados.py"
# desde cualquier directorio (no solo via "python -m pytest" desde zproyect/),
# agregando zproyect/ (el padre de esta carpeta test/) al import path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traslados import (
    CicloInput,
    cargar_parametros,
    calcular_traslado,
    calcular_traslado_seguro,
    contar_semanas_feriado_entre,
    obtener_semanas_feriado_lunes,
    generar_pasos_cuotas,
    generar_pasos_contado,
    TrasladoError,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARAMETROS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "parameters.json"))
PARAMS = cargar_parametros(PARAMETROS_PATH)


def check(nombre, cond):
    print(("OK  " if cond else "FAIL"), nombre)
    assert cond, nombre


# ---------------------------------------------------------------------------
# Fix de semanas feriado: 28/29 julio en la misma semana vs semanas distintas
# ---------------------------------------------------------------------------

# 2026: 28 y 29 julio en la MISMA semana -> 1 sola semana feriado en julio
lunes_2026 = obtener_semanas_feriado_lunes(2026)
check("2026: 28 y 29 julio colapsan a 1 semana (+1 de diciembre = 2 en total)", len(lunes_2026) == 2)

# 2030: 28/07 es domingo, 29/07 es lunes -> semanas DISTINTAS -> 2 semanas en julio + 1 en dic = 3
lunes_2030 = obtener_semanas_feriado_lunes(2030)
check("2030: 28 y 29 julio caen en semanas distintas (2 semanas) + diciembre = 3 en total", len(lunes_2030) == 3)

# contar_semanas_feriado_entre debe reflejar esto en un ciclo anual completo
semanas_feriado_2026 = contar_semanas_feriado_entre(date(2026, 1, 1), date(2026, 12, 31))
check("Ciclo 2026 completo: 2 semanas de feriado (julio colapsado + diciembre)", semanas_feriado_2026 == 2)

semanas_feriado_2030 = contar_semanas_feriado_entre(date(2030, 1, 1), date(2030, 12, 31))
check("Ciclo 2030 completo: 3 semanas de feriado (julio partido en 2 + diciembre)", semanas_feriado_2030 == 3)


# ---------------------------------------------------------------------------
# TC-1: Traslado CONTADO con saldo a favor (usa datos reales de parameters.json)
# ---------------------------------------------------------------------------
origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")  # mismo ciclo real distinto modalidad
r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
det = r["resultado"]["detalle"]["origen"]
check("TC-1: semanas consumidas origen = 9", det["semanas_consumidas"] == 9)
# CORREGIDO 2026-07-09: los feriados NO se cobran al alumno. Anteriormente se
# sumaban al denominador (duration_weeks + feriados = 42), diluyendo el costo.
# Ahora duration_weeks (40) se usa directamente: valor_semana = 4590/40 = 114.75,
# semanas_restantes = 40-9 = 31, saldo = 114.75*31 = 3557.25.
check("TC-1: saldo_origen == 3557.25 (feriados excluidos, /40)", r["resultado"]["saldo_origen"] == 3557.25)
check("TC-1: costo_destino == 2511.00 (3240/40*31)", r["resultado"]["costo_destino"] == 2511.00)
# detalle ahora usa duration_weeks (no + feriados) porque los feriados no se cobran.
check("TC-1: detalle.semanas_totales == duration_weeks (40)", det["semanas_totales"] == 40)
check("TC-1: detalle.semanas_restantes == 40 - 9 = 31", det["semanas_restantes"] == 31)
check("TC-1: detalle incluye 'pasos' (desglose humano, FR-010)", len(det["pasos"]) > 0)
print("   -> ", r["resultado"]["mensaje"])


# ---------------------------------------------------------------------------
# TC-6 / TC-7 / TC-8: regla lunes/martes no consumida, miércoles sí consumida
# ---------------------------------------------------------------------------
origen40 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
destino40 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")

# CORREGIDO 2026-07-09: feriados excluidos (÷40 en vez de ÷42). Los valores
# correctos son 4131.00 / 4016.25. Lo que se preserva es que lunes y martes
# dan el mismo resultado, y miércoles da un valor menor.
r_lunes = calcular_traslado(date(2026, 4, 13), origen40, destino40, PARAMS)  # lunes
check("TC-6 lunes: saldo_origen == 4131.00", r_lunes["resultado"]["saldo_origen"] == 4131.00)

r_martes = calcular_traslado(date(2026, 4, 14), origen40, destino40, PARAMS)  # martes
check("TC-7 martes: saldo_origen == 4131.00 (igual que lunes)", r_martes["resultado"]["saldo_origen"] == r_lunes["resultado"]["saldo_origen"])

r_miercoles = calcular_traslado(date(2026, 4, 15), origen40, destino40, PARAMS)  # miércoles
check("TC-8 miércoles: saldo_origen == 4016.25 (sí consumida, menor que lunes/martes)", r_miercoles["resultado"]["saldo_origen"] == 4016.25)
check("TC-8 < TC-6 (miércoles consume una semana más que lunes)", r_miercoles["resultado"]["saldo_origen"] < r_lunes["resultado"]["saldo_origen"])


# ---------------------------------------------------------------------------
# TC-3 / TC-9 (test-cases.md): CUOTAS con saldo a favor — prorrateo de la
# cuota vigente (mismo ciclo, distinta modalidad).
#
# CORREGIDO 2026-07-07: esta aserción esperaba 4080.00 (= 510 x 8 cuotas
# futuras completas), que era la fórmula ANTERIOR a la adopción del
# algoritmo v4 (ver decisions.md, entrada 2026-07-04). El algoritmo real
# prorratea SOLO la cuota vigente a la fecha de traslado
# (calcular_valor_cuotas / _prorratear_cuota), no suma cuotas futuras.
# Para el 20/04/2026 la cuota vigente es la cuota 2 (periodo 11/04-09/05,
# 4 semanas), con 1 semana consumida y 3 restantes: 510 x 3/4 = 382.50.
# ---------------------------------------------------------------------------
origen_c = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
destino_c = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
r3 = calcular_traslado(date(2026, 4, 20), origen_c, destino_c, PARAMS)
check("TC-3/TC-9: saldo_origen == 382.50 (cuota 2 prorrateada, no 8 cuotas completas)", r3["resultado"]["saldo_origen"] == 382.50)
check("TC-3/TC-9: costo_destino == 270.00 (cash_price distinto: cuota de 360)", r3["resultado"]["costo_destino"] == 270.00)
check("TC-3/TC-9: diferencia == 112.50, SALDO_A_FAVOR", r3["resultado"]["diferencia"] == 112.50 and r3["resultado"]["estado"] == "SALDO_A_FAVOR")
det3 = r3["resultado"]["detalle"]["origen"]
check("TC-3/TC-9: detalle refleja el periodo de la cuota vigente (4 semanas totales, no las 40 del ciclo)", det3["semanas_totales"] == 4)
check("TC-3/TC-9: detalle.semanas_consumidas == 1, semanas_restantes == 3", det3["semanas_consumidas"] == 1 and det3["semanas_restantes"] == 3)
check("TC-3/TC-9: pasos menciona la cuota 2", any("cuota 2" in p for p in det3["pasos"]))
print("   -> ", r3["resultado"]["mensaje"])


# ---------------------------------------------------------------------------
# AC-3.4 (spec.md) / TC-14 (test-cases.md): desglose humano CUOTAS
# Ejemplo verificado manualmente por el usuario y confirmado contra el
# código real: 25/03/2026, ANUAL MARZO SM Presencial->Virtual CUOTAS.
# ---------------------------------------------------------------------------
o14 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
d14 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
r14 = calcular_traslado(date(2026, 3, 25), o14, d14, PARAMS)
check("AC-3.4/TC-14: saldo_origen == 382.50", r14["resultado"]["saldo_origen"] == 382.50)
check("AC-3.4/TC-14: costo_destino == 270.00", r14["resultado"]["costo_destino"] == 270.00)
check("AC-3.4/TC-14: diferencia == 112.50, SALDO_A_FAVOR", r14["resultado"]["diferencia"] == 112.50 and r14["resultado"]["estado"] == "SALDO_A_FAVOR")
det14 = r14["resultado"]["detalle"]["origen"]
check("AC-3.4/TC-14: cuota vigente es la 1, periodo de 4 semanas, 1 consumida, 3 restantes",
      det14["semanas_totales"] == 4 and det14["semanas_consumidas"] == 1 and det14["semanas_restantes"] == 3)
check("AC-3.4/TC-14: pasos menciona la cuota 1 y el periodo 16/03/2026 al 11/04/2026",
      any("cuota 1" in p and "16/03/2026" in p and "11/04/2026" in p for p in det14["pasos"]))


# ---------------------------------------------------------------------------
# AC-3.5 (spec.md) / TC-15 (test-cases.md): desglose humano CONTADO
# CORREGIDO 2026-07-09: feriados excluidos del cálculo. El ciclo SEMIANUAL
# MARZO tiene 1 feriado en su rango (Fiestas Patrias), pero NO se suma al
# denominador. duration_weeks=28 es el total de semanas de clase.
# ---------------------------------------------------------------------------
o15 = CicloInput("SEMIANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
d15 = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
r15 = calcular_traslado(date(2026, 5, 15), o15, d15, PARAMS)
check("AC-3.5/TC-15: saldo_origen == 2180.25 (3213/28*19)", r15["resultado"]["saldo_origen"] == 2180.25)
check("AC-3.5/TC-15: costo_destino == 1539.00 (2268/28*19)", r15["resultado"]["costo_destino"] == 1539.00)
check("AC-3.5/TC-15: diferencia == 641.25, SALDO_A_FAVOR", r15["resultado"]["diferencia"] == 641.25 and r15["resultado"]["estado"] == "SALDO_A_FAVOR")
det15 = r15["resultado"]["detalle"]["origen"]
check("AC-3.5/TC-15: semanas de clase 28, 9 consumidas, 19 restantes",
      det15["semanas_totales"] == 28 and det15["semanas_consumidas"] == 9 and det15["semanas_restantes"] == 19)
check("AC-3.5/TC-15: pasos menciona la semana 9 y que el 15/05/2026 es viernes",
      any("semana 9" in p for p in det15["pasos"]) and any("viernes" in p for p in det15["pasos"]))


# ---------------------------------------------------------------------------
# TC-4: Modalidad de pago diferente -> bloqueo
# ---------------------------------------------------------------------------
o4 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
d4 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
try:
    calcular_traslado(date(2026, 5, 15), o4, d4, PARAMS)
    check("TC-4 debía lanzar TrasladoError", False)
except TrasladoError as e:
    check("TC-4: bloqueo por modalidad de pago diferente", "modalidades de pago diferentes" in str(e))


# ---------------------------------------------------------------------------
# TC-5: Fecha fuera de rango del ciclo origen
# ---------------------------------------------------------------------------
o5 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
d5 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
try:
    calcular_traslado(date(2026, 1, 15), o5, d5, PARAMS)  # antes del 16/3/2026
    check("TC-5 debía lanzar TrasladoError", False)
except TrasladoError as e:
    check("TC-5: fuera de rango ciclo origen", "fuera del rango" in str(e))


# ---------------------------------------------------------------------------
# TC-10: Ciclo no encontrado
# ---------------------------------------------------------------------------
o10 = CicloInput("CICLO INEXISTENTE", "SM", "PRESENCIAL", "CONTADO")
d10 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
r10 = calcular_traslado_seguro(date(2026, 5, 15), o10, d10, PARAMS)
check("TC-10: ciclo origen no encontrado (modo seguro)", r10 == {"success": False, "error": "Ciclo origen no encontrado en la base de datos"})


# ---------------------------------------------------------------------------
# TC-12: Traslado CONTADO durante semana de feriado (Fiestas Patrias 2026)
# CORREGIDO 2026-07-09: feriados excluidos del cálculo. Anteriormente se
# sumaban al denominador. Ahora: valor_semana=4590/40, restantes=40-19=21,
# saldo=2409.75 (vs 2513.57 con la fórmula antigua ÷42).
# ---------------------------------------------------------------------------
o_fer = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
d_fer = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
r_fer = calcular_traslado(date(2026, 7, 29), o_fer, d_fer, PARAMS)
check("TC-12: saldo_origen == 2409.75 (4590/40*(40-19))", r_fer["resultado"]["saldo_origen"] == 2409.75)
check("TC-12: costo_destino == 1701.00 (3240/40*21)", r_fer["resultado"]["costo_destino"] == 1701.00)
check("TC-12: diferencia == 708.75, SALDO_A_FAVOR", r_fer["resultado"]["diferencia"] == 708.75 and r_fer["resultado"]["estado"] == "SALDO_A_FAVOR")
det_fer = r_fer["resultado"]["detalle"]["origen"]
check("TC-12: semanas de clase 40, 19 consumidas (feriado excluido), 21 restantes",
      det_fer["semanas_totales"] == 40 and det_fer["semanas_consumidas"] == 19 and det_fer["semanas_restantes"] == 21)
print("   -> ", r_fer["resultado"]["mensaje"])


# ---------------------------------------------------------------------------
# TC-13: CUOTAS con feriado en el periodo de la cuota vigente (05/08/2026)
# CORREGIDO 2026-07-09: feriados excluidos. Cuota 5 de ANUAL MARZO tiene
# periodo 04/07-08/08 (5 semanas calendario, 1 feriado = 4 semanas reales).
# Con nueva fórmula: semanas_totales=4, consumidas=3, restantes=1.
# saldo_origen=510*1/4=127.50, costo_destino=360*1/4=90.00.
# ---------------------------------------------------------------------------
o13 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
d13 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
r13 = calcular_traslado(date(2026, 8, 5), o13, d13, PARAMS)
check("TC-13: saldo_origen == 127.50 (510*1/4, feriado excluido del total)", r13["resultado"]["saldo_origen"] == 127.50)
check("TC-13: costo_destino == 90.00 (360*1/4)", r13["resultado"]["costo_destino"] == 90.00)
check("TC-13: diferencia == 37.50, SALDO_A_FAVOR", r13["resultado"]["diferencia"] == 37.50 and r13["resultado"]["estado"] == "SALDO_A_FAVOR")
det13 = r13["resultado"]["detalle"]["origen"]
check("TC-13: semanas totales 4 (5-1 feriado), 3 consumidas, 1 restante",
      det13["semanas_totales"] == 4 and det13["semanas_consumidas"] == 3 and det13["semanas_restantes"] == 1)
print("   -> ", r13["resultado"]["mensaje"])


# ---------------------------------------------------------------------------
# FR-011 / AC-3.6 / AC-3.7 / AC-3.8 / CB-9 / CB-10: campos estructurados
# fecha_inicio_periodo, fecha_fin_periodo, semana_actual en detalle.
# Producido vía SDD Enterprise real (Requirement Analyst -> Architect ADR-4
# -> esta implementación), ver spec.md y plan.md, 2026-07-07.
# ---------------------------------------------------------------------------

# AC-3.6: CONTADO
o36 = CicloInput("SEMIANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
d36 = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
r36 = calcular_traslado(date(2026, 5, 15), o36, d36, PARAMS)
det36 = r36["resultado"]["detalle"]["origen"]
check("AC-3.6: fecha_inicio_periodo == 16/03/2026", det36["fecha_inicio_periodo"] == "16/03/2026")
check("AC-3.6: fecha_fin_periodo == 02/10/2026", det36["fecha_fin_periodo"] == "02/10/2026")
check("AC-3.6: semana_actual == 9", det36["semana_actual"] == 9)

# AC-3.7: CUOTAS
o37 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
d37 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
r37 = calcular_traslado(date(2026, 3, 25), o37, d37, PARAMS)
det37 = r37["resultado"]["detalle"]["origen"]
check("AC-3.7: fecha_inicio_periodo == 16/03/2026 (periodo de la cuota, no del ciclo)", det37["fecha_inicio_periodo"] == "16/03/2026")
check("AC-3.7: fecha_fin_periodo == 11/04/2026", det37["fecha_fin_periodo"] == "11/04/2026")
check("AC-3.7: semana_actual == 2", det37["semana_actual"] == 2)

# AC-3.8: simetría origen/destino (mismos campos calculados con la data del destino)
check("AC-3.8: destino tiene los mismos 3 campos que origen", all(k in r36["resultado"]["detalle"]["destino"] for k in ("fecha_inicio_periodo", "fecha_fin_periodo", "semana_actual")))

# CB-9: fecha de traslado en el fin exacto del ciclo (CUOTAS) -> caso "fuera_de_ciclo", todo null
o_cb9 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
d_cb9 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
r_cb9 = calcular_traslado(date(2026, 12, 31), o_cb9, d_cb9, PARAMS)
det_cb9 = r_cb9["resultado"]["detalle"]["origen"]
check("CB-9: fuera_de_ciclo -> fecha_inicio_periodo es None", det_cb9["fecha_inicio_periodo"] is None)
check("CB-9: fuera_de_ciclo -> fecha_fin_periodo es None", det_cb9["fecha_fin_periodo"] is None)
check("CB-9: fuera_de_ciclo -> semana_actual es None (no 0, no omitido)", det_cb9["semana_actual"] is None)

# CB-10: CONTADO en el último día del ciclo -> semana_actual no debe exceder semanas_totales.
# NOTA (hallazgo del agente Review, 2026-07-07): con datos reales de parameters.json el
# clamp NUNCA se activa -- en ningún ciclo real el índice crudo excede semanas_efectivas,
# así que "<=" siempre es trivialmente cierto incluso si se borra el clamp del código
# (verificado con mutation testing por el Review). Se deja este caso con datos reales como
# smoke test, y se agrega abajo un caso SINTÉTICO (mismo tratamiento que CB-8) que sí fuerza
# el clamp: duration_weeks=1 sobre un rango de 2 semanas calendario, con fecha_traslado en
# la 2da semana -> sin clamp semana_actual sería 2, con clamp debe ser 1.
o_cb10 = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
d_cb10 = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
r_cb10 = calcular_traslado(date(2026, 12, 31), o_cb10, d_cb10, PARAMS)
det_cb10 = r_cb10["resultado"]["detalle"]["origen"]
check("CB-10 (smoke, datos reales): semana_actual <= semanas_totales", det_cb10["semana_actual"] <= det_cb10["semanas_totales"])

pasos_cb10b, det_cb10b = generar_pasos_contado(
    "Ciclo sintético (unit test CB-10, fuerza el clamp)",
    date(2026, 3, 23),   # fecha_traslado: lunes de la 2da semana calendario del rango
    date(2026, 3, 16),   # fecha_inicio: lunes
    date(2026, 3, 30),   # fecha_fin: 2 semanas calendario después
    1,                   # duration_weeks = 1 (deliberadamente menor a lo que el calendario da)
    Decimal("100"),
)
check("CB-10 (sintético): semana_actual == 1 (clamp activo; sin clamp sería 2)", det_cb10b["semana_actual"] == 1)
check("CB-10 (sintético): semana_actual == semanas_totales (invariante al límite)", det_cb10b["semana_actual"] == det_cb10b["semanas_totales"])

# CB-8: "antes_primera_cuota" -- NOTA: ningún ciclo real de parameters.json puede
# ejercitar esta rama (la cuota 1 de todos los ciclos usa "En la matrícula",
# que hace fallback a la propia fecha de inicio del ciclo, y fecha_traslado
# nunca puede ser anterior a esa fecha por la validación de PASO 3). Se
# ejercita la rama directamente con datos sintéticos de cuotas (NO un ciclo
# inventado en parameters.json/spec.md -- solo el input de esta función),
# documentado así explícitamente en vez de fabricar un ciclo falso.
installments_sinteticas = [
    {"number": 1, "amount": 500, "due_date": "01/06/2026"},
    {"number": 2, "amount": 500, "due_date": "01/07/2026"},
]
pasos_cb8, det_cb8 = generar_pasos_cuotas(
    "Ciclo sintético (unit test CB-8)",
    installments_sinteticas,
    date(2026, 5, 15),  # antes del vencimiento de la cuota 1 (01/06/2026)
    date(2026, 5, 1),   # fecha_inicio_ciclo (anterior a la fecha de traslado, para pasar validación externa si se usara)
    date(2026, 12, 31),
)
check("CB-8 (sintético): fecha_inicio_periodo es None (ningún periodo ha empezado)", det_cb8["fecha_inicio_periodo"] is None)
check("CB-8 (sintético): fecha_fin_periodo == vencimiento de la cuota 1 (01/06/2026)", det_cb8["fecha_fin_periodo"] == "01/06/2026")
check("CB-8 (sintético): semana_actual == 1", det_cb8["semana_actual"] == 1)
check("CB-8 (sintético): valor == monto completo de la cuota 1 (500.00)", det_cb8["valor"] == Decimal("500.00"))


# ---------------------------------------------------------------------------
# AC-014 a AC-016: Narrativa paso a paso (TC-021 a TC-026)
# ---------------------------------------------------------------------------

# Reusamos variables existentes:
#   r14 = CUOTAS, 25/03/2026, ANUAL MARZO, cuota 1 vigente
#   r15 = CONTADO, 15/05/2026, SEMIANUAL MARZO

det_ac14 = r14["resultado"]["detalle"]["origen"]
pasos_cuotas = det_ac14["pasos"]
check("TC-021: CUOTAS identifica cuota vigente con número y fechas",
      any("cuota 1" in p and "16/03/2026" in p and "11/04/2026" in p for p in pasos_cuotas))
check("TC-022: CUOTAS incluye días del periodo y semanas equivalentes",
      any("días" in p and "semana(s)" in p for p in pasos_cuotas))
check("TC-023: CUOTAS incluye semanas consumidas y restantes",
      any("Semanas consumidas del periodo" in p and "Semanas restantes" in p for p in pasos_cuotas))
check("TC-024: CUOTAS incluye fórmula monto × restantes ÷ totales",
      any("×" in p and "÷" in p for p in pasos_cuotas))

det_ac16_contado = r15["resultado"]["detalle"]["origen"]
pasos_contado = det_ac16_contado["pasos"]
check("TC-025: CONTADO menciona inicio y fin del ciclo completo",
      any("inicia" in p and "termina" in p for p in pasos_contado))

det_ac16_cuotas = r14["resultado"]["detalle"]["origen"]
pasos_cuotas2 = det_ac16_cuotas["pasos"]
check("TC-026: CUOTAS menciona periodo de cuota (no ciclo completo) con fechas del periodo",
      any("periodo del" in p and "16/03/2026" in p and "11/04/2026" in p for p in pasos_cuotas2))

# AC-014(5): "conclusión con diferencia y estado" — ningún TC-0XX de test-cases.md
# cubre este punto todavía; se verifica contra mensaje/estado ya calculados por
# calcular_traslado (no se fabrican valores nuevos, Art. "Precisión" constitución).
check("AC-014(5) CUOTAS: desglose_narrativo incluye conclusión con mensaje y estado reales",
      "CONCLUSIÓN" in r14["resultado"]["desglose_narrativo"]
      and r14["resultado"]["estado"] in r14["resultado"]["desglose_narrativo"]
      and r14["resultado"]["mensaje"] in r14["resultado"]["desglose_narrativo"])
check("AC-014(5) CONTADO: desglose_narrativo incluye conclusión con mensaje y estado reales",
      "CONCLUSIÓN" in r15["resultado"]["desglose_narrativo"]
      and r15["resultado"]["estado"] in r15["resultado"]["desglose_narrativo"]
      and r15["resultado"]["mensaje"] in r15["resultado"]["desglose_narrativo"])

print("\nTodas las pruebas pasaron correctamente.")