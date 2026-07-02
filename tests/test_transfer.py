import json
from pathlib import Path

import pytest

from calculator import calculate_transfer
from validation import validate_payload


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = ROOT / "data" / "parameters.json"


@pytest.fixture
def parameters():
    with PARAMETERS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_calculate_transfer_for_same_cycle_returns_zero():
    payload = {
        "cicloOrigen": "C01",
        "cicloDestino": "C01",
        "modalidad": "Presencial",
        "estado": "MATRICULADO",
        "montoPagado": 1000,
        "condicionPago": "Contado",
    }
    result = calculate_transfer(payload)
    assert result["success"] is True
    assert result["result"]["estado"] == "Sin saldo pendiente"


def test_calculate_transfer_uses_monto_pagado_to_compute_saldo_a_favor():
    payload = {
        "fechaTraslado": "2026-04-15",
        "cicloOrigen": {
            "modalidad": "Presencial",
            "universidad": "SM",
            "nombreCiclo": "ANUAL MARZO",
            "pago": "Contado",
        },
        "cicloDestino": {
            "modalidad": "Presencial",
            "universidad": "SM",
            "nombreCiclo": "SEMIANUAL MARZO",
            "pago": "Contado",
        },
        "estado": "MATRICULADO",
        "montoPagado": 1000,
        "condicionPago": "Contado",
    }
    result = calculate_transfer(payload)
    assert result["success"] is True
    assert result["result"]["detalle"]["saldo_a_favor"] == "1000.00"


def test_validate_payload_requires_positive_monto_pagado():
    payload = {
        "cicloOrigen": "C01",
        "cicloDestino": "C02",
        "estado": "MATRICULADO",
        "condicionPago": "Contado",
    }
    with pytest.raises(ValueError, match="monto pagado"):
        validate_payload(payload)


def test_validate_payload_accepts_known_states_and_cycles(parameters):
    payload = {
        "cicloOrigen": parameters["cycles"][0]["code"],
        "cicloDestino": parameters["cycles"][1]["code"],
        "modalidad": "Presencial",
        "estado": "MATRICULADO",
        "condicionPago": "Contado",
        "montoPagado": 1000,
    }
    validate_payload(payload)
