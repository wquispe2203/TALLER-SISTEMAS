from __future__ import annotations

import json
import sys
from datetime import date
from decimal import Decimal

from validation import (
    TrasladoError,
    CicloInput,
    _PAGO_A_PLAN,
    parse_fecha,
    cargar_parametros,
    buscar_ciclo,
)
from calculator import (
    FERIADOS_DIAS,
    contar_semanas_feriado_entre,
    obtener_semanas_feriado_lunes,
    calcular_semanas_consumidas,
    calcular_valor_contado,
    _seleccionar_cuota_vigente,
    _fmt_fecha_opt,
    generar_pasos_contado,
    generar_pasos_cuotas,
    calcular_valor_cuotas,
)


# ---------------------------------------------------------------------------
# Algoritmo principal
# ---------------------------------------------------------------------------


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

    # PASO 4 y 5: valor residual + desglose narrado
    plan_key = _PAGO_A_PLAN[pago_en]
    plan_origen = ciclo_origen["payment_plans"][plan_key]
    plan_destino = ciclo_destino["payment_plans"][plan_key]

    if pago_en == "CONTADO":
        pasos_origen, det_origen = generar_pasos_contado(
            "Ciclo origen", fecha_traslado, fecha_inicio_origen, fecha_fin_origen,
            ciclo_origen["duration_weeks"], Decimal(str(plan_origen["cash_price"])),
        )
        pasos_destino, det_destino = generar_pasos_contado(
            "Ciclo destino", fecha_traslado, fecha_inicio_destino, fecha_fin_destino,
            ciclo_destino["duration_weeks"], Decimal(str(plan_destino["cash_price"])),
        )
    else:  # CUOTAS
        pasos_origen, det_origen = generar_pasos_cuotas(
            "Ciclo origen", plan_origen["installments"], fecha_traslado, fecha_inicio_origen, fecha_fin_origen,
        )
        pasos_destino, det_destino = generar_pasos_cuotas(
            "Ciclo destino", plan_destino["installments"], fecha_traslado, fecha_inicio_destino, fecha_fin_destino,
        )

    saldo_origen = det_origen.pop("valor")
    costo_destino = det_destino.pop("valor")
    det_origen["pasos"] = pasos_origen
    det_destino["pasos"] = pasos_destino

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

    conclusion = f"Conclusión: {mensaje} (estado: {estado})."
    desglose_narrativo = (
        "\n---\n".join(pasos_origen)
        + "\n\n-- DESTINO --\n"
        + "\n---\n".join(pasos_destino)
        + "\n\n-- CONCLUSIÓN --\n"
        + conclusion
    )

    return {
        "success": True,
        "resultado": {
            "saldo_origen": float(saldo_origen),
            "costo_destino": float(costo_destino),
            "diferencia": float(diferencia),
            "estado": estado,
            "mensaje": mensaje,
            "desglose_narrativo": desglose_narrativo,
            "detalle": {
                "origen": det_origen,
                "destino": det_destino,
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
