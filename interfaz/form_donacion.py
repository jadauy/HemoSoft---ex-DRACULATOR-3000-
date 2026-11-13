"""Formulario de registro de donación (H3 · T3.5) con sus mensajes (T3.6)."""

from tkinter import Frame, Label, LabelFrame, messagebox

from donantes.sedes import SEDES, buscar_sede, sede_por_nombre
from donantes.servicio_donaciones import (DatosDonacionInvalidosError, DonacionRechazadaError,
                                          ServicioDonaciones)
from interfaz.comun import (FUENTE, FUENTE_CHICA, ROJO, TITULO_VENTANA, VERDE, boton, crear_entrada,
                            limpiar_campo, titulo)
from interfaz.dibujo_codigo import crear_lienzo, dibujar_codigo

VOLUMEN_HABITUAL = "450"


class FormularioDonacion(Frame):
    def __init__(self, padre, servicio=None):
        super().__init__(padre)
        self.servicio = servicio or ServicioDonaciones()

        titulo(self, "Registro de donación")
        self.marco = LabelFrame(self, text="Datos de la extracción", font=FUENTE, padx=5, pady=5)
        self.marco.pack(padx=10)
        self.entradas = {
            "rut": crear_entrada(self.marco, 0, "RUT del donante"),
            "sede": crear_entrada(self.marco, 1, "Sede", [s.nombre for s in SEDES]),
            "volumen": crear_entrada(self.marco, 2, "Volumen (ml)"),
        }
        self.entradas["volumen"].insert(0, VOLUMEN_HABITUAL)
        self.errores = {}
        for fila, campo in enumerate(self.entradas):
            self.errores[campo] = Label(self.marco, text="", fg=ROJO, font=FUENTE_CHICA, wraplength=170,
                                        justify="left")
            self.errores[campo].grid(row=fila, column=2, sticky="w")
        boton(self.marco, "Registrar", self.registrar).grid(row=3, column=1, pady=12)

        self.mensaje = Label(self, text="", font=FUENTE, wraplength=540, justify="left")
        self.mensaje.pack(padx=10)
        self.etiqueta_unidad = Label(self, text="", font=FUENTE, justify="left")
        self.etiqueta_unidad.pack(padx=10, pady=(6, 0))
        self.lienzo = crear_lienzo(self)
        self.lienzo.pack(pady=6)

    def leer_datos(self):
        datos = {campo: entrada.get() for campo, entrada in self.entradas.items()}
        sede = sede_por_nombre(datos["sede"])
        datos["sede"] = sede.codigo if sede else ""
        return datos

    def limpiar(self):
        for entrada in self.entradas.values():
            limpiar_campo(entrada)
        self.entradas["volumen"].insert(0, VOLUMEN_HABITUAL)

    def mostrar_errores(self, errores):
        for campo, etiqueta in self.errores.items():
            etiqueta.config(text=errores.get(campo, ""))

    def mostrar_unidad(self, unidad):
        if unidad is None:
            self.etiqueta_unidad.config(text="")
            dibujar_codigo(self.lienzo, "")
            return
        self.etiqueta_unidad.config(text=f"Unidad {unidad.codigo_barras} · {unidad.tipo} · "
                                         f"vence el {unidad.fecha_vencimiento}")
        dibujar_codigo(self.lienzo, unidad.codigo_barras)

    def registrar(self):
        self.mostrar_errores({})
        self.mostrar_unidad(None)
        try:
            donacion, unidad = self.servicio.registrar(self.leer_datos())
        except DatosDonacionInvalidosError as e:
            self.mostrar_errores(e.errores)
            self.mensaje.config(text="Faltan datos o hay datos inválidos: revise los campos marcados en rojo.",
                                fg=ROJO)
            return None
        except DonacionRechazadaError as e:
            texto = "No se puede registrar la donación:\n" + "\n".join(f"• {m}" for m in e.motivos)
            self.mensaje.config(text=texto, fg=ROJO)
            messagebox.showwarning(TITULO_VENTANA, texto)
            return None

        sede = buscar_sede(donacion.codigo_sede)
        texto = (f"Donación N° {donacion.idDonacion} registrada: {donacion.volumen_ml} ml del RUT "
                 f"{donacion.rut_donante} en {sede.nombre}. Etiquete la bolsa con el código {unidad.codigo_barras}.")
        self.mensaje.config(text=texto, fg=VERDE)
        self.mostrar_unidad(unidad)
        messagebox.showinfo(TITULO_VENTANA, texto)
        self.limpiar()
        return unidad
