import os
import tempfile
import unittest

from donantes.EvaluacionElegibilidad import APTO, DIFERIDO, EvaluacionElegibilidad
from donantes.repositorio_evaluaciones import RepositorioEvaluaciones


def evaluacion(id_, fecha, resultado=APTO, rut="12345678-5"):
    return EvaluacionElegibilidad(id_, fecha, resultado, fecha, rut_donante=rut, peso=62.0, hemoglobina=13.1,
                                  presion_sistolica=120, presion_diastolica=80, causa_temporal=False,
                                  causa_permanente=False, motivos="")


class TestRepositorioEvaluaciones(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.repo = RepositorioEvaluaciones(os.path.join(self.carpeta.name, "evaluaciones.txt"))

    def tearDown(self):
        self.carpeta.cleanup()

    def test_guarda_y_lee_todos_los_campos(self):
        original = evaluacion(1, "10-11-2026")
        original.causa_temporal = True
        original.motivos = "Peso bajo 50 kg. | Hemoglobina baja."
        self.repo.guardar(original)
        leida = self.repo.listar()[0]
        for campo in EvaluacionElegibilidad.COLUMNAS:
            self.assertEqual(getattr(leida, campo), getattr(original, campo), campo)

    def test_dos_evaluaciones_del_mismo_rut(self):
        self.repo.guardar(evaluacion(1, "01-11-2026", DIFERIDO))
        self.repo.guardar(evaluacion(2, "10-11-2026", APTO))
        self.repo.guardar(evaluacion(3, "05-11-2026", APTO, rut="11111111-1"))
        self.assertEqual([e.idEvaluacion for e in self.repo.por_rut("12345678-5")], [1, 2])
        self.assertEqual(self.repo.ultima_por_rut("12345678-5").resultado, APTO)

    def test_siguiente_id_y_rut_sin_evaluaciones(self):
        self.assertEqual(self.repo.siguiente_id(), 1)
        self.repo.guardar(evaluacion(1, "10-11-2026"))
        self.assertEqual(self.repo.siguiente_id(), 2)
        self.assertIsNone(self.repo.ultima_por_rut("11111111-1"))


if __name__ == "__main__":
    unittest.main()
