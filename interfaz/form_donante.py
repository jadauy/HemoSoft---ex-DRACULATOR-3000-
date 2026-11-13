"""Formulario de registro y búsqueda de donantes (H1)."""

from tkinter import Frame, Label, LabelFrame, messagebox

from donantes.servicio import DatosInvalidosError, DonanteDuplicadoError, ServicioDonantes
from donantes.validaciones import SEXOS, TIPOS_SANGRE
from interfaz.comun import (FUENTE, FUENTE_CHICA, ROJO, TITULO_VENTANA, VERDE, boton, crear_entrada,
                            limpiar_campo, titulo)

CAMPOS = [
    ("rut", "RUT (12.345.678-5)", None),
    ("nombre", "Nombre completo", None),
    ("fecha_nacimiento", "Fecha de nacimiento (DD-MM-AAAA)", None),
    ("sexo", "Sexo", SEXOS),
    ("peso", "Peso (kg)", None),
    ("tipo_sangre", "Tipo de sangre", TIPOS_SANGRE),
    ("telefono", "Teléfono (+56 9 ...)", None),
]


class FormularioDonante(Frame):
    def __init__(self, padre, servicio=None):
        super().__init__(padre)
        self.servicio = servicio or ServicioDonantes()
        self.entradas = {}
        self.errores = {}

        titulo(self, "Registro de donante")
        marco = LabelFrame(self, text="Ingrese los datos del donante", font=FUENTE, padx=5, pady=5)
        marco.pack(padx=10)
        for fila, (campo, etiqueta, opciones) in enumerate(CAMPOS):
            self.entradas[campo] = crear_entrada(marco, fila, etiqueta, opciones)
            self.errores[campo] = Label(marco, text="", fg=ROJO, font=FUENTE_CHICA, wraplength=170, justify="left")
            self.errores[campo].grid(row=fila, column=2, sticky="w")
        boton(marco, "Registrar", self.registrar).grid(row=len(CAMPOS), column=1, pady=12)
        self.mensaje = Label(marco, text="", font=FUENTE, wraplength=420)
        self.mensaje.grid(row=len(CAMPOS) + 1, column=0, columnspan=3)

        busqueda = LabelFrame(self, text="Buscar donante por RUT", font=FUENTE, padx=5, pady=5)
        busqueda.pack(padx=10, pady=10, fill="x")
        self.rut_busqueda = crear_entrada(busqueda, 0, "RUT")
        boton(busqueda, "Buscar", self.buscar).grid(row=0, column=2, padx=5)
        self.resultado_busqueda = Label(busqueda, text="", font=FUENTE, justify="left")
        self.resultado_busqueda.grid(row=1, column=0, columnspan=3, sticky="w", padx=10)

    def leer_datos(self):
        """Lee lo que el usuario escribió en este momento (no al crear la ventana)."""
        return {campo: entrada.get() for campo, entrada in self.entradas.items()}

    def limpiar(self):
        for entrada in self.entradas.values():
            limpiar_campo(entrada)

    def mostrar_errores(self, errores):
        """Escribe cada error junto a su campo y borra los de los campos que ya están bien."""
        for campo, etiqueta in self.errores.items():
            etiqueta.config(text=errores.get(campo, ""))

    def registrar(self):
        self.mostrar_errores({})
        try:
            donante = self.servicio.registrar(self.leer_datos())
        except DatosInvalidosError as e:
            self.mostrar_errores(e.errores)
            self.mensaje.config(text=f"No se pudo registrar: revise los {len(e.errores)} campo(s) marcados en rojo.",
                                fg=ROJO)
            return None
        except DonanteDuplicadoError:
            self.mostrar_errores({"rut": "Este RUT ya está registrado."})
            self.mensaje.config(text="El donante ya existe. Use la búsqueda por RUT para ver sus datos.", fg=ROJO)
            messagebox.showwarning(TITULO_VENTANA, "Ya existe un donante registrado con ese RUT.")
            return None
        texto = f"Donante {donante['nombre']} ({donante['rut']}) registrado correctamente."
        self.mensaje.config(text=texto, fg=VERDE)
        messagebox.showinfo(TITULO_VENTANA, texto)
        self.limpiar()
        return donante

    def buscar(self):
        donante = self.servicio.buscar_por_rut(self.rut_busqueda.get())
        if not donante:
            self.resultado_busqueda.config(text="No se encontró un donante con ese RUT.")
            return None
        lineas = [f"{etiqueta.split(' (')[0]}: {donante[campo]}" for campo, etiqueta, _ in CAMPOS]
        self.resultado_busqueda.config(text="\n".join(lineas))
        return donante
