from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PARAMETERS_PATH = ROOT / "data" / "parameters.json"


def load_parameters() -> dict[str, Any]:
    with PARAMETERS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_payload(payload: dict[str, Any]) -> None:
    parameters = load_parameters()
    valid_states = set(parameters["valid_states"])
    blocked_states = set(parameters["blocked_states"])
    valid_modalities = set(parameters["valid_modalities"])
    valid_conditions = set(parameters["valid_conditions_of_payment"])
    cycles = {cycle["code"]: cycle for cycle in parameters["cycles"]}

    amount_paid = payload.get("montoPagado")
    if amount_paid is None:
        raise ValueError("Debe ingresar el monto pagado.")
    try:
        amount_paid_value = float(amount_paid)
    except (TypeError, ValueError):
        raise ValueError("El monto pagado debe ser numérico.") from None
    if amount_paid_value <= 0:
        raise ValueError("El monto pagado debe ser mayor a 0.")

    state = payload.get("estado")
    if state in blocked_states:
        raise ValueError("El estado del estudiante no permite realizar traslados.")
    if state not in valid_states:
        raise ValueError("El estado del estudiante es inválido.")

    origin_selection = payload.get("cicloOrigen")
    destination_selection = payload.get("cicloDestino")
    if not origin_selection or not destination_selection:
        raise ValueError("Debe seleccionar un ciclo origen y destino.")

    if isinstance(origin_selection, dict):
        modality = origin_selection.get("modalidad")
        university = origin_selection.get("universidad")
        name = origin_selection.get("nombreCiclo")
        if modality not in valid_modalities:
            raise ValueError("La modalidad seleccionada es inválida.")
        if not university or not name:
            raise ValueError("Faltan datos para identificar el ciclo origen.")
    elif origin_selection in cycles:
        pass
    else:
        raise ValueError("Los ciclos seleccionados no existen en los parámetros oficiales.")

    if isinstance(destination_selection, dict):
        modality = destination_selection.get("modalidad")
        university = destination_selection.get("universidad")
        name = destination_selection.get("nombreCiclo")
        if modality not in valid_modalities:
            raise ValueError("La modalidad seleccionada es inválida.")
        if not university or not name:
            raise ValueError("Faltan datos para identificar el ciclo destino.")
    elif destination_selection in cycles:
        pass
    else:
        raise ValueError("Los ciclos seleccionados no existen en los parámetros oficiales.")

    condition = payload.get("condicionPago")
    if condition not in valid_conditions and str(condition).lower() not in {"contado", "matricula"}:
        raise ValueError("La condición de pago seleccionada es inválida.")
