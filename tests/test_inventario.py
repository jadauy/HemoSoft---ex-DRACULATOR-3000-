import os
import tempfile
import unittest
from datetime import date

from donantes.donacion import Donacion, Hemocomponente
from donantes.inventario import Inventario
from donantes.repositorio import RepositorioDonantes
from donantes.repositorio_donaciones import RepositorioDonaciones
from donantes.servicio import ServicioDonantes
from donantes.validaciones import TIPOS_SANGRE

HOY = date(2026, 11, 22)


class TestInventario(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        ruta = lambda n: os.path.join(self.carpeta.name, n)
        self.donantes = ServicioDonantes(RepositorioDonantes(ruta("d.txt")))
        self.repo = RepositorioDonaciones(ruta("don.txt"), ruta("u.txt"))
        self.inventario = Inventario(self.repo, self.donantes)
        self.siguiente = 1

    def tearDown(self):
        self.carpeta.cleanup()

    def donante(self, rut, tipo_sangre):
        self.donantes.registrar({"rut": rut, "nombre": "Persona Prueba", "fecha_nacimiento": "15-03-1990",
                                 "sexo": "F", "peso": "62", "tipo_sangre": tipo_sangre, "telefono": "912345678"})

    def unidad(self, rut, vence, sede="CON"):
        n = self.siguiente
        self.siguiente += 1
        self.repo.guardar_donacion(Donacion(n, rut, "01-11-2026", sede, 450))
        self.repo.guardar_unidad(Hemocomponente(f"CON2611010{n:03d}0", n, "Sangre total", "01-11-2026", vence))

    def test_sin_unidades_muestra_los_8_grupos_en_cero(self):
        stock = self.inventario.stock_por_grupo(HOY)
        self.assertEqual(list(stock), list(TIPOS_SANGRE))
        self.assertTrue(all(v == 0 for v in stock.values()))

    def test_cuenta_unidades_vigentes_por_grupo_del_donante(self):
        self.donante("12.345.678-5", "O+")
        self.donante("11.111.111-1", "A-")
        self.unidad("12345678-5", "13-12-2026")
        self.unidad("12345678-5", "20-12-2026")
        self.unidad("11111111-1", "10-12-2026")
        stock = self.inventario.stock_por_grupo(HOY)
        self.assertEqual((stock["O+"], stock["A-"], stock["AB+"]), (2, 1, 0))
        self.assertEqual(self.inventario.total_vigente(HOY), 3)

    def test_las_vencidas_no_cuentan_y_el_dia_de_vencimiento_si(self):
        self.donante("12.345.678-5", "B+")
        self.unidad("12345678-5", "21-11-2026")  # venció ayer
        self.unidad("12345678-5", "22-11-2026")  # vence hoy: todavía vigente
        self.assertEqual(self.inventario.stock_por_grupo(HOY)["B+"], 1)

    def test_unidad_sin_donante_no_se_asigna_a_ningun_grupo(self):
        self.unidad("10000013-K", "13-12-2026")  # donante no registrado
        unidades = self.inventario.unidades()
        self.assertIsNone(unidades[0].tipo_sangre)
        self.assertEqual(self.inventario.total_vigente(HOY), 0)


if __name__ == "__main__":
    unittest.main()
