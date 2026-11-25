"""Determina las unidades por vencer y las que ya vencieron"""

# Una unidad de sangre debe tener su código, grupo sanguíneo (este debe ser sacado del donante), fecha de extracción y fecha de vencimiento

from datetime import date, timedelta

from donantes.validaciones import parsear_fecha
DIAS_VENCIMIENTO = 7

# Se saca una lista de elementos de variable "Hemocomponente", debe ser una lista para sacar cada unidad de sangre por separado
def calcular_vencimientos(unidades_sangre, hoy = None):
    fecha_hoy = hoy if hoy is not None else date.today()
    unidades_vencidas = []
    unidades_por_vencer = []

    for unidad in unidades_sangre:
        # Se saca la fecha de vencimiento de cada unidad de sangre
        fecha_vencimiento_str = unidad.fecha_vencimiento
        fecha_vencimiento = parsear_fecha(fecha_vencimiento_str)

        if fecha_hoy >= fecha_vencimiento:
            unidades_vencidas.append(unidad)

        # Si la fecha de vencimiento es hoy, se considera vencida, si la fecha de vencimiento es dentro de los próximos 7 días, se considera por vencer
        elif fecha_hoy <= fecha_vencimiento and fecha_vencimiento <= fecha_hoy + timedelta(days = DIAS_VENCIMIENTO):
            unidades_por_vencer.append(unidad)

    return unidades_vencidas, unidades_por_vencer

def ordenar_por_vencer(unidades_por_vencer):
    # Ordena las unidades por vencer según la fecha de vencimiento, de más próxima a más lejana
    return sorted(unidades_por_vencer,
                  key = lambda unidad: parsear_fecha(unidad.fecha_vencimiento))