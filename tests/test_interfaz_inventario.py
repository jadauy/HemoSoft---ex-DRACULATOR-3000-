import os
import tempfile
import unittest
from datetime import date, timedelta
from tkinter import TclError, Tk

from donantes.donacion import Donacion, Hemocomponente
from donantes.inventario import Inventario
from donantes.repositorio import RepositorioDonantes
from donantes.repositorio_donaciones import RepositorioDonaciones
from donantes.servicio import ServicioDonantes
from interfaz.inventario import VistaInventario
from donantes.vencimientos import Vencimientos
from donantes.validaciones import TIPOS_SANGRE

HOY = date.today()


class TestVistaInventario(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = Tk()
        except TclError:
            self.skipTest("No hay pantalla disponible para probar la interfaz")
        self.raiz.withdraw()
        self.carpeta = tempfile.TemporaryDirectory()
        ruta = lambda nombre: os.path.join(self.carpeta.name, nombre)
        self.donantes = ServicioDonantes(RepositorioDonantes(ruta("donantes.txt")))
        self.repositorio = RepositorioDonaciones(
            ruta("donaciones.txt"), ruta("unidades.txt")
        )
        self.inventario = Inventario(self.repositorio, self.donantes)
        self.vencimientos = Vencimientos(self.inventario)
        self.vista = VistaInventario(
            self.raiz, self.inventario, self.vencimientos
        )
        self.vista.pack()
        self.donantes.registrar({
            "rut": "12.345.678-5",
            "nombre": "Persona Prueba",
            "fecha_nacimiento": "15-03-1990",
            "sexo": "F",
            "peso": "62",
            "tipo_sangre": "O+",
            "telefono": "912345678",
        })
        self.donantes.registrar({
            "rut": "11.111.111-1",
            "nombre": "Otra Persona",
            "fecha_nacimiento": "15-03-1990",
            "sexo": "M",
            "peso": "70",
            "tipo_sangre": "A+",
            "telefono": "912345679",
        })

    def tearDown(self):
        self.raiz.destroy()
        self.carpeta.cleanup()

    def agregar_unidad(self, numero, sede, fecha_vencimiento, rut="12345678-5"):
        self.repositorio.guardar_donacion(
            Donacion(numero, rut, HOY.strftime("%d-%m-%Y"), sede, 450)
        )
        self.repositorio.guardar_unidad(
            Hemocomponente(
                f"{sede}000000{numero:04d}0",
                numero,
                "Sangre total",
                HOY.strftime("%d-%m-%Y"),
                fecha_vencimiento.strftime("%d-%m-%Y"),
            )
        )

    def test_refresca_stock_alertas_y_listas_de_vencimiento(self):
        self.agregar_unidad(1, "CON", HOY)
        self.agregar_unidad(2, "TAL", HOY)
        self.agregar_unidad(3, "CON", HOY - timedelta(days=1))
        for numero in range(4, 9):
            self.agregar_unidad(
                numero, "CON", HOY + timedelta(days=10), "11111111-1"
            )

        self.vista.actualizar()
        filas = self.vista.tabla_stock.get_children()
        self.assertEqual(
            [self.vista.tabla_stock.item(fila, "values")[0] for fila in filas],
            list(TIPOS_SANGRE),
        )
        fila_o = next(
            fila for fila in filas
            if self.vista.tabla_stock.item(fila, "values")[0] == "O+"
        )
        self.assertEqual(self.vista.tabla_stock.item(fila_o, "values")[1], "2")
        self.assertIn("stock_bajo", self.vista.tabla_stock.item(fila_o, "tags"))
        fila_a = next(
            fila for fila in filas
            if self.vista.tabla_stock.item(fila, "values")[0] == "A+"
        )
        self.assertEqual(self.vista.tabla_stock.item(fila_a, "values")[1], "5")
        self.assertNotIn("stock_bajo", self.vista.tabla_stock.item(fila_a, "tags"))
        self.assertEqual(len(self.vista.tabla_por_vencer.get_children()), 2)
        self.assertEqual(len(self.vista.tabla_vencidas.get_children()), 1)

        self.vista.selector_sede.set("Sede Talcahuano")
        self.vista.selector_sede.event_generate("<<ComboboxSelected>>")
        self.raiz.update_idletasks()
        fila_o = next(
            fila for fila in self.vista.tabla_stock.get_children()
            if self.vista.tabla_stock.item(fila, "values")[0] == "O+"
        )
        self.assertEqual(self.vista.tabla_stock.item(fila_o, "values")[1], "1")

        fecha_nueva = HOY + timedelta(days=1)
        self.agregar_unidad(9, "TAL", fecha_nueva)
        self.vista.actualizar()
        fila_o = next(
            fila for fila in self.vista.tabla_stock.get_children()
            if self.vista.tabla_stock.item(fila, "values")[0] == "O+"
        )
        self.assertEqual(self.vista.tabla_stock.item(fila_o, "values")[1], "2")


if __name__ == "__main__":
    unittest.main()
