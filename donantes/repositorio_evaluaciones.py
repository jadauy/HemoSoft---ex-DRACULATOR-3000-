"""Guardado de evaluaciones de elegibilidad en datos/evaluaciones.txt (H2 · T2.2)."""

from .archivo_txt import agregar_fila, leer_filas, ruta_datos
from .EvaluacionElegibilidad import EvaluacionElegibilidad
from .validaciones import parsear_fecha

COLUMNAS = EvaluacionElegibilidad.COLUMNAS


class RepositorioEvaluaciones:
    def __init__(self, ruta=None):
        self.ruta = ruta or ruta_datos("evaluaciones.txt")

    def listar(self):
        return [EvaluacionElegibilidad.desde_fila(f) for f in leer_filas(self.ruta, COLUMNAS)]

    def guardar(self, evaluacion):
        agregar_fila(self.ruta, COLUMNAS, evaluacion.a_fila())

    def siguiente_id(self):
        return max((e.idEvaluacion for e in self.listar()), default=0) + 1

    def por_rut(self, rut):
        """Evaluaciones de un donante, de la más antigua a la más reciente."""
        propias = [e for e in self.listar() if e.rut_donante == rut]
        return sorted(propias, key=lambda e: (parsear_fecha(e.fechaEvaluacion), e.idEvaluacion))

    def ultima_por_rut(self, rut):
        evaluaciones = self.por_rut(rut)
        return evaluaciones[-1] if evaluaciones else None
