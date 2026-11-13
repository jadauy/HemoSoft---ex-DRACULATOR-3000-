import os
import tempfile
import unittest
from datetime import date

from donantes.codigo_barras import codigo_valido
from donantes.repositorio import RepositorioDonantes
from donantes.repositorio_donaciones import RepositorioDonaciones
from donantes.repositorio_evaluaciones import RepositorioEvaluaciones
from donantes.servicio import ServicioDonantes
from donantes.servicio_donaciones import (DatosDonacionInvalidosError, DonacionRechazadaError,
                                          ServicioDonaciones)
from donantes.servicio_evaluaciones import ServicioEvaluaciones

HOY = date(2026, 11, 11)
EVALUACION_OK = {"peso": "62", "hemoglobina": "13,2", "presion_sistolica": "120", "presion_diastolica": "80"}


class Entorno:
    """Servicios conectados a archivos temporales, como en el programa real."""

    def __init__(self, carpeta):
        ruta = lambda n: os.path.join(carpeta, n)
        self.donantes = ServicioDonantes(RepositorioDonantes(ruta("d.txt")))
        self.repo_eval = RepositorioEvaluaciones(ruta("e.txt"))
        self.evaluaciones = ServicioEvaluaciones(self.repo_eval, self.donantes)
        self.repo_don = RepositorioDonaciones(ruta("don.txt"), ruta("u.txt"))
        self.donaciones = ServicioDonaciones(self.repo_don, self.donantes, self.repo_eval)

    def registrar_donante(self, rut="12.345.678-5", sexo="F"):
        self.donantes.registrar({"rut": rut, "nombre": "Ana Pérez", "fecha_nacimiento": "15-03-1990",
                                 "sexo": sexo, "peso": "62", "tipo_sangre": "O+", "telefono": "912345678"})

    def evaluar(self, rut="12.345.678-5", fecha=HOY, **cambios):
        return self.evaluaciones.evaluar(dict(EVALUACION_OK, rut=rut, **cambios), fecha)


class TestServicioDonaciones(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.e = Entorno(self.carpeta.name)
        self.e.registrar_donante()

    def tearDown(self):
        self.carpeta.cleanup()

    def donar(self, fecha=HOY, **cambios):
        return self.e.donaciones.registrar(dict({"rut": "12.345.678-5", "sede": "CON", "volumen": "450"}, **cambios),
                                           fecha)

    def test_donacion_exitosa_genera_unidad_con_codigo(self):
        self.e.evaluar()
        donacion, unidad = self.donar()
        self.assertEqual(donacion.rut_donante, "12345678-5")
        self.assertTrue(codigo_valido(unidad.codigo_barras))
        self.assertEqual(unidad.fecha_vencimiento, "23-12-2026")
        self.assertEqual(self.e.repo_don.buscar_unidad(unidad.codigo_barras).idDonacion, donacion.idDonacion)

    def test_codigos_distintos_en_la_misma_sede_y_dia(self):
        self.e.registrar_donante("11.111.111-1", sexo="M")
        self.e.evaluar()
        self.e.evaluar(rut="11.111.111-1", hemoglobina="14,5")  # mínimo de hombres: 13,5
        _, u1 = self.donar()
        _, u2 = self.donar(rut="11.111.111-1")
        self.assertNotEqual(u1.codigo_barras, u2.codigo_barras)

    def test_rechaza_sin_evaluacion_apto(self):
        with self.assertRaises(DonacionRechazadaError) as ctx:
            self.donar()
        self.assertIn("evaluación", ctx.exception.motivos[0])
        self.e.evaluar(peso="45")
        with self.assertRaises(DonacionRechazadaError) as ctx:
            self.donar()
        self.assertIn("DIFERIDO", ctx.exception.motivos[0])

    def test_rechaza_si_no_se_cumple_el_plazo(self):
        self.e.evaluar(fecha=date(2026, 9, 1))
        self.donar(fecha=date(2026, 9, 1))
        self.e.evaluar()
        with self.assertRaises(DonacionRechazadaError) as ctx:
            self.donar()
        self.assertIn("plazo mínimo", ctx.exception.motivos[0])

    def test_datos_invalidos_por_campo(self):
        with self.assertRaises(DatosDonacionInvalidosError) as ctx:
            self.donar(rut="", sede="XXX", volumen="900")
        self.assertEqual(set(ctx.exception.errores), {"rut", "sede", "volumen"})

    def test_donante_no_registrado(self):
        with self.assertRaises(DonacionRechazadaError) as ctx:
            self.donar(rut="10.000.013-K")
        self.assertIn("No hay un donante", ctx.exception.motivos[0])


if __name__ == "__main__":
    unittest.main()
