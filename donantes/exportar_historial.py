"""Exportar el historial de un donante a un archivo .txt legible (H5 · T5.3).

Recibe el historial que arma la consulta de T5.1, con este formato acordado:

    {
        "donante": {"rut", "nombre", "fecha_nacimiento", "sexo", "tipo_sangre", "telefono"},
        "evaluaciones": [{"fecha", "resultado", "motivos", "fecha_habilitacion"}, ...],
        "donaciones": [{"fecha", "sede", "volumen_ml", "codigo_unidad", "estado"}, ...],
        "estado_actual": "Puede donar hoy"   # opcional, lo calcula T5.2
    }

Las listas vienen de la más reciente a la más antigua.
"""

import os
from datetime import datetime

from .archivo_txt import ruta_datos
from .validaciones import FORMATO_FECHA

SIN_REGISTROS = "Sin registros."
ANCHO = 60


def _titulo(texto):
    return [texto, "-" * len(texto)]


def formatear_historial(historial, generado=None):
    """Devuelve el historial como texto, listo para guardar o mostrar."""
    generado = generado or datetime.now()
    donante = historial["donante"]
    lineas = [
        "=" * ANCHO,
        "HISTORIAL DEL DONANTE · HemoSoft",
        f"Generado el {generado.strftime(FORMATO_FECHA)} a las {generado.strftime('%H:%M')}",
        "=" * ANCHO,
        "",
        *_titulo("Datos del donante"),
        f"RUT:                 {donante['rut']}",
        f"Nombre:              {donante['nombre']}",
        f"Fecha de nacimiento: {donante['fecha_nacimiento']}",
        f"Sexo:                {donante['sexo']}",
        f"Grupo sanguíneo:     {donante['tipo_sangre']}",
        f"Teléfono:            {donante['telefono']}",
    ]
    if historial.get("estado_actual"):
        lineas.append(f"Estado actual:       {historial['estado_actual']}")

    evaluaciones = historial.get("evaluaciones") or []
    lineas += ["", *_titulo(f"Evaluaciones de elegibilidad ({len(evaluaciones)})")]
    if not evaluaciones:
        lineas.append(SIN_REGISTROS)
    for e in evaluaciones:
        linea = f"{e['fecha']}  {e['resultado']}"
        if e.get("fecha_habilitacion") and e["resultado"] != "APTO":
            linea += f"  (puede volver desde el {e['fecha_habilitacion']})"
        lineas.append(linea)
        for motivo in [m for m in (e.get("motivos") or "").split(" | ") if m]:
            lineas.append(f"    - {motivo}")

    donaciones = historial.get("donaciones") or []
    lineas += ["", *_titulo(f"Donaciones ({len(donaciones)})")]
    if not donaciones:
        lineas.append(SIN_REGISTROS)
    for d in donaciones:
        lineas.append(f"{d['fecha']}  {d['sede']}  {d['volumen_ml']} ml  unidad {d['codigo_unidad']}  [{d['estado']}]")

    return "\n".join(lineas) + "\n"


def ruta_por_defecto(rut, generado):
    nombre = f"historial_{rut.replace('.', '')}_{generado.strftime('%Y%m%d_%H%M%S')}.txt"
    return ruta_datos(os.path.join("historiales", nombre))


def exportar_historial(historial, ruta=None, generado=None):
    """Guarda el historial en un .txt y devuelve la ruta del archivo creado.

    Sin ruta, lo deja en datos/historiales/historial_<rut>_<fecha y hora>.txt.
    """
    generado = generado or datetime.now()
    ruta = ruta or ruta_por_defecto(historial["donante"]["rut"], generado)
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(formatear_historial(historial, generado))
    return ruta
