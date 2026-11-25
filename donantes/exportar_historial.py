"""Exportar el historial de un donante a un archivo .txt (H5 · T5.3). En curso.

Avance: dónde y cómo se guarda el archivo.
Pendiente: armar el texto del historial, cuando esté definido el historial de T5.1.
"""

import os
from datetime import datetime

from .archivo_txt import ruta_datos


def ruta_por_defecto(rut, generado=None):
    """datos/historiales/historial_<rut>_<AAAAMMDD_HHMMSS>.txt"""
    generado = generado or datetime.now()
    nombre = f"historial_{rut.replace('.', '')}_{generado.strftime('%Y%m%d_%H%M%S')}.txt"
    return ruta_datos(os.path.join("historiales", nombre))


def guardar_texto(texto, ruta):
    """Guarda el texto en UTF-8, creando la carpeta si no existe, y devuelve la ruta."""
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(texto)
    return ruta
