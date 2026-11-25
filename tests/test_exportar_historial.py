import os
import tempfile
import unittest
from datetime import datetime

from donantes.exportar_historial import guardar_texto, ruta_por_defecto


class TestGuardarHistorial(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.carpeta.cleanup()

    def test_nombre_del_archivo_con_rut_y_fecha(self):
        ruta = ruta_por_defecto("12.345.678-5", datetime(2026, 11, 25, 19, 30))
        self.assertTrue(ruta.endswith(os.path.join("historiales", "historial_12345678-5_20261125_193000.txt")))

    def test_guarda_texto_con_tildes_y_crea_la_carpeta(self):
        ruta = os.path.join(self.carpeta.name, "historiales", "h.txt")
        self.assertEqual(guardar_texto("Ana Pérez · Sede Concepción\n", ruta), ruta)
        with open(ruta, encoding="utf-8") as archivo:
            self.assertEqual(archivo.read(), "Ana Pérez · Sede Concepción\n")


if __name__ == "__main__":
    unittest.main()
