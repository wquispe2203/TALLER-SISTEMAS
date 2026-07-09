from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from validation import parse_fecha

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

    NOTA: esta función ahora se usa SOLO con fines informativos/narrativos
    (mostrar cuántos feriados hay en el ciclo). Ya NO se usa para calcular
    el monto en CONTADO: los feriados no se cobran, así que no deben entrar
    ni al numerador ni al denominador de la fórmula de valor residual
    (ver `calcular_valor_contado`).
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


def _detalle_semanas_periodo(inicio: date, fin: date, fecha_traslado: date) -> dict:
    """
    Fuente única de verdad para "cuántas semanas de un periodo [inicio, fin)
    ya se consumieron a fecha_traslado", ancladas al día en que empezó ESE
    periodo (no al lunes del calendario). La semana que contiene un feriado
    se "cancela": no cuenta como consumida NI como parte del total que se
    cobra (los feriados no se le cobran al alumno, ni diluidos ni de otra
    forma — Art. correcciones §feriados).

    Usada tanto por `_prorratear_cuota` (para el monto) como por
    `generar_pasos_cuotas` (para la narrativa) — evita que el texto
    explicativo y el monto calculado puedan desincronizarse (Art. 4.4 de la
    constitución: no duplicar fórmulas de cálculo).
    """
    semanas_totales_calendario = _semanas_en_periodo(inicio, fin)
    feriado_indices = _semana_indices_feriado(inicio, fin)

    semanas_totales_reales = max(0, semanas_totales_calendario - len(feriado_indices))

    idx_actual = (fecha_traslado - inicio).days // 7
    idx_actual = max(0, min(idx_actual, semanas_totales_calendario - 1))

    semanas_consumidas = sum(1 for i in range(idx_actual) if i not in feriado_indices)
    semanas_restantes = max(0, semanas_totales_reales - semanas_consumidas)

    return {
        "inicio_periodo": inicio,
        "fin_periodo": fin,
        "dias_periodo": (fin - inicio).days,
        "semanas_totales_calendario": semanas_totales_calendario,
        "semanas_totales": semanas_totales_reales,
        "dias_transcurridos": (fecha_traslado - inicio).days,
        "idx_actual": idx_actual,
        "feriado_indices": feriado_indices,
        "semanas_consumidas": semanas_consumidas,
        "semanas_restantes": semanas_restantes,
    }


def _prorratear_cuota(
    monto: Decimal,
    inicio_periodo: date,
    fin_periodo: date,
    fecha_traslado: date,
) -> Decimal:
    """Prorratea el monto de la cuota vigente según `_detalle_semanas_periodo`."""
    d = _detalle_semanas_periodo(inicio_periodo, fin_periodo, fecha_traslado)
    valor = monto * Decimal(d["semanas_restantes"]) / Decimal(d["semanas_totales"])
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


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
) -> Decimal:
    """
    Valor residual de CONTADO.

    IMPORTANTE (corrección de feriados): `duration_weeks` representa las
    semanas REALES de clase del ciclo (sin feriados). Los feriados NO se
    cobran al alumno, así que no deben sumarse al denominador ni al
    numerador — antes se hacía `duration_weeks + semanas_feriado` como
    base, lo cual diluía el costo del feriado entre todas las semanas en
    vez de eliminarlo. Ahora el feriado simplemente no cuenta en ningún
    lado: ni en `semanas_consumidas` (ver `calcular_semanas_consumidas`,
    que ya lo excluía) ni aquí.
    """
    semanas_restantes = duration_weeks - semanas_consumidas
    valor_semana = cash_price / Decimal(duration_weeks)
    valor = valor_semana * Decimal(semanas_restantes)
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Selección de cuota vigente (CUOTAS)
# ---------------------------------------------------------------------------

def _seleccionar_cuota_vigente(
    installments: list[dict],
    fecha_traslado: date,
    fecha_inicio_ciclo: date,
    fecha_fin_ciclo: date,
) -> dict:
    """
    Determina qué cuota está vigente a `fecha_traslado` (o el caso borde que
    aplica). Única fuente de esta selección — usada tanto por
    `calcular_valor_cuotas` (monto) como por `generar_pasos_cuotas`
    (narrativa).

    Casos: "vigente" (hay una cuota cuyo periodo contiene la fecha),
    "antes_primera_cuota" (se debe la cuota 1 completa) o "fuera_de_ciclo"
    (fecha_traslado en o después del fin del ciclo: nada pendiente).
    """
    fechas = [parse_fecha(c["due_date"], fallback=fecha_inicio_ciclo) for c in installments]
    montos = [Decimal(str(c["amount"])) for c in installments]

    n = len(installments)
    for i in range(n):
        inicio_periodo = fechas[i]
        fin_periodo = fechas[i + 1] if i + 1 < n else fecha_fin_ciclo
        if inicio_periodo <= fecha_traslado < fin_periodo:
            return {
                "caso": "vigente",
                "numero": i + 1,
                "monto": montos[i],
                "inicio_periodo": inicio_periodo,
                "fin_periodo": fin_periodo,
            }

    if fechas and fecha_traslado < fechas[0]:
        return {
            "caso": "antes_primera_cuota",
            "numero": 1,
            "monto": montos[0],
            "inicio_periodo": None,
            "fin_periodo": fechas[0],
        }

    return {"caso": "fuera_de_ciclo", "numero": None, "monto": Decimal("0.00"), "inicio_periodo": None, "fin_periodo": None}


# ---------------------------------------------------------------------------
# Utilitarios de presentación
# ---------------------------------------------------------------------------

_DIAS_SEMANA_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _fmt_fecha_opt(f: Optional[date]) -> Optional[str]:
    """Formatea una fecha a DD/MM/YYYY, o None si f es None (FR-011/ADR-4 §4.2)."""
    return f.strftime("%d/%m/%Y") if f else None


# ---------------------------------------------------------------------------
# Generación de pasos narrativos (CONTADO)
# ---------------------------------------------------------------------------

def generar_pasos_contado(
    etiqueta: str,
    fecha_traslado: date,
    fecha_inicio: date,
    fecha_fin: date,
    duration_weeks: int,
    cash_price: Decimal,
) -> tuple[list[str], dict]:
    """
    Narra, paso a paso, cómo se llegó al valor residual de CONTADO.
    Reutiliza `calcular_semanas_consumidas` y `calcular_valor_contado`
    (las mismas funciones que usa el cálculo real) para que el texto
    nunca pueda desincronizarse del monto.

    Devuelve (lista_de_pasos, detalle_numerico); detalle_numerico incluye
    "valor" (Decimal) para que el llamador no tenga que recalcular el monto.
    """
    semanas_feriado = contar_semanas_feriado_entre(fecha_inicio, fecha_fin)
    semanas_consumidas = calcular_semanas_consumidas(fecha_traslado, fecha_inicio)
    semanas_restantes = duration_weeks - semanas_consumidas
    valor = calcular_valor_contado(cash_price, duration_weeks, semanas_consumidas)

    lunes_semana_actual = _lunes_de_semana(fecha_traslado)
    domingo_semana_actual = lunes_semana_actual + timedelta(days=6)
    dia_semana = fecha_traslado.weekday()
    indice_semana_actual = (lunes_semana_actual - fecha_inicio).days // 7 + 1
    semana_actual = max(1, min(indice_semana_actual, duration_weeks))
    consumida = dia_semana not in (0, 1)

    pasos = [
        f"{etiqueta}: fecha de traslado {fecha_traslado.strftime('%d/%m/%Y')} "
        f"({_DIAS_SEMANA_ES[dia_semana]}).",
        f"El ciclo inicia el {fecha_inicio.strftime('%d/%m/%Y')} y termina el {fecha_fin.strftime('%d/%m/%Y')}.",
        f"La fecha de traslado cae en la semana {indice_semana_actual} del ciclo "
        f"({lunes_semana_actual.strftime('%d/%m/%Y')} al {domingo_semana_actual.strftime('%d/%m/%Y')}).",
        (
            f"Como es {_DIAS_SEMANA_ES[dia_semana]} (miércoles a domingo consumen la semana), "
            f"esa semana SÍ se cuenta como consumida."
            if consumida
            else (
                f"Como es {_DIAS_SEMANA_ES[dia_semana]} (lunes y martes NO consumen la semana), "
                f"esa semana todavía NO se cuenta como consumida."
            )
        ),
        f"Semanas consumidas: {semanas_consumidas}.",
        (
            f"Dentro del ciclo completo hay {semanas_feriado} semana(s) de feriado. "
            "No se cobran al alumno: no se incluyen ni en las semanas de clase "
            "ni en las semanas restantes."
            if semanas_feriado
            else "El ciclo completo no cruza ninguna semana de feriado."
        ),
        f"Semanas de clase del ciclo (duration_weeks, feriados ya excluidos): {duration_weeks}.",
        f"Semanas restantes = semanas de clase ({duration_weeks}) − semanas consumidas ({semanas_consumidas}) = {semanas_restantes}.",
        f"Valor por semana = cash_price (S/ {cash_price:.2f}) ÷ semanas de clase ({duration_weeks}) = "
        f"S/ {(cash_price / Decimal(duration_weeks)):.4f}.",
        f"Saldo = valor por semana × semanas restantes ({semanas_restantes}) = S/ {valor:.2f} "
        "(redondeo half-up a 2 decimales).",
    ]
    detalle = {
        "semanas_totales": duration_weeks,
        "semanas_consumidas": semanas_consumidas,
        "semanas_restantes": semanas_restantes,
        "fecha_inicio_periodo": _fmt_fecha_opt(fecha_inicio),
        "fecha_fin_periodo": _fmt_fecha_opt(fecha_fin),
        "semana_actual": semana_actual,
        "valor": valor,
    }
    return pasos, detalle


# ---------------------------------------------------------------------------
# Cálculo de valor residual (CUOTAS)
# ---------------------------------------------------------------------------

def calcular_valor_cuotas(
    installments: list[dict],
    fecha_traslado: date,
    fecha_inicio_ciclo: date,
    fecha_fin_ciclo: date,
) -> Decimal:
    """
    Calcula el valor residual en modalidad CUOTAS.

    Se prorratea SOLO la cuota vigente a la fecha de traslado, según
    cuántas semanas REALES (sin feriados, ver `_detalle_semanas_periodo`)
    de su propio periodo ya se consumieron. No se suman cuotas futuras
    completas, y los feriados no se cobran (ni diluidos ni de otra forma).
    """
    sel = _seleccionar_cuota_vigente(installments, fecha_traslado, fecha_inicio_ciclo, fecha_fin_ciclo)
    if sel["caso"] == "vigente":
        return _prorratear_cuota(sel["monto"], sel["inicio_periodo"], sel["fin_periodo"], fecha_traslado)
    if sel["caso"] == "antes_primera_cuota":
        return sel["monto"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal("0.00")


# ---------------------------------------------------------------------------
# Generación de pasos narrativos (CUOTAS)
# ---------------------------------------------------------------------------

def generar_pasos_cuotas(
    etiqueta: str,
    installments: list[dict],
    fecha_traslado: date,
    fecha_inicio_ciclo: date,
    fecha_fin_ciclo: date,
) -> tuple[list[str], dict]:
    """
    Narra, paso a paso y en lenguaje natural, cómo se llegó al valor
    residual de CUOTAS — reutilizando `_seleccionar_cuota_vigente` y
    `_detalle_semanas_periodo` (los mismos que usa `calcular_valor_cuotas`),
    para que el texto y el monto nunca puedan desincronizarse.

    Devuelve (lista_de_pasos, detalle_numerico) donde detalle_numerico
    reemplaza al bloque `detalle` genérico de `calcular_traslado` con las
    semanas del PERIODO DE LA CUOTA VIGENTE (no las del ciclo completo).
    """
    sel = _seleccionar_cuota_vigente(installments, fecha_traslado, fecha_inicio_ciclo, fecha_fin_ciclo)
    pasos = [f"{etiqueta}: fecha de traslado {fecha_traslado.strftime('%d/%m/%Y')}."]

    if sel["caso"] == "fuera_de_ciclo":
        pasos.append("La fecha de traslado está en o después del fin del ciclo: no queda ninguna cuota pendiente.")
        return pasos, {
            "semanas_totales": 0, "semanas_consumidas": 0, "semanas_restantes": 0,
            "fecha_inicio_periodo": None, "fecha_fin_periodo": None, "semana_actual": None,
            "valor": Decimal("0.00"),
        }

    if sel["caso"] == "antes_primera_cuota":
        valor_completo = sel["monto"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        pasos.append(
            f"La fecha de traslado es anterior al vencimiento de la cuota 1 "
            f"({sel['fin_periodo'].strftime('%d/%m/%Y')}): se debe la cuota 1 completa, S/ {valor_completo:.2f}."
        )
        return pasos, {
            "semanas_totales": 1, "semanas_consumidas": 0, "semanas_restantes": 1,
            "fecha_inicio_periodo": None, "fecha_fin_periodo": _fmt_fecha_opt(sel["fin_periodo"]), "semana_actual": 1,
            "valor": valor_completo,
        }

    d = _detalle_semanas_periodo(sel["inicio_periodo"], sel["fin_periodo"], fecha_traslado)
    valor = _prorratear_cuota(sel["monto"], sel["inicio_periodo"], sel["fin_periodo"], fecha_traslado)

    pasos.append(
        f"La cuota vigente es la cuota {sel['numero']}, de S/ {sel['monto']:.2f}, "
        f"con periodo del {sel['inicio_periodo'].strftime('%d/%m/%Y')} al {sel['fin_periodo'].strftime('%d/%m/%Y')} "
        f"({d['dias_periodo']} días)."
    )
    pasos.append(
        f"Ese periodo equivale a {d['semanas_totales_calendario']} semana(s) de calendario "
        f"({d['dias_periodo']} días ÷ 7 = {d['dias_periodo']/7:.2f}, redondeado)."
    )
    pasos.append(
        f"Desde el inicio del periodo ({sel['inicio_periodo'].strftime('%d/%m/%Y')}) hasta la fecha de traslado "
        f"han pasado {d['dias_transcurridos']} día(s)."
    )
    if d["feriado_indices"]:
        pasos.append(
            f"Dentro de este periodo hay {len(d['feriado_indices'])} semana(s) de feriado. "
            "No se cobran al alumno: no cuentan como consumidas ni se incluyen en el total "
            f"de semanas del periodo ({d['semanas_totales_calendario']} calendario − "
            f"{len(d['feriado_indices'])} feriado(s) = {d['semanas_totales']} semanas reales)."
        )
    else:
        pasos.append("Ninguna semana feriado cae dentro de este periodo.")
    pasos.append(
        f"Semanas consumidas del periodo: {d['semanas_consumidas']}. "
        f"Semanas restantes: {d['semanas_totales']} − {d['semanas_consumidas']} = {d['semanas_restantes']}."
    )
    pasos.append(
        f"Valor residual = monto de la cuota (S/ {sel['monto']:.2f}) × semanas restantes ({d['semanas_restantes']}) "
        f"÷ semanas reales del periodo ({d['semanas_totales']}) = S/ {valor:.2f} "
        "(redondeo half-up a 2 decimales)."
    )

    detalle = {
        "semanas_totales": d["semanas_totales"],
        "semanas_consumidas": d["semanas_consumidas"],
        "semanas_restantes": d["semanas_restantes"],
        "fecha_inicio_periodo": _fmt_fecha_opt(sel["inicio_periodo"]),
        "fecha_fin_periodo": _fmt_fecha_opt(sel["fin_periodo"]),
        "semana_actual": d["idx_actual"] + 1,
        "valor": valor,
    }
    return pasos, detalle
