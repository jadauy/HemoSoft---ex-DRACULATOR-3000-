"""Guardado de donaciones y unidades en datos/donaciones.txt y datos/unidades.txt (H3 · T3.2)."""

from .archivo_txt import agregar_fila, leer_filas, ruta_datos
from .donacion import Donacion, Hemocomponente
from .validaciones import parsear_fecha


class RepositorioDonaciones:
    def __init__(self, ruta_donaciones=None, ruta_unidades=None):
        self.ruta_donaciones = ruta_donaciones or ruta_datos("donaciones.txt")
        self.ruta_unidades = ruta_unidades or ruta_datos("unidades.txt")

    # ---- Donaciones ----
    def listar_donaciones(self):
        return [Donacion.desde_fila(f) for f in leer_filas(self.ruta_donaciones, Donacion.COLUMNAS)]

    def guardar_donacion(self, donacion):
        agregar_fila(self.ruta_donaciones, Donacion.COLUMNAS, donacion.a_fila())

    def siguiente_id_donacion(self):
        return max((d.idDonacion for d in self.listar_donaciones()), default=0) + 1

    def buscar_donacion(self, id_donacion):
        for d in self.listar_donaciones():
            if d.idDonacion == id_donacion:
                return d
        return None

    def donaciones_por_rut(self, rut):
        """Donaciones de un donante, de la más antigua a la más reciente."""
        propias = [d for d in self.listar_donaciones() if d.rut_donante == rut]
        return sorted(propias, key=lambda d: (parsear_fecha(d.fecha), d.idDonacion))

    def ultima_donacion(self, rut):
        donaciones = self.donaciones_por_rut(rut)
        return donaciones[-1] if donaciones else None

    # ---- Unidades ----
    def listar_unidades(self):
        return [Hemocomponente.desde_fila(f) for f in leer_filas(self.ruta_unidades, Hemocomponente.COLUMNAS)]

    def guardar_unidad(self, unidad):
        agregar_fila(self.ruta_unidades, Hemocomponente.COLUMNAS, unidad.a_fila())

    def buscar_unidad(self, codigo_barras):
        codigo = codigo_barras.strip().upper()
        for u in self.listar_unidades():
            if u.codigo_barras == codigo:
                return u
        return None

    def unidades_de_donacion(self, id_donacion):
        return [u for u in self.listar_unidades() if u.idDonacion == id_donacion]

    def contar_donaciones(self, codigo_sede, fecha):
        """Cuántas donaciones lleva una sede en una fecha (sirve para el correlativo del código)."""
        return sum(1 for d in self.listar_donaciones() if d.codigo_sede == codigo_sede and d.fecha == fecha)
