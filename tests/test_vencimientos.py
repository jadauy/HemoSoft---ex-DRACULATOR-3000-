import unittest
from datetime import date
from donantes.donacion import Hemocomponente
from donantes.validaciones import FORMATO_FECHA, parsear_fecha
from donantes.vencimientos import calcular_vencimientos, ordenar_por_vencer

class TestVencimientos(unittest.TestCase):
    def setUp(self):
        self.hoy = date(2026, 11, 20)  # Fecha de referencia para las pruebas
        self.unidades = [
            # Unidad vencida
            Hemocomponente("CON26111100010", 1, Hemocomponente.SANGRE_TOTAL, "10-11-2026", "20-11-2026"),
            # Unidades que vencen en 5, 1 y 7 días respectivamente
            Hemocomponente("CON26111100011", 2, Hemocomponente.SANGRE_TOTAL, "10-11-2026", "25-11-2026"),
            Hemocomponente("CON26111100012", 3, Hemocomponente.SANGRE_TOTAL, "10-11-2026", "21-11-2026"),
            Hemocomponente("CON26111100013", 4, Hemocomponente.SANGRE_TOTAL, "10-11-2026", "27-11-2026"),
            # Unidad que vence en 8 días
            Hemocomponente("CON26111100014", 5, Hemocomponente.SANGRE_TOTAL, "10-11-2026", "28-11-2026"),
            # Unidad vencida ayer
            Hemocomponente("CON26111100015", 6, Hemocomponente.SANGRE_TOTAL, "10-11-2026", "19-11-2026"),
        ]
        self.unidades_vencidas, self.unidades_por_vencer = calcular_vencimientos(self.unidades, hoy = self.hoy)

    # Test que verifica una unidad vencida se encuentra en la lista de unidades vencidas
    def test_vence_hoy(self):
        self.assertIn(self.unidades[0], self.unidades_vencidas)
        self.assertNotIn(self.unidades[0], self.unidades_por_vencer)

    # Caso borde: unidad que va a vencer en 7 días
    def test_por_vencer_7_dias(self):
        self.assertIn(self.unidades[3], self.unidades_por_vencer)
        self.assertNotIn(self.unidades[3], self.unidades_vencidas)

    # Caso borde: unidad que vence en 8 días
    def test_por_vencer_8_dias(self):
        self.assertNotIn(self.unidades[4], self.unidades_por_vencer)
        self.assertNotIn(self.unidades[4], self.unidades_vencidas)

    # Verifica que las unidades por vencer estén ordenadas por fecha de vencimiento
    def test_orden_por_vencer(self):
        unidades_ordenadas = ordenar_por_vencer(self.unidades_por_vencer)
        fechas_ordenadas = [u.fecha_vencimiento for u in unidades_ordenadas]

        # Ahora se ocupa parsear_fecha para ordenar las fechas esperadas y compararlas con las fechas ordenadas
        fechas_esperadas = sorted(fechas_ordenadas, key = lambda f: parsear_fecha(f))
        self.assertEqual(fechas_ordenadas, fechas_esperadas)

    # Se verifica una unidad que venció ayer se encuentra en la lista de unidades vencidas
    def test_vencida_ayer(self):
        self.assertIn(self.unidades[5], self.unidades_vencidas)
        self.assertNotIn(self.unidades[5], self.unidades_por_vencer)

if __name__ == "__main__":
    unittest.main()