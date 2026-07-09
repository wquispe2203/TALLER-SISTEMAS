from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Optional


# ---------------------------------------------------------------------------
# Errores y tipos
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
