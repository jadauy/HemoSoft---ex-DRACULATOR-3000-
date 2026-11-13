import unittest
from datetime import date

from donantes.donacion import Donacion
from donantes.EvaluacionElegibilidad import APTO, DIFERIDO, EvaluacionElegibilidad
from donantes.requisitos_donacion import sumar_meses, verificar_puede_donar

HOY = date(2026, 11, 11)
MUJER = {"sexo": "F"}
HOMBRE = {"sexo": "M"}


def evaluacion(fecha="11-11-2026", resultado=APTO):
    return EvaluacionElegibilidad(1, fecha, resultado, fecha)


def donacion(fecha):
    return Donacion(1, "12345678-5", fecha, "CON", 450)


class TestRequisitosDonacion(unittest.TestCase):
    def test_apto_hoy_y_sin_donaciones_puede_donar(self):
        self.assertEqual(verificar_puede_donar(MUJER, evaluacion(), None, HOY), [])

    def test_sin_evaluacion(self):
        self.assertIn("no tiene una evaluación", verificar_puede_donar(MUJER, None, None, HOY)[0])

    def test_evaluacion_de_otro_dia(self):
        self.assertIn("mismo día", verificar_puede_donar(MUJER, evaluacion("10-11-2026"), None, HOY)[0])

    def test_evaluacion_no_apto(self):
        self.assertIn("DIFERIDO", verificar_puede_donar(MUJER, evaluacion(resultado=DIFERIDO), None, HOY)[0])

    def test_plazo_mujer_4_meses(self):
        self.assertIn("4 meses", verificar_puede_donar(MUJER, evaluacion(), donacion("12-07-2026"), HOY)[0])
        self.assertEqual(verificar_puede_donar(MUJER, evaluacion(), donacion("11-07-2026"), HOY), [])

    def test_plazo_hombre_3_meses(self):
        self.assertIn("16-11-2026", verificar_puede_donar(HOMBRE, evaluacion(), donacion("16-08-2026"), HOY)[0])
        self.assertEqual(verificar_puede_donar(HOMBRE, evaluacion(), donacion("11-08-2026"), HOY), [])

    def test_sumar_meses_ajusta_fin_de_mes(self):
        self.assertEqual(sumar_meses(date(2026, 11, 30), 3), date(2027, 2, 28))


if __name__ == "__main__":
    unittest.main()
