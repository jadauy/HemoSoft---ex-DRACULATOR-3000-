"""Registrar una donación: verifica requisitos, genera la unidad con su código y guarda (H3 · T3.5)."""

from datetime import date

from .codigo_barras import fecha_vencimiento, generar_codigo
from .donacion import Donacion, Hemocomponente
from .repositorio_donaciones import RepositorioDonaciones
from .repositorio_evaluaciones import RepositorioEvaluaciones
from .requisitos_donacion import verificar_puede_donar
from .rut import normalizar_rut, validar_rut
from .sedes import buscar_sede
from .servicio import ServicioDonantes
from .validaciones import FORMATO_FECHA, parsear_fecha

VOLUMEN_MINIMO, VOLUMEN_MAXIMO = 400, 500  # ml


class DatosDonacionInvalidosError(Exception):
    def __init__(self, errores):
        super().__init__("Datos de donación inválidos")
        self.errores = errores  # {campo: mensaje}


class DonacionRechazadaError(Exception):
    def __init__(self, motivos):
        super().__init__("Donación rechazada")
        self.motivos = motivos  # lista de textos


def validar_datos_donacion(datos):
    errores = {}
    rut = str(datos.get("rut", "") or "").strip()
    if not rut:
        errores["rut"] = "Campo obligatorio."
    elif validar_rut(rut):
        errores["rut"] = validar_rut(rut)

    sede = str(datos.get("sede", "") or "").strip()
    if not sede:
        errores["sede"] = "Campo obligatorio."
    elif buscar_sede(sede) is None:
        errores["sede"] = "Sede desconocida."

    volumen = str(datos.get("volumen", "") or "").strip()
    if not volumen:
        errores["volumen"] = "Campo obligatorio."
    elif not volumen.isdigit():
        errores["volumen"] = "Debe ser un número entero de ml."
    elif not VOLUMEN_MINIMO <= int(volumen) <= VOLUMEN_MAXIMO:
        errores["volumen"] = f"Debe estar entre {VOLUMEN_MINIMO} y {VOLUMEN_MAXIMO} ml."
    return errores


class ServicioDonaciones:
    def __init__(self, repositorio=None, servicio_donantes=None, repositorio_evaluaciones=None):
        self.repositorio = repositorio or RepositorioDonaciones()
        self.servicio_donantes = servicio_donantes or ServicioDonantes()
        self.repositorio_evaluaciones = repositorio_evaluaciones or RepositorioEvaluaciones()

    def registrar(self, datos, hoy=None):
        """Devuelve (donacion, unidad). Lanza DatosDonacionInvalidosError o DonacionRechazadaError."""
        hoy = hoy or date.today()
        errores = validar_datos_donacion(datos)
        if errores:
            raise DatosDonacionInvalidosError(errores)

        rut = normalizar_rut(datos["rut"])
        donante = self.servicio_donantes.buscar_por_rut(rut)
        if donante is None:
            raise DonacionRechazadaError([f"No hay un donante registrado con RUT {rut}."])

        motivos = verificar_puede_donar(donante, self.repositorio_evaluaciones.ultima_por_rut(rut),
                                        self.repositorio.ultima_donacion(rut), hoy)
        if motivos:
            raise DonacionRechazadaError(motivos)

        sede = buscar_sede(datos["sede"].strip())
        fecha = hoy.strftime(FORMATO_FECHA)
        correlativo = self.repositorio.contar_donaciones(sede.codigo, fecha) + 1
        donacion = Donacion(self.repositorio.siguiente_id_donacion(), rut, fecha, sede.codigo, int(datos["volumen"]))
        unidad = Hemocomponente(generar_codigo(sede.codigo, hoy, correlativo), donacion.idDonacion,
                                Hemocomponente.SANGRE_TOTAL, fecha, fecha_vencimiento(hoy).strftime(FORMATO_FECHA))
        self.repositorio.guardar_donacion(donacion)
        self.repositorio.guardar_unidad(unidad)
        return donacion, unidad

    def buscar_unidad(self, codigo, hoy=None):
        """Trazabilidad (T3.7): unidad, donación, donante y sede a partir del código de barras.

        Devuelve None si no existe. El estado es VIGENTE o VENCIDA según la fecha de hoy.
        """
        hoy = hoy or date.today()
        unidad = self.repositorio.buscar_unidad(codigo)
        if unidad is None:
            return None
        donacion = self.repositorio.buscar_donacion(unidad.idDonacion)
        vence = parsear_fecha(unidad.fecha_vencimiento)
        return {
            "unidad": unidad,
            "donacion": donacion,
            "donante": self.servicio_donantes.buscar_por_rut(donacion.rut_donante),
            "sede": buscar_sede(donacion.codigo_sede),
            "estado": "VIGENTE" if hoy <= vence else "VENCIDA",
            "dias_restantes": (vence - hoy).days,
        }
