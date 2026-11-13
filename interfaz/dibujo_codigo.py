"""Dibuja un código de barras Code 39 en un Canvas de tkinter (H3 · T3.4)."""

from tkinter import Canvas

from donantes.codigo_barras import barras_code39

MARGEN = 12


def crear_lienzo(padre, alto=90):
    return Canvas(padre, width=520, height=alto, bg="white", highlightthickness=0)


def dibujar_codigo(lienzo, codigo, alto_barras=55):
    lienzo.delete("all")
    if not codigo:
        return
    elementos = barras_code39(codigo)
    ancho_total = sum(ancho for ancho, _ in elementos) + 2 * MARGEN
    lienzo.config(width=max(ancho_total, 200))
    x = MARGEN
    for ancho, es_barra in elementos:
        if es_barra:
            lienzo.create_rectangle(x, 8, x + ancho - 1, 8 + alto_barras, fill="black", outline="black")
        x += ancho
    lienzo.create_text(ancho_total / 2, 8 + alto_barras + 14, text=codigo, font=("Courier New", 12, "bold"))
