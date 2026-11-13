"""Estilos y piezas compartidas por todas las pantallas."""

from tkinter import Button, Entry, Label, ttk

FUENTE = ("Times New Roman", 12)
FUENTE_TITULO = ("Times New Roman", 14)
FUENTE_CHICA = ("Times New Roman", 10)
ROJO = "#b3261e"
VERDE = "#2e7d32"
NARANJO = "#b26a00"
TITULO_VENTANA = "Draculator 3000"


def titulo(padre, texto):
    etiqueta = Label(padre, text=texto, font=FUENTE_TITULO, pady=10)
    etiqueta.pack()
    return etiqueta


def boton(padre, texto, accion):
    return Button(padre, text=texto, command=accion, height=2, width=12, bg="red", fg="white",
                  font=(FUENTE[0], FUENTE[1], "bold"))


def crear_entrada(padre, fila, etiqueta, opciones=None):
    """Agrega una fila «etiqueta: campo» al formulario y devuelve el campo.

    Si se pasan opciones, el campo es una lista desplegable de solo lectura.
    """
    Label(padre, text=etiqueta + ":", font=FUENTE).grid(row=fila, column=0, sticky="e", padx=10, pady=4)
    if opciones is not None:
        campo = ttk.Combobox(padre, values=opciones, state="readonly", width=23, font=FUENTE)
    else:
        campo = Entry(padre, width=25, font=FUENTE)
    campo.grid(row=fila, column=1, padx=10, pady=4)
    return campo


def limpiar_campo(campo):
    if isinstance(campo, ttk.Combobox):
        campo.set("")
    else:
        campo.delete(0, "end")
