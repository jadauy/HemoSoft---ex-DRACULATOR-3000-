"""Determina las unidades por vencer y las que ya vencieron"""

# Una unidad de sangre debe tener su código, grupo sanguíneo (este debe ser sacado del donante), fecha de extracción y fecha de vencimiento

from datetime import date, timedelta
DIAS_VENCIMIENTO = 7

# Se saca una lista de elementos de variable "Hemocomponente", debe ser una lista para sacar cada unidad de sangre por separado
def calcular_vencimientos(unidades_sangre):
    fecha_hoy = date.today()
    unidades_vencidas = []
    unidades_por_vencer = []

    for unidad in unidades_sangre:
        fecha_vencimiento = unidad.fecha_extraccion + timedelta(days = DIAS_VENCIMIENTO)

        if fecha_hoy >= fecha_vencimiento:
            unidades_vencidas.append(unidad)

        # TODO: Verificar si todas las unidades "por vencer" son las que están dentro del rango [unidad.fecha_extraccion, fecha_vencimiento] ó es cualquier fecha que esté antes de fecha_vencimiento
        
        elif fecha_hoy < fecha_vencimiento:
            unidades_por_vencer.append(unidad)

    return unidades_vencidas, unidades_por_vencer

def ordenar_por_vencer(unidades_por_vencer):
    return sorted(unidades_por_vencer,
                  key = lambda unidad: unidad.fecha_extraccion + timedelta(days = DIAS_VENCIMIENTO))