import os
import tempfile
import unittest
from datetime import date

from donantes.elegibilidad import calcular_resultado
from donantes.EvaluacionElegibilidad import APTO, DIFERIDO, NO_APTO
from donantes.repositorio import RepositorioDonantes
from donantes.repositorio_evaluaciones import RepositorioEvaluaciones
from donantes.servicio import ServicioDonantes
from donantes.servicio_evaluaciones import (DatosEvaluacionInvalidosError, DonanteNoRegistradoError,
                                            ServicioEvaluaciones)

HOY = date(2026, 11, 11)
NACIDA_1990 = date(1990, 3, 15)


def calcular(**cambios):
    datos = dict(sexo="F", fecha_nacimiento=NACIDA_1990, fecha=HOY, peso=62, hemoglobina=13.0,
                 sistolica=120, diastolica=80, causa_temporal=False, causa_permanente=False)
    datos.update(cambios)
    return calcular_resultado(**datos)


class TestCalcularResultado(unittest.TestCase):
    def test_apto(self):
        self.assertEqual(calcular(), (APTO, [], HOY))

    def test_diferido_por_peso_y_hemoglobina(self):
        resultado, motivos, habilitacion = calcular(peso=48, hemoglobina=11.9)
        self.assertEqual(resultado, DIFERIDO)
        self.assertEqual(len(motivos), 2)
        self.assertEqual(habilitacion, date(2026, 12, 11))

    def test_hemoglobina_minima_depende_del_sexo(self):
        self.assertEqual(calcular(sexo="F", hemoglobina=13.0)[0], APTO)
        self.assertEqual(calcular(sexo="M", hemoglobina=13.0)[0], DIFERIDO)

    def test_presion_fuera_de_rango(self):
        self.assertEqual(calcular(sistolica=190)[0], DIFERIDO)
        self.assertEqual(calcular(diastolica=45)[0], DIFERIDO)

    def test_menor_de_edad_se_habilita_al_cumplir_18(self):
        resultado, _, habilitacion = calcular(fecha_nacimiento=date(2009, 6, 1))
        self.assertEqual(resultado, DIFERIDO)
        self.assertEqual(habilitacion, date(2027, 6, 1))

    def test_no_apto_por_causa_permanente_o_edad(self):
        self.assertEqual(calcular(causa_permanente=True)[0], NO_APTO)
        resultado, _, habilitacion = calcular(fecha_nacimiento=date(1958, 1, 1))
        self.assertEqual((resultado, habilitacion), (NO_APTO, None))


class TestServicioEvaluaciones(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        donantes = ServicioDonantes(RepositorioDonantes(os.path.join(self.carpeta.name, "d.txt")))
        donantes.registrar({"rut": "12.345.678-5", "nombre": "Ana Pérez", "fecha_nacimiento": "15-03-1990",
                            "sexo": "F", "peso": "62", "tipo_sangre": "O+", "telefono": "912345678"})
        self.servicio = ServicioEvaluaciones(RepositorioEvaluaciones(os.path.join(self.carpeta.name, "e.txt")),
                                             donantes)
        self.datos = {"rut": "12345678-5", "peso": "62", "hemoglobina": "13,2", "presion_sistolica": "120",
                      "presion_diastolica": "80"}

    def tearDown(self):
        self.carpeta.cleanup()

    def test_evalua_guarda_y_queda_en_historial(self):
        evaluacion = self.servicio.evaluar(self.datos, HOY)
        self.assertEqual((evaluacion.resultado, evaluacion.fechaEvaluacion), (APTO, "11-11-2026"))
        self.servicio.evaluar(dict(self.datos, peso="45"), HOY)
        historial = self.servicio.historial("12.345.678-5")
        self.assertEqual([e.resultado for e in historial], [APTO, DIFERIDO])
        self.assertIn("Peso", historial[-1].motivos)

    def test_datos_invalidos_por_campo(self):
        with self.assertRaises(DatosEvaluacionInvalidosError) as ctx:
            self.servicio.evaluar({"rut": "12.345.678-9", "peso": "abc", "presion_sistolica": "120.5"}, HOY)
        errores = ctx.exception.errores
        self.assertEqual(set(errores), {"rut", "peso", "hemoglobina", "presion_sistolica", "presion_diastolica"})
        self.assertIn("entero", errores["presion_sistolica"])

    def test_donante_no_registrado(self):
        with self.assertRaises(DonanteNoRegistradoError):
            self.servicio.evaluar(dict(self.datos, rut="11.111.111-1"), HOY)


if __name__ == "__main__":
    unittest.main()
