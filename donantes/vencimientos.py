"""Consultas de unidades próximas a vencer y vencidas."""

from datetime import date

from .inventario import Inventario


class Vencimientos:
    DIAS_ALERTA = 7

    def __init__(self, inventario=None):
        self.inventario = inventario or Inventario()

    def unidades_por_vencer(self, hoy=None, sede=None):
        """Unidades vigentes que vencen dentro de los próximos 7 días, ordenadas por fecha."""
        hoy = hoy or date.today()
        unidades = [
            unidad for unidad in self.inventario.unidades(sede)
            if 0 <= (unidad.fecha_vencimiento - hoy).days < self.DIAS_ALERTA
        ]
        return sorted(unidades, key=lambda unidad: unidad.fecha_vencimiento)

    def unidades_vencidas(self, hoy=None, sede=None):
        """Unidades vencidas; no forman parte del stock vigente."""
        hoy = hoy or date.today()
        unidades = [
            unidad for unidad in self.inventario.unidades(sede)
            if unidad.fecha_vencimiento < hoy
        ]
        return sorted(unidades, key=lambda unidad: unidad.fecha_vencimiento, reverse=True)
