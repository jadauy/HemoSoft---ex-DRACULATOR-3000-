"""Código de barras único por unidad y fecha de vencimiento (H3 · T3.4).

Formato del código: SSS AAMMDD NNNN V  (sin espacios)
  SSS   código de la sede (3 letras)
  AAMMDD fecha de extracción
  NNNN  correlativo de la donación en esa sede y día
  V     dígito verificador (módulo 10) para detectar errores al digitar
Se imprime en Code 39, que acepta letras mayúsculas y números.
"""

from datetime import timedelta

VIDA_UTIL_DIAS = 42  # decisión del PO

# Code 39: 9 elementos por carácter (barra, espacio, barra, ...); n = angosto, w = ancho.
CODE39 = {
    "0": "nnnwwnwnn", "1": "wnnwnnnnw", "2": "nnwwnnnnw", "3": "wnwwnnnnn", "4": "nnnwwnnnw",
    "5": "wnnwwnnnn", "6": "nnwwwnnnn", "7": "nnnwnnwnw", "8": "wnnwnnwnn", "9": "nnwwnnwnn",
    "A": "wnnnnwnnw", "B": "nnwnnwnnw", "C": "wnwnnwnnn", "D": "nnnnwwnnw", "E": "wnnnwwnnn",
    "F": "nnwnwwnnn", "G": "nnnnnwwnw", "H": "wnnnnwwnn", "I": "nnwnnwwnn", "J": "nnnnwwwnn",
    "K": "wnnnnnnww", "L": "nnwnnnnww", "M": "wnwnnnnwn", "N": "nnnnwnnww", "O": "wnnnwnnwn",
    "P": "nnwnwnnwn", "Q": "nnnnnnwww", "R": "wnnnnnwwn", "S": "nnwnnnwwn", "T": "nnnnwnwwn",
    "U": "wwnnnnnnw", "V": "nwwnnnnnw", "W": "wwwnnnnnn", "X": "nwnnwnnnw", "Y": "wwnnwnnnn",
    "Z": "nwwnwnnnn", "-": "nwnnnnwnw", "*": "nwnnwnwnn",
}


def digito_verificador(texto):
    """Módulo 10 sobre los dígitos (las letras valen su posición en el alfabeto)."""
    valores = [int(c) if c.isdigit() else ord(c) - ord("A") + 10 for c in texto]
    suma = sum(v * (3 if i % 2 == 0 else 1) for i, v in enumerate(reversed(valores)))
    return str((10 - suma % 10) % 10)


def generar_codigo(codigo_sede, fecha_extraccion, correlativo):
    base = f"{codigo_sede.upper()}{fecha_extraccion.strftime('%y%m%d')}{correlativo:04d}"
    return base + digito_verificador(base)


def codigo_valido(codigo):
    codigo = codigo.strip().upper()
    return len(codigo) == 14 and codigo[:3].isalpha() and codigo[3:].isdigit() and \
        digito_verificador(codigo[:-1]) == codigo[-1]


def fecha_vencimiento(fecha_extraccion):
    return fecha_extraccion + timedelta(days=VIDA_UTIL_DIAS)


def barras_code39(codigo, angosto=2, ancho=5):
    """Lista de (ancho_en_pixeles, es_barra) para dibujar el código, con * de inicio y fin."""
    elementos = []
    for caracter in f"*{codigo.upper()}*":
        for i, tipo in enumerate(CODE39[caracter]):
            elementos.append((ancho if tipo == "w" else angosto, i % 2 == 0))
        elementos.append((angosto, False))  # separación entre caracteres
    return elementos[:-1]
