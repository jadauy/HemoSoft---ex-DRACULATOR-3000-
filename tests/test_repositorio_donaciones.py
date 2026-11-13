import os
import tempfile
import unittest

from donantes.donacion import Donacion, Hemocomponente
from donantes.repositorio_donaciones import RepositorioDonaciones


class TestRepositorioDonaciones(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.repo = RepositorioDonaciones(os.path.join(self.carpeta.name, "donaciones.txt"),
                                          os.path.join(self.carpeta.name, "unidades.txt"))

    def tearDown(self):
        self.carpeta.cleanup()

    def test_guarda_donacion_y_su_unidad(self):
        self.repo.guardar_donacion(Donacion(1, "12345678-5", "11-11-2026", "CON", 450))
        self.repo.guardar_unidad(Hemocomponente("CON26111100011", 1, "Sangre total", "11-11-2026", "23-12-2026"))
        self.assertEqual(self.repo.buscar_donacion(1).volumen_ml, 450)
        unidad = self.repo.buscar_unidad("con26111100011")  # sin importar mayúsculas
        self.assertEqual(unidad.idDonacion, 1)
        self.assertEqual(len(self.repo.unidades_de_donacion(1)), 1)

    def test_ultima_donacion_por_fecha(self):
        self.repo.guardar_donacion(Donacion(1, "12345678-5", "01-03-2026", "CON", 450))
        self.repo.guardar_donacion(Donacion(2, "12345678-5", "05-08-2026", "TAL", 450))
        self.repo.guardar_donacion(Donacion(3, "11111111-1", "10-11-2026", "CON", 450))
        self.assertEqual(self.repo.ultima_donacion("12345678-5").idDonacion, 2)
        self.assertIsNone(self.repo.ultima_donacion("10000013-K"))

    def test_ids_y_conteo_por_sede_y_dia(self):
        self.assertEqual(self.repo.siguiente_id_donacion(), 1)
        self.repo.guardar_donacion(Donacion(1, "12345678-5", "11-11-2026", "CON", 450))
        self.repo.guardar_donacion(Donacion(2, "11111111-1", "11-11-2026", "CON", 450))
        self.repo.guardar_donacion(Donacion(3, "10000013-K", "11-11-2026", "TAL", 450))
        self.assertEqual(self.repo.siguiente_id_donacion(), 4)
        self.assertEqual(self.repo.contar_donaciones("CON", "11-11-2026"), 2)
        self.assertIsNone(self.repo.buscar_unidad("NOEXISTE"))


if __name__ == "__main__":
    unittest.main()
