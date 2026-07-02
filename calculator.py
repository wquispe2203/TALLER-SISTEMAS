from __future__ import annotations

import json
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PARAMETERS_PATH = ROOT / "data" / "parameters.json"


def load_parameters() -> dict[str, Any]:
    with PARAMETERS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def decimalize(value: Any) -> Decimal:
    return Decimal(str(value))


def round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _normalize_text(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_value).strip().lower()


def _normalize_condition(value: Any) -> str:
    normalized = _normalize_text(value)
    if normalized in {"matricula", "matricula"}:
        return "Contado"
    if normalized in {"contado", "cuotas", "matricula"}:
        return "Contado" if normalized != "cuotas" else "Cuotas"
    return "Contado"


def _get_plan_price(cycle: dict[str, Any], condition: str) -> Decimal:
    plan = cycle["payment_plans"].get(condition)
    if not plan:
        raise ValueError("La condición de pago seleccionada no tiene un plan configurado.")

    if condition == "Cuotas" and plan.get("installments"):
        return round_money(sum(decimalize(item["amount"]) for item in plan["installments"]))

    return round_money(decimalize(plan["price"]))


def _get_discount_percent(label: str) -> Decimal:
    if label == "20%":
        return Decimal("0.20")
    if label == "1/2 beca":
        return Decimal("0.50")
    if label == "1/4 beca":
        return Decimal("0.25")
    if label == "Descuento familiar":
        return Decimal("0.10")
    return Decimal("0.00")


def _resolve_cycle(cycles: dict[str, dict[str, Any]], selection: Any) -> dict[str, Any]:
    if isinstance(selection, str) and selection in cycles:
        return cycles[selection]

    if not isinstance(selection, dict):
        raise ValueError("Debe seleccionar un ciclo origen y destino válidos.")

    modality = _normalize_text(selection.get("modalidad"))
    university = _normalize_text(selection.get("universidad"))
    cycle_name = _normalize_text(selection.get("nombreCiclo"))

    if not modality or not university or not cycle_name:
        raise ValueError("Faltan datos para identificar el ciclo seleccionado.")

    for cycle in cycles.values():
        if (
            _normalize_text(cycle.get("modality")) == modality
            and _normalize_text(cycle.get("institution")) == university
            and _normalize_text(cycle.get("cycle_name")) == cycle_name
        ):
            return cycle

    raise ValueError("No se encontró un ciclo con los datos proporcionados.")


def calculate_transfer(payload: dict[str, Any]) -> dict[str, Any]:
    parameters = load_parameters()
    cycles = {cycle["code"]: cycle for cycle in parameters["cycles"]}

    origin_selection = payload.get("cicloOrigen")
    destination_selection = payload.get("cicloDestino")
    amount_paid = payload.get("montoPagado")

    if amount_paid is None:
        raise ValueError("Debe ingresar el monto pagado.")

    try:
        amount_paid_value = Decimal(str(amount_paid))
    except Exception as exc:
        raise ValueError("El monto pagado debe ser numérico.") from exc

    if amount_paid_value <= 0:
        raise ValueError("El monto pagado debe ser mayor a 0.")

    if origin_selection is None or destination_selection is None:
        raise ValueError("Debe seleccionar un ciclo origen y destino.")

    if isinstance(origin_selection, dict) and isinstance(destination_selection, dict):
        if origin_selection == destination_selection:
            return {
                "success": True,
                "result": {
                    "estado": "Sin saldo pendiente",
                    "mensaje": "El traslado no genera saldo ni monto pendiente.",
                    "detalle": {
                        "operacion": "ciclo_origen_igual_destino",
                        "resultado": "0.00",
                        "formula": "No aplica: el origen y el destino coinciden.",
                        "operaciones": ["El ciclo de origen coincide con el destino; por eso no hay ajuste."],
                    },
                },
            }

    origin = _resolve_cycle(cycles, origin_selection)
    destination = _resolve_cycle(cycles, destination_selection)

    condition = _normalize_condition(payload.get("condicionPago", "Contado"))
    origin_price = _get_plan_price(origin, condition)
    destination_price = _get_plan_price(destination, condition)

    weeks_total = int(origin["duration_weeks"])
    weeks_remaining = max(weeks_total, 1)
    saldo_a_favor = round_money(amount_paid_value * Decimal(weeks_remaining) / Decimal(weeks_total))
    discount_percent = _get_discount_percent(str(payload.get("descuento", "Ninguno")))
    discount_amount = round_money(destination_price * discount_percent)
    monto_a_cancelar = round_money(destination_price - discount_amount)
    resultado = round_money(saldo_a_favor - monto_a_cancelar)

    if resultado > 0:
        estado = "Saldo a favor"
        mensaje = "El saldo a favor del ciclo cubre el traslado."
    elif resultado == 0:
        estado = "Sin saldo pendiente"
        mensaje = "El saldo a favor cubre exactamente el costo del nuevo ciclo."
    else:
        estado = "Monto pendiente"
        mensaje = f"El saldo a favor del ciclo no cubre. Falta S/ {abs(resultado):.2f}"

    formula = "saldo a favor = precio del ciclo origen; monto a cancelar = precio del ciclo destino menos descuentos"
    operaciones = [
        f"Ciclo origen: {origin.get('display_name', origin.get('code'))}",
        f"Ciclo destino: {destination.get('display_name', destination.get('code'))}",
        f"Semanas calculadas: {weeks_total}",
        f"Saldo a favor: S/ {saldo_a_favor:.2f}",
        f"Monto a cancelar: S/ {monto_a_cancelar:.2f}",
        f"Diferencia final: S/ {resultado:.2f}",
    ]

    return {
        "success": True,
        "result": {
            "estado": estado,
            "mensaje": mensaje,
            "detalle": {
                "semanas_calculadas": weeks_total,
                "saldo_a_favor": f"{saldo_a_favor:.2f}",
                "monto_a_cancelar": f"{monto_a_cancelar:.2f}",
                "resultado": f"{resultado:.2f}",
                "formula": formula,
                "operaciones": operaciones,
            },
        },
    }
