from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


# ---------------------------------------------------------------------------
# Feriados (definidos como fechas puntuales; el algoritmo deriva las semanas)
# ---------------------------------------------------------------------------

# (mes, día) de cada feriado que "cancela" su semana completa.
FERIADOS_DIAS = [
    (7, 28),   # Fiestas Patrias
    (7, 29),   # Fiestas Patrias
    (12, 25),  # Navidad
]


def _lunes_de_semana(fecha: date) -> date:
    """Devuelve el lunes de la semana (lunes-domingo) que contiene `fecha`."""
    return fecha - timedelta(days=fecha.weekday())


def obtener_semanas_feriado_lunes(year: int) -> set[date]:
    """
    Para un año dado, devuelve el conjunto de lunes que marcan el inicio
    de cada semana de feriado (deduplicado). Si 28 y 29 de julio caen en
    la misma semana, el set solo tendrá 1 entrada para julio; si caen en
    semanas distintas, tendrá 2.
    """
    lunes_set: set[date] = set()
    for mes, dia in FERIADOS_DIAS:
        try:
            f = date(year, mes, dia)
        except ValueError:
            continue
        lunes_set.add(_lunes_de_semana(f))
    return lunes_set


def es_semana_feriado(fecha: date) -> bool:
    """Determina si `fecha` cae dentro de alguna semana de feriado (lunes-domingo, calendario global)."""
    lunes_actual = _lunes_de_semana(fecha)
    candidatos = (
        obtener_semanas_feriado_lunes(fecha.year - 1)
        | obtener_semanas_feriado_lunes(fecha.year)
        | obtener_semanas_feriado_lunes(fecha.year + 1)
    )
    return lunes_actual in candidatos


def contar_semanas_feriado_entre(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Cuenta cuántas semanas de feriado (lunes de esa semana, calendario global)
    caen dentro del rango [fecha_inicio, fecha_fin], inclusive.
    Se usa para el cálculo de CONTADO (semanas ancladas al calendario global).
    """
    if fecha_fin < fecha_inicio:
        return 0
    lunes_feriados: set[date] = set()
    for year in range(fecha_inicio.year - 1, fecha_fin.year + 2):
        lunes_feriados |= obtener_semanas_feriado_lunes(year)
    return sum(1 for lunes in lunes_feriados if fecha_inicio <= lunes <= fecha_fin)


# ---------------------------------------------------------------------------
# Semanas ancladas a un periodo específico (usado en el prorrateo de CUOTAS)
# ---------------------------------------------------------------------------
#
# A diferencia de CONTADO (que ancla las semanas al lunes del calendario
# global), cada cuota puede empezar cualquier día de la semana (p. ej.
# sábado). Aquí la "semana 1" de un periodo siempre empieza el mismo día
# en que empezó ese periodo, sin importar qué día calendario sea.

def _semana_indices_feriado(inicio: date, fin: date) -> set[int]:
    """
    Devuelve los índices de semana (0-based, en bloques de 7 días ancladas
    a `inicio`) que contienen un feriado, dentro del rango [inicio, fin).
    """
    indices: set[int] = set()
    if fin <= inicio:
        return indices
    for year in range(inicio.year - 1, fin.year + 2):
        for mes, dia in FERIADOS_DIAS:
            try:
                f = date(year, mes, dia)
            except ValueError:
                continue
            if inicio <= f < fin:
                indices.add((f - inicio).days // 7)
    return indices


def _semanas_en_periodo(inicio: date, fin: date) -> int:
    """
    Número de semanas del periodo [inicio, fin), redondeado a entero.
    Prohibido dejarlo como fracción (p. ej. 3.71): el negocio trabaja
    siempre en semanas completas.
    """
    dias = (fin - inicio).days
    return max(1, round(dias / 7))


def _prorratear_cuota(
    monto: Decimal,
    inicio_periodo: date,
    fin_periodo: date,
    fecha_traslado: date,
) -> Decimal:
    """
    Prorratea el monto de la cuota vigente según las semanas ya consumidas
    dentro de SU PROPIO periodo (ancladas al día en que empezó ese periodo,
    no al lunes del calendario). La semana que contiene un feriado se
    "cancela": no cuenta como consumida.
    """
    semanas_totales = _semanas_en_periodo(inicio_periodo, fin_periodo)
    feriado_indices = _semana_indices_feriado(inicio_periodo, fin_periodo)

    idx_actual = (fecha_traslado - inicio_periodo).days // 7
    idx_actual = max(0, min(idx_actual, semanas_totales - 1))

    # Semanas completas antes del índice actual, sin contar semanas feriado.
    semanas_consumidas = sum(1 for i in range(idx_actual) if i not in feriado_indices)
    semanas_restantes = max(0, semanas_totales - semanas_consumidas)

    valor = monto * Decimal(semanas_restantes) / Decimal(semanas_totales)
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Utilidades de fecha
# ---------------------------------------------------------------------------

def parse_fecha(valor: str, fallback: Optional[date] = None) -> date:
    """
    Parsea una fecha que puede venir como:
      - "D/M/YYYY" o "DD/MM/YYYY"  (formato del Excel/parameters.json)
      - "YYYY-MM-DD"               (formato ISO)
      - "En la matrícula"          (usa `fallback`, normalmente fecha de inicio del ciclo)
    """
    if valor is None:
        raise ValueError("Fecha vacía")
    valor = valor.strip()
    if valor.lower() == "en la matrícula":
        if fallback is None:
            raise ValueError("'En la matrícula' requiere fecha de inicio del ciclo")
        return fallback
    if "/" in valor:
        d, m, y = valor.split("/")
        return date(int(y), int(m), int(d))
    return date.fromisoformat(valor)


# ---------------------------------------------------------------------------
# Carga y búsqueda de ciclos
# ---------------------------------------------------------------------------

def cargar_parametros(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def buscar_ciclo(parametros: dict, nombre: str, institucion: str, modalidad: str) -> Optional[dict]:
    """Busca un ciclo por nombre + institución + modalidad (case-insensitive)."""
    nombre_n = nombre.strip().upper()
    inst_n = institucion.strip().upper()
    mod_n = modalidad.strip().upper()
    for ciclo in parametros.get("cycles", []):
        if (
            ciclo["cycle_name"].strip().upper() == nombre_n
            and ciclo["institution"].strip().upper() == inst_n
            and ciclo["modality"].strip().upper() == mod_n
        ):
            return ciclo
    return None


# ---------------------------------------------------------------------------
# Cálculo de semanas consumidas (CONTADO — ancladas al calendario global)
# ---------------------------------------------------------------------------

def calcular_semanas_consumidas(fecha_traslado: date, fecha_inicio: date) -> int:
    """
    Calcula cuántas semanas se han consumido desde fecha_inicio hasta
    fecha_traslado, saltando semanas de feriado completas y aplicando la
    regla lunes/martes = semana actual NO consumida.
    Usado únicamente para el plan CONTADO.
    """
    semanas_feriado = contar_semanas_feriado_entre(fecha_inicio, fecha_traslado)
    fecha_ajustada = fecha_traslado - timedelta(weeks=semanas_feriado)

    dias_transcurridos = (fecha_ajustada - fecha_inicio).days
    semanas_completas = dias_transcurridos // 7

    dia_semana = fecha_ajustada.weekday()  # 0=Lunes ... 6=Domingo
    if dia_semana in (0, 1):  # Lunes o Martes
        return semanas_completas
    return semanas_completas + 1


# ---------------------------------------------------------------------------
# Cálculo de valor residual
# ---------------------------------------------------------------------------

def calcular_valor_contado(
    cash_price: Decimal,
    duration_weeks: int,
    semanas_consumidas: int,
    fecha_inicio: date,
    fecha_fin: date,
) -> Decimal:
    semanas_feriado = contar_semanas_feriado_entre(fecha_inicio, fecha_fin)
    semanas_efectivas = duration_weeks + semanas_feriado
    semanas_restantes = semanas_efectivas - semanas_consumidas
    valor_semana = cash_price / Decimal(semanas_efectivas)
    valor = valor_semana * Decimal(semanas_restantes)
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_valor_cuotas(
    installments: list[dict],
    fecha_traslado: date,
    fecha_inicio_ciclo: date,
    fecha_fin_ciclo: date,
) -> Decimal:
    """
    Calcula el valor residual en modalidad CUOTAS.

    A diferencia de la versión anterior (que sumaba el monto completo de
    TODAS las cuotas futuras), ahora se prorratea SOLO la cuota vigente a
    la fecha de traslado, según cuántas semanas de su propio periodo ya
    se consumieron (sin contar la semana feriado, si la hay). No se suman
    cuotas futuras completas.
    """
    fechas = [parse_fecha(c["due_date"], fallback=fecha_inicio_ciclo) for c in installments]
    montos = [Decimal(str(c["amount"])) for c in installments]

    n = len(installments)
    for i in range(n):
        inicio_periodo = fechas[i]
        fin_periodo = fechas[i + 1] if i + 1 < n else fecha_fin_ciclo
        if inicio_periodo <= fecha_traslado < fin_periodo:
            return _prorratear_cuota(montos[i], inicio_periodo, fin_periodo, fecha_traslado)

    # fecha_traslado antes de la primera cuota: se debe la cuota 1 completa.
    if fechas and fecha_traslado < fechas[0]:
        return montos[0].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # fecha_traslado en o después del fin del ciclo: nada pendiente.
    return Decimal("0.00")


# ---------------------------------------------------------------------------
# Algoritmo principal
# ---------------------------------------------------------------------------

class TrasladoError(Exception):
    """Error de validación de negocio (ciclo no encontrado, fecha fuera de rango, etc.)."""


@dataclass
class CicloInput:
    nombre: str
    universidad: str
    modalidad_academica: str  # "PRESENCIAL" / "VIRTUAL"
    pago_en: str               # "CONTADO" / "CUOTAS"


_PAGO_A_PLAN = {"CONTADO": "Contado", "CUOTAS": "Cuotas"}


def calcular_traslado(
    fecha_traslado: date,
    origen: CicloInput,
    destino: CicloInput,
    parametros: dict,
) -> dict:
    # PASO 1: existencia de ciclos
    ciclo_origen = buscar_ciclo(parametros, origen.nombre, origen.universidad, origen.modalidad_academica)
    if ciclo_origen is None:
        raise TrasladoError("Ciclo origen no encontrado en la base de datos")

    ciclo_destino = buscar_ciclo(parametros, destino.nombre, destino.universidad, destino.modalidad_academica)
    if ciclo_destino is None:
        raise TrasladoError("Ciclo destino no encontrado en la base de datos")

    # PASO 2: modalidad de pago igual
    if origen.pago_en.strip().upper() != destino.pago_en.strip().upper():
        raise TrasladoError(
            "No se permiten traslados entre modalidades de pago diferentes. "
            "Si requiere este tipo de traslado, debe procesarlo manualmente."
        )
    pago_en = origen.pago_en.strip().upper()
    if pago_en not in _PAGO_A_PLAN:
        raise TrasladoError(f"Modalidad de pago inválida: {origen.pago_en}")

    # PASO 3: fecha dentro de rango
    fecha_inicio_origen = parse_fecha(ciclo_origen["start_date"])
    fecha_fin_origen = parse_fecha(ciclo_origen["end_date"])
    fecha_inicio_destino = parse_fecha(ciclo_destino["start_date"])
    fecha_fin_destino = parse_fecha(ciclo_destino["end_date"])

    if not (fecha_inicio_origen <= fecha_traslado <= fecha_fin_origen):
        raise TrasladoError(
            f"La fecha de traslado está fuera del rango del ciclo origen ({ciclo_origen['cycle_name']})"
        )
    if not (fecha_inicio_destino <= fecha_traslado <= fecha_fin_destino):
        raise TrasladoError(
            f"La fecha de traslado está fuera del rango del ciclo destino ({ciclo_destino['cycle_name']})"
        )

    # PASO 4: semanas consumidas (solo aplica/reporta para CONTADO; en CUOTAS
    # el detalle usa las semanas del periodo de la cuota vigente).
    semanas_consumidas_origen = calcular_semanas_consumidas(fecha_traslado, fecha_inicio_origen)
    semanas_consumidas_destino = calcular_semanas_consumidas(fecha_traslado, fecha_inicio_destino)

    # PASO 5: valor residual
    plan_key = _PAGO_A_PLAN[pago_en]
    if pago_en == "CONTADO":
        plan_origen = ciclo_origen["payment_plans"][plan_key]
        plan_destino = ciclo_destino["payment_plans"][plan_key]

        saldo_origen = calcular_valor_contado(
            Decimal(str(plan_origen["cash_price"])),
            ciclo_origen["duration_weeks"],
            semanas_consumidas_origen,
            fecha_inicio_origen,
            fecha_fin_origen,
        )
        costo_destino = calcular_valor_contado(
            Decimal(str(plan_destino["cash_price"])),
            ciclo_destino["duration_weeks"],
            semanas_consumidas_destino,
            fecha_inicio_destino,
            fecha_fin_destino,
        )
    else:  # CUOTAS
        plan_origen = ciclo_origen["payment_plans"][plan_key]
        plan_destino = ciclo_destino["payment_plans"][plan_key]

        saldo_origen = calcular_valor_cuotas(
            plan_origen["installments"], fecha_traslado, fecha_inicio_origen, fecha_fin_origen
        )
        costo_destino = calcular_valor_cuotas(
            plan_destino["installments"], fecha_traslado, fecha_inicio_destino, fecha_fin_destino
        )

    # PASO 6: diferencia
    diferencia = saldo_origen - costo_destino

    # PASO 7: mensaje
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
        "success": True,
        "resultado": {
            "saldo_origen": float(saldo_origen),
            "costo_destino": float(costo_destino),
            "diferencia": float(diferencia),
            "estado": estado,
            "mensaje": mensaje,
            "detalle": {
                "origen": {
                    "semanas_totales": ciclo_origen["duration_weeks"],
                    "semanas_consumidas": semanas_consumidas_origen,
                    "semanas_restantes": ciclo_origen["duration_weeks"] - semanas_consumidas_origen,
                },
                "destino": {
                    "semanas_totales": ciclo_destino["duration_weeks"],
                    "semanas_consumidas": semanas_consumidas_destino,
                    "semanas_restantes": ciclo_destino["duration_weeks"] - semanas_consumidas_destino,
                },
            },
        },
    }


def calcular_traslado_seguro(
    fecha_traslado: date,
    origen: CicloInput,
    destino: CicloInput,
    parametros: dict,
) -> dict:
    """Igual que calcular_traslado pero captura TrasladoError y devuelve {"success": False, "error": ...}."""
    try:
        return calcular_traslado(fecha_traslado, origen, destino, parametros)
    except TrasladoError as e:
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# CLI simple
# ---------------------------------------------------------------------------

def _main():
    import argparse

    parser = argparse.ArgumentParser(description="Calculadora de traslados académicos")
    parser.add_argument("--parametros", default="parameters.json")
    parser.add_argument("--fecha", required=True, help="Fecha de traslado DD/MM/YYYY")
    parser.add_argument("--origen-nombre", required=True)
    parser.add_argument("--origen-universidad", required=True)
    parser.add_argument("--origen-modalidad", required=True, choices=["PRESENCIAL", "VIRTUAL"])
    parser.add_argument("--origen-pago", required=True, choices=["CONTADO", "CUOTAS"])
    parser.add_argument("--destino-nombre", required=True)
    parser.add_argument("--destino-universidad", required=True)
    parser.add_argument("--destino-modalidad", required=True, choices=["PRESENCIAL", "VIRTUAL"])
    parser.add_argument("--destino-pago", required=True, choices=["CONTADO", "CUOTAS"])
    args = parser.parse_args()

    parametros = cargar_parametros(args.parametros)
    fecha_traslado = parse_fecha(args.fecha)

    origen = CicloInput(args.origen_nombre, args.origen_universidad, args.origen_modalidad, args.origen_pago)
    destino = CicloInput(args.destino_nombre, args.destino_universidad, args.destino_modalidad, args.destino_pago)

    resultado = calcular_traslado_seguro(fecha_traslado, origen, destino, parametros)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if not resultado["success"]:
        sys.exit(1)


if __name__ == "__main__":
    _main()