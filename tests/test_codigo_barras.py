import unittest
from datetime import date

from donantes.codigo_barras import (CODE39, barras_code39, codigo_valido, fecha_vencimiento, generar_codigo)


class TestCodigoBarras(unittest.TestCase):
    def test_formato_del_codigo(self):
        codigo = generar_codigo("con", date(2026, 11, 11), 1)
        self.assertTrue(codigo.startswith("CON2611110001"))
        self.assertEqual(len(codigo), 14)
        self.assertTrue(codigo_valido(codigo))

    def test_codigos_distintos_no_se_repiten(self):
        codigos = {generar_codigo(sede, date(2026, 11, d), n)
                   for sede in ("CON", "TAL") for d in (11, 12) for n in range(1, 51)}
        self.assertEqual(len(codigos), 2 * 2 * 50)

    def test_digito_verificador_detecta_errores_de_digitacion(self):
        codigo = generar_codigo("CON", date(2026, 11, 11), 7)
        alterado = codigo[:-2] + str((int(codigo[-2]) + 1) % 10) + codigo[-1]
        self.assertFalse(codigo_valido(alterado))
        self.assertFalse(codigo_valido("CON123"))

    def test_vencimiento_a_42_dias(self):
        self.assertEqual(fecha_vencimiento(date(2026, 11, 11)), date(2026, 12, 23))

    def test_tabla_code39(self):
        for caracter, patron in CODE39.items():
            self.assertEqual(len(patron), 9, caracter)
            self.assertEqual(patron.count("w"), 3, caracter)

    def test_barras_empiezan_y_terminan_en_barra(self):
        elementos = barras_code39("CON26111100017")
        self.assertTrue(elementos[0][1] and elementos[-1][1])
        self.assertEqual(len(elementos), 16 * 10 - 1)  # 14 caracteres + 2 asteriscos


if __name__ == "__main__":
    unittest.main()
