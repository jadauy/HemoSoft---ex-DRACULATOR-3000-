import tempfile
import unittest
from datetime import date
from tkinter import TclError, Tk
from unittest import mock

from interfaz.form_donacion import FormularioDonacion
from test_servicio_donaciones import Entorno


class TestFormularioDonacion(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = Tk()
        except TclError:
            self.skipTest("No hay pantalla disponible para probar la interfaz")
        self.raiz.withdraw()
        self.carpeta = tempfile.TemporaryDirectory()
        self.e = Entorno(self.carpeta.name)
        self.e.registrar_donante()
        self.form = FormularioDonacion(self.raiz, self.e.donaciones)

    def tearDown(self):
        self.raiz.destroy()
        self.carpeta.cleanup()

    def llenar(self, rut="12.345.678-5", sede="Sede Concepción"):
        self.form.entradas["rut"].insert(0, rut)
        self.form.entradas["sede"].set(sede)

    @mock.patch("interfaz.form_donacion.messagebox")
    def test_confirmacion_con_codigo(self, mb):
        self.e.evaluar(fecha=date.today())
        self.llenar()
        unidad = self.form.registrar()
        self.assertIn(unidad.codigo_barras, self.form.mensaje.cget("text"))
        self.assertIn("vence el", self.form.etiqueta_unidad.cget("text"))
        self.assertTrue(self.form.lienzo.find_all())  # se dibujó el código
        mb.showinfo.assert_called_once()

    @mock.patch("interfaz.form_donacion.messagebox")
    def test_rechazo_por_donante_no_apto(self, mb):
        self.e.evaluar(fecha=date.today(), peso="45")
        self.llenar()
        self.assertIsNone(self.form.registrar())
        self.assertIn("DIFERIDO", self.form.mensaje.cget("text"))
        self.assertFalse(self.form.lienzo.find_all())
        mb.showwarning.assert_called_once()

    @mock.patch("interfaz.form_donacion.messagebox")
    def test_datos_faltantes_marcados_por_campo(self, _):
        self.form.entradas["volumen"].delete(0, "end")
        self.assertIsNone(self.form.registrar())
        for campo in ("rut", "sede", "volumen"):
            self.assertEqual(self.form.errores[campo].cget("text"), "Campo obligatorio.")


if __name__ == "__main__":
    unittest.main()
