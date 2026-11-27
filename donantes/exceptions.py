class RutInvalidoError(Exception):
    """El formato o el dígito verificador del RUT no es válido."""

class DonanteNoEncontradoError(Exception):
    """El RUT es válido, pero no existe en la base de datos."""