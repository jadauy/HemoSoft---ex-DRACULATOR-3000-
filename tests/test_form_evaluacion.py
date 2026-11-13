import os
import tempfile
import unittest
from tkinter import TclError, Tk
from unittest import mock

from donantes.repositorio import RepositorioDonantes
from donantes.repositorio_evaluaciones import RepositorioEvaluaciones
from donantes.servicio import ServicioDonantes
from donantes.servicio_evaluaciones import ServicioEvaluaciones
from interfaz.form_evaluacion import FormularioEvaluacion


class TestFormularioEvaluacion(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = Tk()
        except TclError:
            self.skipTest("No hay pantalla disponible para probar la interfaz")
        self.raiz.withdraw()
        self.carpeta = tempfile.TemporaryDirectory()
        donantes = ServicioDonantes(RepositorioDonantes(os.path.join(self.carpeta.name, "d.txt")))
        donantes.registrar({"rut": "12.345.678-5", "nombre": "Ana Pérez", "fecha_nacimiento": "15-03-1990",
                            "sexo": "F", "peso": "62", "tipo_sangre": "O+", "telefono": "912345678"})
        servicio = ServicioEvaluaciones(RepositorioEvaluaciones(os.path.join(self.carpeta.name, "e.txt")), donantes)
        self.form = FormularioEvaluacion(self.raiz, servicio)

    def tearDown(self):
        self.raiz.destroy()
        self.carpeta.cleanup()

    def llenar(self, **datos):
        for campo, valor in datos.items():
            self.form.entradas[campo].insert(0, valor)

    def test_muestra_apto(self):
        self.llenar(rut="12.345.678-5", peso="62", hemoglobina="13", presion_sistolica="120", presion_diastolica="80")
        self.assertEqual(self.form.evaluar().resultado, "APTO")
        self.assertEqual(self.form.resultado.cget("text"), "APTO")
        self.assertIn("Puede donar hoy", self.form.detalle.cget("text"))

    def test_muestra_diferido_con_motivos(self):
        self.llenar(rut="12.345.678-5", peso="45", hemoglobina="13", presion_sistolica="120", presion_diastolica="80")
        self.form.causa_temporal.set(True)
        self.form.evaluar()
        self.assertEqual(self.form.resultado.cget("text"), "DIFERIDO")
        self.assertIn("Peso", self.form.detalle.cget("text"))

    @mock.patch("interfaz.form_evaluacion.messagebox")
    def test_errores_y_donante_no_registrado(self, mb):
        self.llenar(rut="12.345.678-9")
        self.assertIsNone(self.form.evaluar())
        self.assertIn("verificador", self.form.errores["rut"].cget("text"))
        self.form.limpiar()
        self.llenar(rut="11.111.111-1", peso="62", hemoglobina="13", presion_sistolica="120", presion_diastolica="80")
        self.assertIsNone(self.form.evaluar())
        mb.showwarning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
