"""Semillas: sedes disponibles al iniciar el sistema (H3 · T3.1)."""

from .donacion import Sede

SEDES = [
    Sede("CON", "Sede Concepción", "Concepción"),
    Sede("TAL", "Sede Talcahuano", "Talcahuano"),
    Sede("CHI", "Sede Chillán", "Chillán"),
    Sede("LAN", "Sede Los Ángeles", "Los Ángeles"),
]


def buscar_sede(codigo):
    for sede in SEDES:
        if sede.codigo == codigo:
            return sede
    return None


def sede_por_nombre(nombre):
    for sede in SEDES:
        if sede.nombre == nombre:
            return sede
    return None
