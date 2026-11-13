"""DRACULATOR 3000: ventana principal del sistema."""

import os
from tkinter import Tk, ttk

from interfaz.form_donante import FormularioDonante
from interfaz.form_donacion import FormularioDonacion
from interfaz.form_evaluacion import FormularioEvaluacion
from interfaz.busqueda_unidad import BusquedaUnidad

RAIZ = os.path.dirname(os.path.abspath(__file__))
ICONO = os.path.join(RAIZ, "assets", "sangre_icon.ico")


def crear_ventana():
    ventana = Tk()
    ventana.title("Draculator 3000")
    ventana.geometry("620x760")
    try:
        ventana.iconbitmap(ICONO)
    except Exception:  # Sin ícono en sistemas que no lo soportan
        pass

    pestanas = ttk.Notebook(ventana)
    pestanas.pack(fill="both", expand=True)
    pestanas.add(FormularioDonante(pestanas), text="Donantes")
    pestanas.add(FormularioEvaluacion(pestanas), text="Evaluación")
    pestanas.add(FormularioDonacion(pestanas), text="Donación")
    pestanas.add(BusquedaUnidad(pestanas), text="Buscar unidad")
    return ventana


if __name__ == "__main__":
    crear_ventana().mainloop()
