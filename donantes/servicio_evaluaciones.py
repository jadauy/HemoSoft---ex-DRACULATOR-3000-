"""Registrar una evaluación de elegibilidad: valida, calcula el resultado y la guarda (H2 · T2.3)."""

from datetime import date

from .elegibilidad import calcular_resultado
from .EvaluacionElegibilidad import EvaluacionElegibilidad
from .repositorio_evaluaciones import RepositorioEvaluaciones
from .rut import normalizar_rut, validar_rut
from .servicio import ServicioDonantes
from .validaciones import FORMATO_FECHA, parsear_fecha

CAMPOS = ("rut", "peso", "hemoglobina", "presion_sistolica", "presion_diastolica")


class DatosEvaluacionInvalidosError(Exception):
    def __init__(self, errores):
        super().__init__("Datos de evaluación inválidos")
        self.errores = errores  # {campo: mensaje}


class DonanteNoRegistradoError(Exception):
    pass


def _numero(texto):
    return float(str(texto).strip().replace(",", "."))


def validar_datos_evaluacion(datos):
    errores = {}
    for campo in CAMPOS:
        valor = str(datos.get(campo, "") or "").strip()
        if not valor:
            errores[campo] = "Campo obligatorio."
            continue
        if campo == "rut":
            error = validar_rut(valor)
            if error:
                errores[campo] = error
            continue
        try:
            numero = _numero(valor)
        except ValueError:
            errores[campo] = "Debe ser un número."
            continue
        if numero <= 0:
            errores[campo] = "Debe ser un número positivo."
        elif campo.startswith("presion") and numero != int(numero):
            errores[campo] = "Debe ser un número entero."
    return errores


class ServicioEvaluaciones:
    def __init__(self, repositorio=None, servicio_donantes=None):
        self.repositorio = repositorio or RepositorioEvaluaciones()
        self.servicio_donantes = servicio_donantes or ServicioDonantes()

    def evaluar(self, datos, hoy=None):
        """Valida los datos, calcula el resultado, guarda la evaluación y la devuelve."""
        hoy = hoy or date.today()
        errores = validar_datos_evaluacion(datos)
        if errores:
            raise DatosEvaluacionInvalidosError(errores)

        rut = normalizar_rut(datos["rut"])
        donante = self.servicio_donantes.buscar_por_rut(rut)
        if donante is None:
            raise DonanteNoRegistradoError(f"No hay un donante registrado con RUT {rut}.")

        peso, hemoglobina = _numero(datos["peso"]), _numero(datos["hemoglobina"])
        sistolica, diastolica = int(_numero(datos["presion_sistolica"])), int(_numero(datos["presion_diastolica"]))
        temporal, permanente = bool(datos.get("causa_temporal")), bool(datos.get("causa_permanente"))

        resultado, motivos, habilitacion = calcular_resultado(
            donante["sexo"], parsear_fecha(donante["fecha_nacimiento"]), hoy, peso, hemoglobina,
            sistolica, diastolica, temporal, permanente)

        evaluacion = EvaluacionElegibilidad(
            self.repositorio.siguiente_id(), hoy.strftime(FORMATO_FECHA), resultado,
            habilitacion.strftime(FORMATO_FECHA) if habilitacion else "",
            rut_donante=rut, peso=peso, hemoglobina=hemoglobina, presion_sistolica=sistolica,
            presion_diastolica=diastolica, causa_temporal=temporal, causa_permanente=permanente,
            motivos=" | ".join(motivos))
        self.repositorio.guardar(evaluacion)
        return evaluacion

    def historial(self, rut):
        if validar_rut(rut):
            return []
        return self.repositorio.por_rut(normalizar_rut(rut))
