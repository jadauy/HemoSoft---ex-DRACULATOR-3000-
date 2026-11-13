"""Búsqueda y trazabilidad de una unidad por su código de barras (H3 · T3.7)."""

from tkinter import Frame, Label, LabelFrame

from donantes.codigo_barras import codigo_valido
from donantes.servicio_donaciones import ServicioDonaciones
from interfaz.comun import FUENTE, ROJO, VERDE, boton, crear_entrada, titulo
from interfaz.dibujo_codigo import crear_lienzo, dibujar_codigo


class BusquedaUnidad(Frame):
    def __init__(self, padre, servicio=None):
        super().__init__(padre)
        self.servicio = servicio or ServicioDonaciones()

        titulo(self, "Trazabilidad de unidades")
        marco = LabelFrame(self, text="Buscar unidad por código de barras", font=FUENTE, padx=5, pady=5)
        marco.pack(padx=10, fill="x")
        self.codigo = crear_entrada(marco, 0, "Código")
        self.codigo.bind("<Return>", lambda _: self.buscar())  # los lectores de código terminan con Enter
        boton(marco, "Buscar", self.buscar).grid(row=0, column=2, padx=5)

        self.estado = Label(self, text="", font=(FUENTE[0], 16, "bold"))
        self.estado.pack(pady=(10, 0))
        self.detalle = Label(self, text="", font=FUENTE, justify="left", wraplength=540)
        self.detalle.pack(padx=10)
        self.lienzo = crear_lienzo(self)
        self.lienzo.pack(pady=6)

    def buscar(self):
        codigo = self.codigo.get().strip().upper()
        self.estado.config(text="")
        dibujar_codigo(self.lienzo, "")
        if not codigo:
            self.detalle.config(text="Ingrese o escanee un código.", fg=ROJO)
            return None
        if not codigo_valido(codigo):
            self.detalle.config(text="El código no es válido (revise que esté bien digitado).", fg=ROJO)
            return None
        traza = self.servicio.buscar_unidad(codigo)
        if traza is None:
            self.detalle.config(text=f"No existe una unidad con el código {codigo}.", fg=ROJO)
            return None

        unidad, donacion, donante, sede = traza["unidad"], traza["donacion"], traza["donante"], traza["sede"]
        vigente = traza["estado"] == "VIGENTE"
        self.estado.config(text=traza["estado"], fg=VERDE if vigente else ROJO)
        plazo = (f"quedan {traza['dias_restantes']} días" if vigente
                 else f"venció hace {-traza['dias_restantes']} días")
        nombre = donante["nombre"] if donante else "(donante no encontrado)"
        tipo_sangre = donante["tipo_sangre"] if donante else "-"
        self.detalle.config(fg="black", text="\n".join([
            f"Unidad: {unidad.codigo_barras} · {unidad.tipo} · grupo {tipo_sangre}",
            f"Donante: {nombre} (RUT {donacion.rut_donante})",
            f"Donación N° {donacion.idDonacion}: {donacion.volumen_ml} ml en {sede.nombre if sede else donacion.codigo_sede}",
            f"Extracción: {unidad.fecha_extraccion} · Vencimiento: {unidad.fecha_vencimiento} ({plazo})",
        ]))
        dibujar_codigo(self.lienzo, unidad.codigo_barras)
        return traza
