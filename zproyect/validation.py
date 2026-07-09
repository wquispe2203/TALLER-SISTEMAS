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


# ---------------------------------------------------------------------------
# Validación en cascada
# ---------------------------------------------------------------------------

@dataclass
class ValidacionResult:
    ciclo_origen: dict
    ciclo_destino: dict
    pago_en: str
    fecha_inicio_origen: date
    fecha_fin_origen: date
    fecha_inicio_destino: date
    fecha_fin_destino: date


def validar_traslado(
    fecha_traslado: date,
    origen: CicloInput,
    destino: CicloInput,
    parametros: dict,
) -> ValidacionResult:
    """
    Validación en cascada fail-fast:
    1. Existencia de ambos ciclos en parameters.json
    2. Igualdad de modalidad de pago entre origen y destino
    3. Fecha de traslado dentro del rango de ambos ciclos

    Devuelve un ValidacionResult con los datos ya validados para el cálculo.
    Lanza TrasladoError en el primer incumplimiento.
    """
    ciclo_origen = buscar_ciclo(parametros, origen.nombre, origen.universidad, origen.modalidad_academica)
    if ciclo_origen is None:
        raise TrasladoError("Ciclo origen no encontrado en la base de datos")

    ciclo_destino = buscar_ciclo(parametros, destino.nombre, destino.universidad, destino.modalidad_academica)
    if ciclo_destino is None:
        raise TrasladoError("Ciclo destino no encontrado en la base de datos")

    if origen.pago_en.strip().upper() != destino.pago_en.strip().upper():
        raise TrasladoError(
            "No se permiten traslados entre modalidades de pago diferentes. "
            "Si requiere este tipo de traslado, debe procesarlo manualmente."
        )
    pago_en = origen.pago_en.strip().upper()
    if pago_en not in _PAGO_A_PLAN:
        raise TrasladoError(f"Modalidad de pago inválida: {origen.pago_en}")

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

    return ValidacionResult(
        ciclo_origen=ciclo_origen,
        ciclo_destino=ciclo_destino,
        pago_en=pago_en,
        fecha_inicio_origen=fecha_inicio_origen,
        fecha_fin_origen=fecha_fin_origen,
        fecha_inicio_destino=fecha_inicio_destino,
        fecha_fin_destino=fecha_fin_destino,
    )
