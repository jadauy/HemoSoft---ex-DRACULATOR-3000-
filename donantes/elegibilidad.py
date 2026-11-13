"""Cálculo del resultado de una evaluación de elegibilidad (H2 · T2.3).

Regla acordada con el PO:
- NO APTO: causa permanente (declarada en el cuestionario o edad sobre 65 años).
- DIFERIDO: causa temporal (menor de 18, peso bajo 50 kg, hemoglobina baja, presión fuera de rango
  o causa temporal declarada). Puede volver a evaluarse desde la fecha de habilitación.
- APTO: cumple todos los requisitos.
"""

from datetime import timedelta

from .EvaluacionElegibilidad import APTO, DIFERIDO, NO_APTO

EDAD_MINIMA = 18
EDAD_MAXIMA = 65
PESO_MINIMO = 50.0
HEMOGLOBINA_MINIMA = {"F": 12.5, "M": 13.5}  # g/dL
PRESION_SISTOLICA = (90, 180)                # mmHg
PRESION_DIASTOLICA = (50, 100)               # mmHg
DIAS_DIFERIMIENTO = 30


def edad_en(fecha_nacimiento, fecha):
    cumplio = (fecha.month, fecha.day) >= (fecha_nacimiento.month, fecha_nacimiento.day)
    return fecha.year - fecha_nacimiento.year - (0 if cumplio else 1)


def cumpleanios(fecha_nacimiento, edad):
    try:
        return fecha_nacimiento.replace(year=fecha_nacimiento.year + edad)
    except ValueError:  # 29 de febrero
        return fecha_nacimiento.replace(year=fecha_nacimiento.year + edad, day=28)


def calcular_resultado(sexo, fecha_nacimiento, fecha, peso, hemoglobina, sistolica, diastolica,
                       causa_temporal=False, causa_permanente=False):
    """Devuelve (resultado, motivos, fecha_habilitacion). fecha_habilitacion es None si es NO APTO."""
    permanentes, temporales = [], []
    habilitacion = fecha + timedelta(days=DIAS_DIFERIMIENTO)
    edad = edad_en(fecha_nacimiento, fecha)

    if causa_permanente:
        permanentes.append("Causa permanente declarada en el cuestionario.")
    if edad > EDAD_MAXIMA:
        permanentes.append(f"Edad sobre {EDAD_MAXIMA} años ({edad}).")
    if edad < EDAD_MINIMA:
        temporales.append(f"Menor de {EDAD_MINIMA} años ({edad}).")
        habilitacion = max(habilitacion, cumpleanios(fecha_nacimiento, EDAD_MINIMA))
    if peso < PESO_MINIMO:
        temporales.append(f"Peso bajo {PESO_MINIMO:g} kg ({peso:g} kg).")
    if hemoglobina < HEMOGLOBINA_MINIMA[sexo]:
        temporales.append(f"Hemoglobina bajo {HEMOGLOBINA_MINIMA[sexo]:g} g/dL ({hemoglobina:g}).")
    if not PRESION_SISTOLICA[0] <= sistolica <= PRESION_SISTOLICA[1] or \
            not PRESION_DIASTOLICA[0] <= diastolica <= PRESION_DIASTOLICA[1]:
        temporales.append(f"Presión fuera de rango ({sistolica}/{diastolica} mmHg).")
    if causa_temporal:
        temporales.append("Causa temporal declarada en el cuestionario.")

    if permanentes:
        return NO_APTO, permanentes + temporales, None
    if temporales:
        return DIFERIDO, temporales, habilitacion
    return APTO, [], fecha
