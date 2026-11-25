import os
import tempfile
import unittest
from datetime import datetime

from donantes.exportar_historial import SIN_REGISTROS, exportar_historial, formatear_historial

GENERADO = datetime(2026, 11, 25, 19, 30)


def historial_ejemplo(**cambios):
    historial = {
        "donante": {"rut": "12345678-5", "nombre": "Ana Pérez", "fecha_nacimiento": "15-03-1990", "sexo": "F",
                    "tipo_sangre": "O+", "telefono": "+56912345678"},
        "evaluaciones": [
            {"fecha": "20-11-2026", "resultado": "APTO", "motivos": "", "fecha_habilitacion": "20-11-2026"},
            {"fecha": "02-10-2026", "resultado": "DIFERIDO",
             "motivos": "Peso bajo 50 kg (48 kg). | Hemoglobina bajo 12.5 g/dL (11.9).",
             "fecha_habilitacion": "01-11-2026"},
        ],
        "donaciones": [
            {"fecha": "20-11-2026", "sede": "Sede Concepción", "volumen_ml": 450, "codigo_unidad": "CON26112000013",
             "estado": "VIGENTE"},
        ],
    }
    historial.update(cambios)
    return historial


class TestFormatearHistorial(unittest.TestCase):
    def test_incluye_datos_evaluaciones_y_donaciones(self):
        texto = formatear_historial(historial_ejemplo(), GENERADO)
        for esperado in ("Ana Pérez", "12345678-5", "O+", "Generado el 25-11-2026 a las 19:30",
                         "Evaluaciones de elegibilidad (2)", "Donaciones (1)", "CON26112000013", "[VIGENTE]"):
            self.assertIn(esperado, texto)

    def test_motivos_y_fecha_de_habilitacion_de_un_diferido(self):
        texto = formatear_historial(historial_ejemplo(), GENERADO)
        self.assertIn("DIFERIDO  (puede volver desde el 01-11-2026)", texto)
        self.assertIn("    - Peso bajo 50 kg (48 kg).", texto)
        self.assertIn("    - Hemoglobina bajo 12.5 g/dL (11.9).", texto)
        self.assertNotIn("APTO  (puede volver", texto)  # un APTO no muestra fecha de habilitación

    def test_respeta_el_orden_recibido(self):
        texto = formatear_historial(historial_ejemplo(), GENERADO)
        self.assertLess(texto.index("20-11-2026  APTO"), texto.index("02-10-2026  DIFERIDO"))

    def test_sin_evaluaciones_ni_donaciones(self):
        texto = formatear_historial(historial_ejemplo(evaluaciones=[], donaciones=[]), GENERADO)
        self.assertEqual(texto.count(SIN_REGISTROS), 2)
        self.assertIn("Evaluaciones de elegibilidad (0)", texto)

    def test_estado_actual_es_opcional(self):
        self.assertNotIn("Estado actual", formatear_historial(historial_ejemplo(), GENERADO))
        texto = formatear_historial(historial_ejemplo(estado_actual="Puede donar hoy"), GENERADO)
        self.assertIn("Estado actual:       Puede donar hoy", texto)


class TestExportarHistorial(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.carpeta.cleanup()

    def test_guarda_el_archivo_en_la_ruta_indicada(self):
        ruta = os.path.join(self.carpeta.name, "sub", "historial.txt")
        self.assertEqual(exportar_historial(historial_ejemplo(), ruta, GENERADO), ruta)
        with open(ruta, encoding="utf-8") as archivo:
            self.assertEqual(archivo.read(), formatear_historial(historial_ejemplo(), GENERADO))

    def test_nombre_por_defecto_con_rut_y_fecha(self):
        from donantes import exportar_historial as modulo
        original = modulo.ruta_datos
        modulo.ruta_datos = lambda nombre: os.path.join(self.carpeta.name, nombre)
        try:
            ruta = exportar_historial(historial_ejemplo(), generado=GENERADO)
        finally:
            modulo.ruta_datos = original
        self.assertTrue(ruta.endswith(os.path.join("historiales", "historial_12345678-5_20261125_193000.txt")))
        self.assertTrue(os.path.exists(ruta))


if __name__ == "__main__":
    unittest.main()
