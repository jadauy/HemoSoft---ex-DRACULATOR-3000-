import unittest

from donantes.alertas_stock import UMBRAL_STOCK_BAJO, obtener_alertas_stock_bajo
from donantes.validaciones import TIPOS_SANGRE


def stock_con():
    """Stock de prueba: los 8 grupos con 10 unidades."""
    stock = {grupo: 10 for grupo in TIPOS_SANGRE}
    return stock


class TestAlertasStockBajo(unittest.TestCase):
    def test_umbral_por_defecto_es_5(self):
        self.assertEqual(UMBRAL_STOCK_BAJO, 5)

    def test_4_unidades_con_umbral_5_activa_la_alerta(self):
        alertas = obtener_alertas_stock_bajo({**stock_con(), "O+": 4})
        self.assertTrue(alertas["O+"])

    def test_5_unidades_con_umbral_5_no_activa_la_alerta(self):
        alertas = obtener_alertas_stock_bajo({**stock_con(), "O+": 5})
        self.assertFalse(alertas["O+"])

    def test_grupo_sin_unidades_activa_la_alerta(self):
        alertas = obtener_alertas_stock_bajo({**stock_con(), "AB-": 0})
        self.assertTrue(alertas["AB-"])

    def test_umbral_personalizado_3_no_alerta_con_4_unidades(self):
        alertas = obtener_alertas_stock_bajo({**stock_con(), "A+": 4}, umbral=3)
        self.assertFalse(alertas["A+"])

    def test_umbral_personalizado_alerta_bajo_ese_valor(self):
        alertas = obtener_alertas_stock_bajo({**stock_con(), "A+": 2, "B+": 3}, umbral=3)
        self.assertTrue(alertas["A+"])
        self.assertFalse(alertas["B+"])

    def test_evalua_los_8_grupos_y_conserva_su_orden(self):
        stock = {grupo: i for i, grupo in enumerate(TIPOS_SANGRE)}  # 0..7
        alertas = obtener_alertas_stock_bajo(stock)
        self.assertEqual(list(alertas), list(TIPOS_SANGRE))
        self.assertEqual(list(alertas.values()), [True] * 5 + [False] * 3)

    def test_no_modifica_el_stock_recibido(self):
        stock = {**stock_con(), "O-": 1}
        copia = dict(stock)
        obtener_alertas_stock_bajo(stock)
        self.assertEqual(stock, copia)


if __name__ == "__main__":
    unittest.main()
