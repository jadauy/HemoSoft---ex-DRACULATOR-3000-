from exceptions import RutInvalidoError
from exceptions import DonanteNoEncontradoError
from datetime import date

"""MÉTODO QUE NORMALIZA EL RUT INGRESADO POR EL USUARIO"""
def normalizar_rut(rut_ingresado):
    """Devuelve (cuerpo, dv) o lanza RutInvalidoError."""
    limpio = str(rut_ingresado).replace(".", "").replace("-", "").replace(" ", "").upper()
    if len(limpio) < 2 or not limpio[:-1].isdigit() or limpio[-1] not in "0123456789K":
        raise RutInvalidoError(f"Formato de RUT inválido: {rut_ingresado!r}")
    cuerpo, dv = limpio[:-1], limpio[-1]
    if calcular_dv(cuerpo) != dv:
        raise RutInvalidoError(f"Dígito verificador incorrecto: {rut_ingresado!r}")
    return cuerpo, dv


"""MÉTODO QUE CALCULA EL DIGITO VERIFICADOR DE UN RUT INGRESADO"""
def calcular_dv(cuerpo):
    suma = 0
    factor = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


"""MÉTODO QUE FORMATEA EL RUT INGRESADO POR EL USUARIO"""
def formatear_rut(cuerpo, dv):
    return f"{int(cuerpo):,}".replace(",", ".") + f"-{dv}"


"""MÉTODO AUXILIAR QUE NORMALIZA EL RUT DE UN DONANTE GUARDADO EN LA BASE DE DATOS"""
def _clave_rut(rut):
    """Normaliza un RUT guardado (con o sin formato) para poder compararlo."""
    return str(rut).replace(".", "").replace("-", "").replace(" ", "").upper()


"""
##########################################################################
MÉTODO QUE OBTIENE EL HISTORIAL DE EVALUACIONES Y DONACIONES DE UN DONANTE
##########################################################################
"""
def obtener_historial_donante(rut_ingresado, donantes):
    """
    donantes: colección de objetos Donante (lista, o lo que use la "base de datos").
    """
    cuerpo, dv = normalizar_rut(rut_ingresado)
    rut_normalizado = cuerpo + dv

    donante = next(
        (d for d in donantes if _clave_rut(d.rut) == rut_normalizado), None
    )
    if donante is None:
        raise DonanteNoEncontradoError(f"No existe un donante con RUT {formatear_rut(cuerpo, dv)}")

    hoy = date.today()

    evaluaciones = sorted(donante.evaluaciones, key=lambda e: e.fechaEvaluacion, reverse=True)
    donaciones = sorted(donante.donaciones, key=lambda d: d.fechaExtraccion, reverse=True)

    return {
        "donante": {
            "nombre": donante.nombre,
            "rut": formatear_rut(cuerpo, dv),
            "grupoSanguineo": donante.grupoSanguineo,
            "sexo": donante.sexo,
            "telefono": donante.telefono,
        },
        "evaluaciones": [
            {
                "fecha": e.fechaEvaluacion,
                "resultado": e.resultado,          # APTO / DIFERIDO / NO APTO
                "fechaHabilitacion": e.fechaHabilitacion,
            }
            for e in evaluaciones
        ],
        "donaciones": [
            {
                "fecha": d.fechaExtraccion,
                "sede": d.sede.nombre,
                "volumen": d.volumen,
                "unidades": [
                    {
                        "codigo": h.codigoEtiqueta,
                        "estado": "Vigente" if h.fechaVencimiento >= hoy else "Vencida",
                    }
                    for h in d.hemocomponentes
                ],
            }
            for d in donaciones
        ],
    }

"""MÉTODO AUXILIAR QUE NORMALIZA EL RUT DE UN DONANTE GUARDADO EN LA BASE DE DATOS"""
def _clave_rut(rut):
    """Normaliza un RUT guardado (con o sin formato) para poder compararlo."""
    return str(rut).replace(".", "").replace("-", "").replace(" ", ").upper()