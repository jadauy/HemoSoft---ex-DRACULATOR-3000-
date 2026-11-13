"""Lectura y escritura de archivos .txt con una fila por registro y campos separados por ';'."""

import csv
import os

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")


def ruta_datos(nombre):
    return os.path.join(CARPETA_DATOS, nombre)


def leer_filas(ruta, columnas):
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo, fieldnames=columnas, delimiter=";")
        return [dict(fila) for fila in lector if fila.get(columnas[0])]


def agregar_fila(ruta, columnas, fila):
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "a", encoding="utf-8", newline="") as archivo:
        csv.DictWriter(archivo, fieldnames=columnas, delimiter=";").writerow({c: fila[c] for c in columnas})
