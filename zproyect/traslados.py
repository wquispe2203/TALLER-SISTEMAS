from __future__ import annotations

import json
import sys
from datetime import date
from decimal import Decimal

from calculator import (
    generar_pasos_contado,
    generar_pasos_cuotas,
)
from validation import (
    _PAGO_A_PLAN,
    CicloInput,
    TrasladoError,
    cargar_parametros,
    parse_fecha,
    validar_traslado,
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
    vr = validar_traslado(fecha_traslado, origen, destino, parametros)
    pago_en = vr.pago_en

    plan_key = _PAGO_A_PLAN[pago_en]
    plan_origen = vr.ciclo_origen["payment_plans"][plan_key]
    plan_destino = vr.ciclo_destino["payment_plans"][plan_key]

    if pago_en == "CONTADO":
        pasos_origen, det_origen = generar_pasos_contado(
            "Ciclo origen", fecha_traslado, vr.fecha_inicio_origen, vr.fecha_fin_origen,
            vr.ciclo_origen["duration_weeks"], Decimal(str(plan_origen["cash_price"])),
        )
        pasos_destino, det_destino = generar_pasos_contado(
            "Ciclo destino", fecha_traslado, vr.fecha_inicio_destino, vr.fecha_fin_destino,
            vr.ciclo_destino["duration_weeks"], Decimal(str(plan_destino["cash_price"])),
        )
    else:  # CUOTAS
        pasos_origen, det_origen = generar_pasos_cuotas(
            "Ciclo origen", plan_origen["installments"], fecha_traslado, vr.fecha_inicio_origen, vr.fecha_fin_origen,
        )
        pasos_destino, det_destino = generar_pasos_cuotas(
            "Ciclo destino", plan_destino["installments"], fecha_traslado, vr.fecha_inicio_destino, vr.fecha_fin_destino,
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
