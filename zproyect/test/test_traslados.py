# -*- coding: utf-8 -*-
import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from traslados import (
    CicloInput,
    TrasladoError,
    calcular_traslado,
    calcular_traslado_seguro,
    cargar_parametros,
    generar_pasos_contado,
    generar_pasos_cuotas,
)
from calculator import (
    contar_semanas_feriado_entre,
    obtener_semanas_feriado_lunes,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARAMETROS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "parameters.json"))
PARAMS = cargar_parametros(PARAMETROS_PATH)


# ---------------------------------------------------------------------------
# Helper: semanas feriado
# ---------------------------------------------------------------------------

def test_semanas_feriado_colapsadas():
    lunes_2026 = obtener_semanas_feriado_lunes(2026)
    assert len(lunes_2026) == 2


def test_semanas_feriado_separadas():
    lunes_2030 = obtener_semanas_feriado_lunes(2030)
    assert len(lunes_2030) == 3


def test_contar_semanas_feriado_2026():
    n = contar_semanas_feriado_entre(date(2026, 1, 1), date(2026, 12, 31))
    assert n == 2


def test_contar_semanas_feriado_2030():
    n = contar_semanas_feriado_entre(date(2030, 1, 1), date(2030, 12, 31))
    assert n == 3


# ---------------------------------------------------------------------------
# US-1: CONTADO
# ---------------------------------------------------------------------------

def test_tc1_contado_saldo_a_favor():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    det = r["resultado"]["detalle"]["origen"]
    assert det["semanas_consumidas"] == 9
    assert r["resultado"]["saldo_origen"] == 3557.25
    assert r["resultado"]["costo_destino"] == 2511.00
    assert det["semanas_totales"] == 40
    assert det["semanas_restantes"] == 31
    assert len(det["pasos"]) > 0


def test_tc6_lunes_no_consume():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 4, 13), origen, destino, PARAMS)
    assert r["resultado"]["saldo_origen"] == 4131.00


def test_tc7_martes_no_consume():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 4, 14), origen, destino, PARAMS)
    assert r["resultado"]["saldo_origen"] == 4131.00


def test_tc8_miercoles_consume():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r_miercoles = calcular_traslado(date(2026, 4, 15), origen, destino, PARAMS)
    r_lunes = calcular_traslado(date(2026, 4, 13), origen, destino, PARAMS)
    assert r_miercoles["resultado"]["saldo_origen"] == 4016.25
    assert r_miercoles["resultado"]["saldo_origen"] < r_lunes["resultado"]["saldo_origen"]


# ---------------------------------------------------------------------------
# US-1: CUOTAS
# ---------------------------------------------------------------------------

def test_tc3_tc9_cuotas_prorrateo():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 4, 20), origen, destino, PARAMS)
    assert r["resultado"]["saldo_origen"] == 382.50
    assert r["resultado"]["costo_destino"] == 270.00
    assert r["resultado"]["diferencia"] == 112.50
    assert r["resultado"]["estado"] == "SALDO_A_FAVOR"
    det = r["resultado"]["detalle"]["origen"]
    assert det["semanas_totales"] == 4
    assert det["semanas_consumidas"] == 1
    assert det["semanas_restantes"] == 3
    assert any("cuota 2" in p for p in det["pasos"])


# ---------------------------------------------------------------------------
# US-3: Desglose humano CUOTAS (AC-3.4)
# ---------------------------------------------------------------------------

def test_ac34_cuotas_desglose():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    assert r["resultado"]["saldo_origen"] == 382.50
    assert r["resultado"]["costo_destino"] == 270.00
    assert r["resultado"]["diferencia"] == 112.50
    assert r["resultado"]["estado"] == "SALDO_A_FAVOR"
    det = r["resultado"]["detalle"]["origen"]
    assert det["semanas_totales"] == 4
    assert det["semanas_consumidas"] == 1
    assert det["semanas_restantes"] == 3
    assert any("cuota 1" in p and "16/03/2026" in p and "11/04/2026" in p for p in det["pasos"])


# ---------------------------------------------------------------------------
# US-3: Desglose humano CONTADO (AC-3.5)
# ---------------------------------------------------------------------------

def test_ac35_contado_desglose():
    origen = CicloInput("SEMIANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    assert r["resultado"]["saldo_origen"] == 2180.25
    assert r["resultado"]["costo_destino"] == 1539.00
    assert r["resultado"]["diferencia"] == 641.25
    assert r["resultado"]["estado"] == "SALDO_A_FAVOR"
    det = r["resultado"]["detalle"]["origen"]
    assert det["semanas_totales"] == 28
    assert det["semanas_consumidas"] == 9
    assert det["semanas_restantes"] == 19
    assert any("semana 9" in p for p in det["pasos"])
    assert any("viernes" in p for p in det["pasos"])


# ---------------------------------------------------------------------------
# US-2: Validación en cascada — errores
# ---------------------------------------------------------------------------

def test_tc4_error_modalidad_diferente():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    with pytest.raises(TrasladoError, match="modalidades de pago diferentes"):
        calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)


def test_tc5_error_fuera_de_rango():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    with pytest.raises(TrasladoError, match="fuera del rango"):
        calcular_traslado(date(2026, 1, 15), origen, destino, PARAMS)


def test_tc10_error_ciclo_no_encontrado():
    origen = CicloInput("CICLO INEXISTENTE", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado_seguro(date(2026, 5, 15), origen, destino, PARAMS)
    assert r == {"success": False, "error": "Ciclo origen no encontrado en la base de datos"}


# ---------------------------------------------------------------------------
# US-3: CONTADO con feriado (TC-12) y CUOTAS con feriado (TC-13)
# ---------------------------------------------------------------------------

def test_tc12_contado_con_feriado():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 7, 29), origen, destino, PARAMS)
    assert r["resultado"]["saldo_origen"] == 2409.75
    assert r["resultado"]["costo_destino"] == 1701.00
    det = r["resultado"]["detalle"]["origen"]
    assert det["semanas_totales"] == 40
    assert det["semanas_consumidas"] == 19
    assert det["semanas_restantes"] == 21


def test_tc13_cuotas_con_feriado():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 8, 5), origen, destino, PARAMS)
    assert r["resultado"]["saldo_origen"] == 127.50
    assert r["resultado"]["costo_destino"] == 90.00
    assert r["resultado"]["diferencia"] == 37.50
    assert r["resultado"]["estado"] == "SALDO_A_FAVOR"
    det = r["resultado"]["detalle"]["origen"]
    assert det["semanas_totales"] == 4
    assert det["semanas_consumidas"] == 3
    assert det["semanas_restantes"] == 1


# ---------------------------------------------------------------------------
# US-6 / FR-011: Campos estructurados (AC-3.6, AC-3.7, AC-3.8, CB-9, CB-10)
# ---------------------------------------------------------------------------

def test_ac36_contado_campos_estructurados():
    origen = CicloInput("SEMIANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    det = r["resultado"]["detalle"]["origen"]
    assert det["fecha_inicio_periodo"] == "16/03/2026"
    assert det["fecha_fin_periodo"] == "02/10/2026"
    assert det["semana_actual"] == 9


def test_ac37_cuotas_campos_estructurados():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    det = r["resultado"]["detalle"]["origen"]
    assert det["fecha_inicio_periodo"] == "16/03/2026"
    assert det["fecha_fin_periodo"] == "11/04/2026"
    assert det["semana_actual"] == 2


def test_ac38_simetria_origen_destino():
    origen = CicloInput("SEMIANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    for k in ("fecha_inicio_periodo", "fecha_fin_periodo", "semana_actual"):
        assert k in r["resultado"]["detalle"]["destino"]


def test_cb9_fuera_de_ciclo_nulls():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 12, 31), origen, destino, PARAMS)
    det = r["resultado"]["detalle"]["origen"]
    assert det["fecha_inicio_periodo"] is None
    assert det["fecha_fin_periodo"] is None
    assert det["semana_actual"] is None


def test_cb10_clamp_smoke():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 12, 31), origen, destino, PARAMS)
    det = r["resultado"]["detalle"]["origen"]
    assert det["semana_actual"] <= det["semanas_totales"]


def test_cb10_clamp_sintetico():
    _, det = generar_pasos_contado(
        "test", date(2026, 3, 23), date(2026, 3, 16), date(2026, 3, 30),
        1, Decimal("100"),
    )
    assert det["semana_actual"] == 1
    assert det["semana_actual"] == det["semanas_totales"]


def test_cb8_antes_primera_cuota():
    installments = [
        {"number": 1, "amount": 500, "due_date": "01/06/2026"},
        {"number": 2, "amount": 500, "due_date": "01/07/2026"},
    ]
    _, det = generar_pasos_cuotas(
        "test", installments, date(2026, 5, 15), date(2026, 5, 1), date(2026, 12, 31),
    )
    assert det["fecha_inicio_periodo"] is None
    assert det["fecha_fin_periodo"] == "01/06/2026"
    assert det["semana_actual"] == 1
    assert det["valor"] == Decimal("500.00")


# ---------------------------------------------------------------------------
# US-5: Narrativa paso a paso
# ---------------------------------------------------------------------------

def test_tc021_cuotas_identifica_cuota():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    pasos = r["resultado"]["detalle"]["origen"]["pasos"]
    assert any("cuota 1" in p and "16/03/2026" in p and "11/04/2026" in p for p in pasos)


def test_tc022_cuotas_dias_y_semanas():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    pasos = r["resultado"]["detalle"]["origen"]["pasos"]
    assert any("días" in p and "semana(s)" in p for p in pasos)


def test_tc023_cuotas_consumidas_restantes():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    pasos = r["resultado"]["detalle"]["origen"]["pasos"]
    assert any("Semanas consumidas del periodo" in p and "Semanas restantes" in p for p in pasos)


def test_tc024_cuotas_formula():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    pasos = r["resultado"]["detalle"]["origen"]["pasos"]
    assert any("×" in p and "÷" in p for p in pasos)


def test_tc025_contado_inicio_fin():
    origen = CicloInput("SEMIANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    pasos = r["resultado"]["detalle"]["origen"]["pasos"]
    assert any("inicia" in p and "termina" in p for p in pasos)


def test_tc026_cuotas_periodo():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    pasos = r["resultado"]["detalle"]["origen"]["pasos"]
    assert any("periodo del" in p and "16/03/2026" in p and "11/04/2026" in p for p in pasos)


def test_desglose_narrativo_conclusion():
    origen = CicloInput("SEMIANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    assert "CONCLUSIÓN" in r["resultado"]["desglose_narrativo"]
    assert r["resultado"]["estado"] in r["resultado"]["desglose_narrativo"]
    assert r["resultado"]["mensaje"] in r["resultado"]["desglose_narrativo"]


def test_desglose_narrativo_conclusion_cuotas():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CUOTAS")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CUOTAS")
    r = calcular_traslado(date(2026, 3, 25), origen, destino, PARAMS)
    assert "CONCLUSIÓN" in r["resultado"]["desglose_narrativo"]
    assert r["resultado"]["estado"] in r["resultado"]["desglose_narrativo"]
    assert r["resultado"]["mensaje"] in r["resultado"]["desglose_narrativo"]


# ---------------------------------------------------------------------------
# T010: Tests adicionales de flujo de error
# ---------------------------------------------------------------------------

def test_error_ciclo_destino_no_encontrado():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("CICLO INEXISTENTE", "SM", "VIRTUAL", "CONTADO")
    with pytest.raises(TrasladoError, match="Ciclo destino no encontrado"):
        calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)


def test_error_fuera_de_rango_destino():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("SEMIANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    with pytest.raises(TrasladoError, match="fuera del rango"):
        calcular_traslado(date(2026, 10, 15), origen, destino, PARAMS)


def test_error_modalidad_invalida():
    origen = CicloInput("SEMIANUAL MARZO", "ZAR", "PRESENCIAL", "CONTADO")
    destino = CicloInput("SEMIANUAL MARZO", "ZAR", "VIRTUAL", "CONTADO")
    with pytest.raises(TrasladoError, match="no encontrado"):
        calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)


def test_calcular_traslado_seguro_exito():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado_seguro(date(2026, 5, 15), origen, destino, PARAMS)
    assert r["success"] is True


def test_validar_traslado_desde_validation():
    from validation import validar_traslado
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    vr = validar_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    assert vr.pago_en == "CONTADO"
    assert vr.ciclo_origen["cycle_name"] == "ANUAL MARZO"
    assert vr.ciclo_destino["institution"] == "SM"


# ---------------------------------------------------------------------------
# Cobertura: MONTO_PENDIENTE y TRASLADO_CUBIERTO
# ---------------------------------------------------------------------------

def test_monto_pendiente():
    origen = CicloInput("INTENSIVO MARZO", "SM", "VIRTUAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "VIRTUAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    assert r["resultado"]["estado"] == "MONTO_PENDIENTE"
    assert r["resultado"]["diferencia"] < 0


def test_traslado_cubierto():
    origen = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    destino = CicloInput("ANUAL MARZO", "SM", "PRESENCIAL", "CONTADO")
    r = calcular_traslado(date(2026, 5, 15), origen, destino, PARAMS)
    assert r["resultado"]["estado"] == "TRASLADO_CUBIERTO"
    assert r["resultado"]["diferencia"] == 0.0
