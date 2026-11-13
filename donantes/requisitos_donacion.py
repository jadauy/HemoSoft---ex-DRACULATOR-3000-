"""Verifica si un donante puede donar hoy: evaluación APTO del día y plazo mínimo (H3 · T3.3)."""

import calendar
from datetime import date

from .EvaluacionElegibilidad import APTO
from .validaciones import FORMATO_FECHA, parsear_fecha

# Decisión del PO: 3 meses entre donaciones para hombres y 4 para mujeres.
MESES_ENTRE_DONACIONES = {"M": 3, "F": 4}


def sumar_meses(fecha, meses):
    mes = fecha.month - 1 + meses
    anio = fecha.year + mes // 12
    mes = mes % 12 + 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def proxima_fecha_permitida(sexo, ultima_donacion):
    """Desde qué fecha puede volver a donar, o None si nunca ha donado."""
    if ultima_donacion is None:
        return None
    return sumar_meses(parsear_fecha(ultima_donacion.fecha), MESES_ENTRE_DONACIONES[sexo])


def verificar_puede_donar(donante, ultima_evaluacion, ultima_donacion, hoy=None):
    """Devuelve la lista de motivos por los que NO puede donar. Si está vacía, puede donar.

    donante: diccionario del donante (usa el campo "sexo").
    ultima_evaluacion: EvaluacionElegibilidad más reciente, o None.
    ultima_donacion: Donacion más reciente, o None.
    """
    hoy = hoy or date.today()
    motivos = []

    if ultima_evaluacion is None:
        motivos.append("El donante no tiene una evaluación de elegibilidad.")
    elif parsear_fecha(ultima_evaluacion.fechaEvaluacion) != hoy:
        motivos.append("La evaluación de elegibilidad debe hacerse el mismo día de la donación "
                       f"(la última es del {ultima_evaluacion.fechaEvaluacion}).")
    elif ultima_evaluacion.resultado != APTO:
        motivos.append(f"El resultado de la evaluación de hoy es {ultima_evaluacion.resultado}.")

    proxima = proxima_fecha_permitida(donante["sexo"], ultima_donacion)
    if proxima and hoy < proxima:
        meses = MESES_ENTRE_DONACIONES[donante["sexo"]]
        motivos.append(f"No se cumple el plazo mínimo de {meses} meses desde la última donación "
                       f"({ultima_donacion.fecha}). Puede volver a donar desde el {proxima.strftime(FORMATO_FECHA)}.")
    return motivos
