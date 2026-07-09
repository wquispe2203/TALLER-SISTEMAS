# -*- coding: utf-8 -*-
"""
API Flask - Sistema de Traslados Académicos
=============================================

Endpoints:
  GET  /health
      -> {"status": "ok"}

  GET  /api/ciclos
      -> lista todos los ciclos disponibles (nombre, universidad, modalidad)

  POST /api/traslados/calcular
      Body JSON esperado:
      {
        "fecha_traslado": "15/05/2026",
        "origen": {
          "nombre": "ANUAL MARZO",
          "universidad": "SM",
          "modalidad_academica": "PRESENCIAL",
          "pago_en": "CONTADO"
        },
        "destino": {
          "nombre": "ANUAL MARZO",
          "universidad": "SM",
          "modalidad_academica": "VIRTUAL",
          "pago_en": "CONTADO"
        }
      }

      Respuesta 200 (éxito del cálculo):
      {
        "success": true,
        "resultado": { ... }
      }

      Respuesta 200 (error de negocio: ciclo no encontrado, fecha fuera de
      rango, modalidades de pago distintas):
      {
        "success": false,
        "error": "mensaje"
      }

      Respuesta 400 (error de formato/input inválido):
      {
        "success": false,
        "error": "mensaje"
      }

Ejecutar:
    python3 app.py
    (por defecto en http://0.0.0.0:5000)

Probar:
    curl -X POST http://localhost:5000/api/traslados/calcular \
      -H "Content-Type: application/json" \
      -d '{
            "fecha_traslado": "15/05/2026",
            "origen": {"nombre": "ANUAL MARZO", "universidad": "SM", "modalidad_academica": "PRESENCIAL", "pago_en": "CONTADO"},
            "destino": {"nombre": "ANUAL MARZO", "universidad": "SM", "modalidad_academica": "VIRTUAL", "pago_en": "CONTADO"}
          }'
"""

import os

from flask import Flask, jsonify, render_template, request
from traslados import (
    CicloInput,
    calcular_traslado_seguro,
    cargar_parametros,
    parse_fecha,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARAMETROS_PATH = os.path.join(BASE_DIR, "data", "parameters.json")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

# Se carga una vez al iniciar. Si el archivo cambia en producción, reiniciar
# el proceso o exponer un endpoint /api/reload que vuelva a llamar esto.
PARAMETROS = cargar_parametros(PARAMETROS_PATH)


def _extraer_ciclo_input(data: dict, campo: str) -> CicloInput:
    if campo not in data or not isinstance(data[campo], dict):
        raise ValueError(f"Falta el campo '{campo}' (objeto) en el body")
    d = data[campo]
    requeridos = ["nombre", "universidad", "modalidad_academica", "pago_en"]
    faltantes = [r for r in requeridos if r not in d or d[r] in (None, "")]
    if faltantes:
        raise ValueError(f"Faltan campos en '{campo}': {', '.join(faltantes)}")
    return CicloInput(
        nombre=str(d["nombre"]),
        universidad=str(d["universidad"]),
        modalidad_academica=str(d["modalidad_academica"]),
        pago_en=str(d["pago_en"]),
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/ciclos", methods=["GET"])
def listar_ciclos():
    ciclos = [
        {
            "nombre": c["cycle_name"],
            "universidad": c["institution"],
            "modalidad": c["modality"],
            "fecha_inicio": c["start_date"],
            "fecha_fin": c["end_date"],
            "duration_weeks": c["duration_weeks"],
        }
        for c in PARAMETROS.get("cycles", [])
    ]
    return jsonify({"success": True, "ciclos": ciclos})


@app.route("/api/traslados/calcular", methods=["POST"])
def calcular_traslado_endpoint():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"success": False, "error": "Body JSON inválido o ausente"}), 400

    if "fecha_traslado" not in data or not data["fecha_traslado"]:
        return jsonify({"success": False, "error": "Falta el campo 'fecha_traslado'"}), 400

    try:
        fecha_traslado = parse_fecha(str(data["fecha_traslado"]))
    except ValueError as e:
        return jsonify({"success": False, "error": f"Formato de fecha inválido: {e}"}), 400

    try:
        origen = _extraer_ciclo_input(data, "origen")
        destino = _extraer_ciclo_input(data, "destino")
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    resultado = calcular_traslado_seguro(fecha_traslado, origen, destino, PARAMETROS)
    return jsonify(resultado), 200


@app.errorhandler(404)
def not_found(_e):
    return jsonify({"success": False, "error": "Ruta no encontrada"}), 404


@app.errorhandler(405)
def method_not_allowed(_e):
    return jsonify({"success": False, "error": "Método no permitido"}), 405


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
