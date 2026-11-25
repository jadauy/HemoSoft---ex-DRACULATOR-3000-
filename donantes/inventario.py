"""Stock vigente de unidades por grupo sanguíneo (H4 · T4.1).

Cada unidad guarda su código y fechas, pero no su grupo sanguíneo: el grupo se obtiene siguiendo
unidad → donación → donante. Una unidad está vigente hasta el día de su vencimiento, inclusive.
"""

from datetime import date

from .repositorio_donaciones import RepositorioDonaciones
from .servicio import ServicioDonantes
from .validaciones import TIPOS_SANGRE, parsear_fecha


class UnidadInventario:
    """Una unidad junto con su donación de origen y el grupo sanguíneo de su donante."""

    def __init__(self, unidad, donacion, tipo_sangre):
        self.unidad = unidad
        self.donacion = donacion
        self.tipo_sangre = tipo_sangre  # None si no se encuentra el donante

    @property
    def fecha_vencimiento(self):
        return parsear_fecha(self.unidad.fecha_vencimiento)

    def esta_vigente(self, hoy):
        return hoy <= self.fecha_vencimiento


class Inventario:
    def __init__(self, repositorio=None, servicio_donantes=None):
        self.repositorio = repositorio or RepositorioDonaciones()
        self.servicio_donantes = servicio_donantes or ServicioDonantes()

    def unidades(self):
        """Todas las unidades guardadas, con su donación y grupo sanguíneo."""
        donaciones = {d.idDonacion: d for d in self.repositorio.listar_donaciones()}
        grupos = {d["rut"]: d["tipo_sangre"] for d in self.servicio_donantes.repositorio.listar()}
        resultado = []
        for unidad in self.repositorio.listar_unidades():
            donacion = donaciones.get(unidad.idDonacion)
            tipo = grupos.get(donacion.rut_donante) if donacion else None
            resultado.append(UnidadInventario(unidad, donacion, tipo))
        return resultado

    def unidades_vigentes(self, hoy=None):
        hoy = hoy or date.today()
        return [u for u in self.unidades() if u.esta_vigente(hoy)]

    def stock_por_grupo(self, hoy=None):
        """Cantidad de unidades vigentes por cada uno de los 8 grupos, incluidos los que tienen 0."""
        stock = {grupo: 0 for grupo in TIPOS_SANGRE}
        for u in self.unidades_vigentes(hoy):
            if u.tipo_sangre in stock:
                stock[u.tipo_sangre] += 1
        return stock

    def total_vigente(self, hoy=None):
        return sum(self.stock_por_grupo(hoy).values())
