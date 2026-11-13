import tempfile
import unittest
from datetime import date
from tkinter import TclError, Tk

from interfaz.busqueda_unidad import BusquedaUnidad
from test_servicio_donaciones import HOY, Entorno


class TestTrazabilidad(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.e = Entorno(self.carpeta.name)
        self.e.registrar_donante()
        self.e.evaluar()
        _, self.unidad = self.e.donaciones.registrar({"rut": "12.345.678-5", "sede": "TAL", "volumen": "450"}, HOY)

    def tearDown(self):
        self.carpeta.cleanup()

    def test_traza_completa_de_la_unidad(self):
        traza = self.e.donaciones.buscar_unidad(self.unidad.codigo_barras.lower(), HOY)
        self.assertEqual(traza["donante"]["nombre"], "Ana Pérez")
        self.assertEqual(traza["sede"].codigo, "TAL")
        self.assertEqual((traza["estado"], traza["dias_restantes"]), ("VIGENTE", 42))

    def test_unidad_vencida(self):
        traza = self.e.donaciones.buscar_unidad(self.unidad.codigo_barras, date(2027, 1, 1))
        self.assertEqual(traza["estado"], "VENCIDA")

    def test_codigo_inexistente(self):
        self.assertIsNone(self.e.donaciones.buscar_unidad("TAL26111199990"))


class TestPantallaBusqueda(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = Tk()
        except TclError:
            self.skipTest("No hay pantalla disponible para probar la interfaz")
        self.raiz.withdraw()
        self.carpeta = tempfile.TemporaryDirectory()
        self.e = Entorno(self.carpeta.name)
        self.e.registrar_donante()
        self.e.evaluar(fecha=date.today())
        _, self.unidad = self.e.donaciones.registrar({"rut": "12.345.678-5", "sede": "CON", "volumen": "450"})
        self.pantalla = BusquedaUnidad(self.raiz, self.e.donaciones)

    def tearDown(self):
        self.raiz.destroy()
        self.carpeta.cleanup()

    def test_muestra_datos_y_dibuja_el_codigo(self):
        self.pantalla.codigo.insert(0, self.unidad.codigo_barras)
        self.assertIsNotNone(self.pantalla.buscar())
        self.assertEqual(self.pantalla.estado.cget("text"), "VIGENTE")
        self.assertIn("Ana Pérez", self.pantalla.detalle.cget("text"))
        self.assertTrue(self.pantalla.lienzo.find_all())

    def test_codigo_mal_digitado_o_inexistente(self):
        self.pantalla.codigo.insert(0, "CON123")
        self.assertIsNone(self.pantalla.buscar())
        self.assertIn("no es válido", self.pantalla.detalle.cget("text"))


if __name__ == "__main__":
    unittest.main()
