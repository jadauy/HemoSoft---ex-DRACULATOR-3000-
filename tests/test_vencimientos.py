import os
import tempfile
import unittest
from datetime import date

from donantes.donacion import Donacion, Hemocomponente
from donantes.inventario import Inventario
from donantes.repositorio import RepositorioDonantes
from donantes.repositorio_donaciones import RepositorioDonaciones
from donantes.servicio import ServicioDonantes
from donantes.vencimientos import Vencimientos

HOY = date(2026, 11, 22)


class TestVencimientos(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        ruta = lambda nombre: os.path.join(self.carpeta.name, nombre)
        donantes = ServicioDonantes(RepositorioDonantes(ruta("donantes.txt")))
        repositorio = RepositorioDonaciones(ruta("donaciones.txt"), ruta("unidades.txt"))
        self.inventario = Inventario(repositorio, donantes)
        self.vencimientos = Vencimientos(self.inventario)
        self.repositorio = repositorio
        donantes.registrar({
            "rut": "12.345.678-5",
            "nombre": "Persona Prueba",
            "fecha_nacimiento": "15-03-1990",
            "sexo": "F",
            "peso": "62",
            "tipo_sangre": "O+",
            "telefono": "912345678",
        })

    def tearDown(self):
        self.carpeta.cleanup()

    def agregar_unidad(self, numero, sede, vencimiento):
        self.repositorio.guardar_donacion(
            Donacion(numero, "12345678-5", "01-11-2026", sede, 450)
        )
        self.repositorio.guardar_unidad(
            Hemocomponente(
                f"{sede}261101{numero:04d}0",
                numero,
                "Sangre total",
                "01-11-2026",
                vencimiento,
            )
        )

    def test_por_vencer_ordenadas_y_vencidas_separadas_del_stock(self):
        self.agregar_unidad(1, "CON", "25-11-2026")
        self.agregar_unidad(2, "CON", "23-11-2026")
        self.agregar_unidad(3, "CON", "29-11-2026")
        self.agregar_unidad(4, "CON", "21-11-2026")

        por_vencer = self.vencimientos.unidades_por_vencer(HOY)
        vencidas = self.vencimientos.unidades_vencidas(HOY)

        self.assertEqual(
            [u.unidad.fecha_vencimiento for u in por_vencer],
            ["23-11-2026", "25-11-2026"],
        )
        self.assertEqual([u.unidad.fecha_vencimiento for u in vencidas], ["21-11-2026"])
        self.assertEqual(self.inventario.stock_por_grupo(HOY)["O+"], 3)

    def test_consultas_de_vencimiento_respetan_el_filtro_de_sede(self):
        self.agregar_unidad(1, "CON", "24-11-2026")
        self.agregar_unidad(2, "TAL", "23-11-2026")

        unidades = self.vencimientos.unidades_por_vencer(HOY, "CON")

        self.assertEqual(len(unidades), 1)
        self.assertEqual(unidades[0].donacion.codigo_sede, "CON")


if __name__ == "__main__":
    unittest.main()
