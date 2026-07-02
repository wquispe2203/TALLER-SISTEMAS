from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import openpyxl


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def normalize_modality(value: Any) -> str:
    text = normalize_text(value).upper()
    if text in {"PRESENCIAL"}:
        return "Presencial"
    if text in {"VIRTUAL"}:
        return "Virtual"
    if "PRESENCIAL" in text and "VIRTUAL" in text:
        return "Presencial/Virtual"
    return normalize_text(value)


def parse_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return text
        try:
            return datetime.strptime(text, "%d/%m/%Y").date().isoformat()
        except ValueError:
            return None
    return None


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = normalize_text(value).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_weeks(value: Any) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*SEMANAS?", text, re.IGNORECASE)
    if match:
        return int(float(match.group(1)))
    return None


def slugify(text: str) -> str:
    text = normalize_text(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def build_cycle(row: list[Any], headers: list[str], cycle_index: int) -> dict[str, Any] | None:
    values = {headers[i]: row[i] for i in range(min(len(headers), len(row))) if headers[i]}

    universidad = normalize_text(values.get("UNIVERSIDAD"))
    ciclo = normalize_text(values.get("CICLO"))
    modalidad = normalize_modality(values.get("MODALIDAD"))
    horario = normalize_text(values.get("HORARIO"))
    inicio = parse_date(values.get("INICIO"))
    fin = parse_date(values.get("FIN"))
    duracion = normalize_text(values.get("DURACIÓN"))

    if not universidad or not ciclo or not modalidad:
        return None
    if universidad.upper() in {"CONCURSO DE BECAS"}:
        return None
    if modalidad in {"Presencial/Virtual"}:
        return None

    total_partes = parse_number(values.get("TOTAL PARTES"))
    descuento = parse_number(values.get("AL CONTADO (% DSCTO.)"))
    monto_contado = parse_number(values.get("MONTO AL CONTADO"))
    ahorro = parse_number(values.get("AHORRO PARA ESTUDIANTE"))
    cuotas = []
    for index in range(1, 11):
        if index == 1:
            cuota_monto = parse_number(values.get("1° Cuota (en la Matrícula)"))
            cuota_vence = None
        else:
            cuota_monto = parse_number(values.get(f"{index}° Cuota (Monto)"))
            cuota_vence = parse_date(values.get(f"{index}° Cuota (Vence)"))
        if cuota_monto is not None or cuota_vence is not None:
            cuotas.append({"number": index, "amount": cuota_monto, "due_date": cuota_vence})

    return {
        "id": slugify(f"{universidad}-{ciclo}-{modalidad}"),
        "code": f"C{cycle_index:02d}",
        "display_name": f"{universidad} - {ciclo} - {modalidad}",
        "institution": universidad,
        "cycle_name": ciclo,
        "modality": modalidad,
        "schedule": horario,
        "start_date": inicio,
        "end_date": fin,
        "duration_text": duracion,
        "duration_weeks": parse_weeks(duracion),
        "payment_plans": {
            "Contado": {
                "discount_percent": descuento,
                "price": monto_contado,
                "savings": ahorro,
                "currency": "PEN",
            },
            "Cuotas": {
                "installment_count": int(total_partes) if total_partes is not None else None,
                "installments": cuotas,
                "currency": "PEN",
            },
        },
        "academic_level": normalize_text(values.get("NIVEL ACADÉMICO")),
        "target_audience": normalize_text(values.get("DIRIGIDO A")),
        "description": normalize_text(values.get("DESCRIPCIÓN DEL CICLO")),
    }


def convert_excel_to_parameters(input_path: Path, output_path: Path) -> dict[str, Any]:
    workbook = openpyxl.load_workbook(input_path, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    headers = [normalize_text(cell) for cell in rows[0]]

    cycles: list[dict[str, Any]] = []
    for index, row in enumerate(rows[1:], start=1):
        if not row or all(normalize_text(cell) == "" for cell in row):
            continue
        cycle = build_cycle(list(row), headers, index)
        if cycle is not None:
            cycles.append(cycle)

    output = {
        "metadata": {
            "source_file": str(input_path),
            "source_sheet": sheet.title,
            "generated_at": datetime.utcnow().date().isoformat(),
            "version": "2026-2",
            "notes": [
                "Archivo generado a partir del Excel oficial de ciclos.",
                "La estructura se ajusta a las reglas definidas en spec.md para validaciones y cálculo.",
            ],
        },
        "valid_states": ["MATRICULADO", "PAGADO"],
        "blocked_states": ["SUSPENDIDO", "RETIRADO"],
        "valid_modalities": ["Presencial", "Virtual"],
        "valid_conditions_of_payment": ["Contado", "Cuotas"],
        "discounts": [
            {"code": "none", "label": "Ninguno", "percent": 0.0},
            {"code": "20_percent", "label": "20%", "percent": 0.2},
            {"code": "familiar", "label": "Descuento familiar", "percent": None},
        ],
        "benefits": [
            {"code": "none", "label": "Ninguno", "percent": 0.0},
            {"code": "half_scholarship", "label": "1/2 beca", "percent": 0.5},
            {"code": "quarter_scholarship", "label": "1/4 beca", "percent": 0.25},
        ],
        "cycles": cycles,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Excel de ciclos a parameters.json")
    parser.add_argument(
        "input_excel",
        nargs="?",
        default=r"C:\Users\USER\Desktop\tem\Programación Ciclos 2026-2.xlsx",
        help="Ruta del archivo Excel fuente",
    )
    parser.add_argument(
        "output_json",
        nargs="?",
        default="data/parameters.json",
        help="Ruta del archivo JSON de salida",
    )
    args = parser.parse_args()

    input_path = Path(args.input_excel)
    output_path = Path(args.output_json)
    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    result = convert_excel_to_parameters(input_path, output_path)
    print(f"Se generaron {len(result['cycles'])} ciclos en {output_path}")
