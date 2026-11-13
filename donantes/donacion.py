"""Modelos de donación, unidad extraída (hemocomponente) y sede (H3 · T3.1)."""


class Sede:
    """Lugar donde se realiza la extracción."""

    def __init__(self, codigo, nombre, ciudad):
        self.codigo = codigo    # 3 letras, forma parte del código de barras
        self.nombre = nombre
        self.ciudad = ciudad

    def __repr__(self):
        return f"Sede({self.codigo}, {self.nombre})"


class Donacion:
    """Una extracción hecha a un donante en una sede y fecha."""

    COLUMNAS = ("idDonacion", "rut_donante", "fecha", "codigo_sede", "volumen_ml")

    def __init__(self, idDonacion, rut_donante, fecha, codigo_sede, volumen_ml):
        self.idDonacion = idDonacion
        self.rut_donante = rut_donante
        self.fecha = fecha              # texto DD-MM-AAAA
        self.codigo_sede = codigo_sede
        self.volumen_ml = volumen_ml

        # Relaciones con el resto de las clases
        self.donante = None
        self.sede = None
        self.unidades = []

    def a_fila(self):
        return {c: getattr(self, c) for c in self.COLUMNAS}

    @classmethod
    def desde_fila(cls, fila):
        return cls(int(fila["idDonacion"]), fila["rut_donante"], fila["fecha"], fila["codigo_sede"],
                   int(fila["volumen_ml"]))


class Hemocomponente:
    """Unidad extraída en una donación. Se identifica con un código de barras único."""

    SANGRE_TOTAL = "Sangre total"
    COLUMNAS = ("codigo_barras", "idDonacion", "tipo", "fecha_extraccion", "fecha_vencimiento")

    def __init__(self, codigo_barras, idDonacion, tipo, fecha_extraccion, fecha_vencimiento):
        self.codigo_barras = codigo_barras
        self.idDonacion = idDonacion
        self.tipo = tipo
        self.fecha_extraccion = fecha_extraccion    # texto DD-MM-AAAA
        self.fecha_vencimiento = fecha_vencimiento  # texto DD-MM-AAAA

        # Relación con la donación de origen
        self.donacion = None

    def a_fila(self):
        return {c: getattr(self, c) for c in self.COLUMNAS}

    @classmethod
    def desde_fila(cls, fila):
        return cls(fila["codigo_barras"], int(fila["idDonacion"]), fila["tipo"], fila["fecha_extraccion"],
                   fila["fecha_vencimiento"])
