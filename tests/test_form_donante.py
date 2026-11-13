import os
import tempfile
import unittest
from tkinter import TclError, Tk
from unittest import mock

from donantes.repositorio import RepositorioDonantes
from donantes.servicio import ServicioDonantes
from interfaz.form_donante import FormularioDonante

DATOS = {
    "rut": "12.345.678-5", "nombre": "Ana Pérez", "fecha_nacimiento": "15-03-1990", "sexo": "F",
    "peso": "62", "tipo_sangre": "O+", "telefono": "+56 9 1234 5678",
}


class TestFormularioDonante(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = Tk()
        except TclError:
            self.skipTest("No hay pantalla disponible para probar la interfaz")
        self.raiz.withdraw()
        self.carpeta = tempfile.TemporaryDirectory()
        servicio = ServicioDonantes(RepositorioDonantes(os.path.join(self.carpeta.name, "d.txt")))
        self.form = FormularioDonante(self.raiz, servicio)

    def tearDown(self):
        self.raiz.destroy()
        self.carpeta.cleanup()

    def llenar(self, datos):
        for campo, valor in datos.items():
            entrada = self.form.entradas[campo]
            if hasattr(entrada, "set"):
                entrada.set(valor)
            else:
                entrada.insert(0, valor)

    @mock.patch("interfaz.form_donante.messagebox")
    def test_registra_lo_escrito_en_el_formulario(self, _):
        self.llenar(DATOS)
        donante = self.form.registrar()
        self.assertEqual(donante["rut"], "12345678-5")
        self.assertEqual(self.form.leer_datos()["rut"], "")  # se limpia al registrar

    @mock.patch("interfaz.form_donante.messagebox")
    def test_confirmacion_al_registrar(self, mb):
        self.llenar(DATOS)
        self.form.registrar()
        self.assertIn("registrado correctamente", self.form.mensaje.cget("text"))
        mb.showinfo.assert_called_once()

    @mock.patch("interfaz.form_donante.messagebox")
    def test_errores_junto_a_cada_campo(self, _):
        self.llenar({"rut": "12.345.678-9", "peso": "-3"})
        self.assertIsNone(self.form.registrar())
        self.assertIn("verificador", self.form.errores["rut"].cget("text"))
        self.assertIn("positivo", self.form.errores["peso"].cget("text"))
        self.assertEqual(self.form.errores["nombre"].cget("text"), "Campo obligatorio.")
        # Al corregir y volver a intentar, los errores anteriores se borran
        self.form.limpiar()
        self.llenar(DATOS)
        self.form.registrar()
        self.assertEqual(self.form.errores["rut"].cget("text"), "")

    @mock.patch("interfaz.form_donante.messagebox")
    def test_aviso_de_rut_duplicado(self, mb):
        self.llenar(DATOS)
        self.form.registrar()
        self.llenar(DATOS)
        self.assertIsNone(self.form.registrar())
        self.assertIn("ya está registrado", self.form.errores["rut"].cget("text"))
        mb.showwarning.assert_called_once()

    @mock.patch("interfaz.form_donante.messagebox")
    def test_busqueda_muestra_los_datos(self, _):
        self.llenar(DATOS)
        self.form.registrar()
        self.form.rut_busqueda.insert(0, "12345678-5")
        self.assertIsNotNone(self.form.buscar())
        self.assertIn("Ana Pérez", self.form.resultado_busqueda.cget("text"))


if __name__ == "__main__":
    unittest.main()
