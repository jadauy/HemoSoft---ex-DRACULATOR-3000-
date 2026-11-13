"""Evaluación de elegibilidad de un donante antes de aceptar una donación (H2)."""

APTO = "APTO"
DIFERIDO = "DIFERIDO"
NO_APTO = "NO APTO"
RESULTADOS = (APTO, DIFERIDO, NO_APTO)


class EvaluacionElegibilidad:

    # Constructor
    def __init__(self, idEvaluacion, fechaEvaluacion, resultado, fechaHabilitacion,
                 rut_donante="", peso=0.0, hemoglobina=0.0, presion_sistolica=0, presion_diastolica=0,
                 causa_temporal=False, causa_permanente=False, motivos=""):

        # Atributos principales
        self.idEvaluacion = idEvaluacion
        self.fechaEvaluacion = fechaEvaluacion      # texto DD-MM-AAAA
        self.resultado = resultado                  # APTO, DIFERIDO o NO APTO
        self.fechaHabilitacion = fechaHabilitacion  # desde cuándo puede donar ("" si NO APTO)

        # Datos medidos y declarados en la evaluación
        self.rut_donante = rut_donante
        self.peso = peso
        self.hemoglobina = hemoglobina
        self.presion_sistolica = presion_sistolica
        self.presion_diastolica = presion_diastolica
        self.causa_temporal = causa_temporal
        self.causa_permanente = causa_permanente
        self.motivos = motivos                      # motivos del resultado, separados por " | "

        # Relaciones con el resto de las clases (Donacion, Donante, Funcionario)
        self.donacion = None
        self.donante = None
        self.funcionario = None

    # Conversión para guardar en archivo de texto
    COLUMNAS = ("idEvaluacion", "rut_donante", "fechaEvaluacion", "peso", "hemoglobina", "presion_sistolica",
                "presion_diastolica", "causa_temporal", "causa_permanente", "resultado", "fechaHabilitacion",
                "motivos")

    def a_fila(self):
        fila = {c: getattr(self, c) for c in self.COLUMNAS}
        fila["causa_temporal"] = "1" if self.causa_temporal else "0"
        fila["causa_permanente"] = "1" if self.causa_permanente else "0"
        return fila

    @classmethod
    def desde_fila(cls, fila):
        return cls(
            idEvaluacion=int(fila["idEvaluacion"]),
            fechaEvaluacion=fila["fechaEvaluacion"],
            resultado=fila["resultado"],
            fechaHabilitacion=fila["fechaHabilitacion"],
            rut_donante=fila["rut_donante"],
            peso=float(fila["peso"]),
            hemoglobina=float(fila["hemoglobina"]),
            presion_sistolica=int(fila["presion_sistolica"]),
            presion_diastolica=int(fila["presion_diastolica"]),
            causa_temporal=fila["causa_temporal"] == "1",
            causa_permanente=fila["causa_permanente"] == "1",
            motivos=fila["motivos"],
        )
