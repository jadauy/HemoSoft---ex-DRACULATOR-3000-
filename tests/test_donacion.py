import unittest

from donantes.donacion import Donacion, Hemocomponente
from donantes.sedes import SEDES, buscar_sede, sede_por_nombre


class TestModelosDonacion(unittest.TestCase):
    def test_donacion_ida_y_vuelta_como_fila(self):
        d = Donacion(7, "12345678-5", "11-11-2026", "CON", 450)
        copia = Donacion.desde_fila({k: str(v) for k, v in d.a_fila().items()})
        self.assertEqual(copia.a_fila(), d.a_fila())

    def test_hemocomponente_ida_y_vuelta_como_fila(self):
        u = Hemocomponente("CON26111100011", 7, Hemocomponente.SANGRE_TOTAL, "11-11-2026", "23-12-2026")
        copia = Hemocomponente.desde_fila({k: str(v) for k, v in u.a_fila().items()})
        self.assertEqual(copia.a_fila(), u.a_fila())


class TestSedes(unittest.TestCase):
    def test_codigos_unicos_de_tres_letras(self):
        codigos = [s.codigo for s in SEDES]
        self.assertEqual(len(codigos), len(set(codigos)))
        self.assertTrue(all(len(c) == 3 and c.isalpha() and c.isupper() for c in codigos))

    def test_busquedas(self):
        self.assertEqual(buscar_sede("CON").nombre, "Sede Concepción")
        self.assertEqual(sede_por_nombre("Sede Chillán").codigo, "CHI")
        self.assertIsNone(buscar_sede("XXX"))


if __name__ == "__main__":
    unittest.main()
