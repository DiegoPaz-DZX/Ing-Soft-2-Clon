from .FiltroMovimiento import FiltroMovimiento
from .RangoFechasInvalidoException import RangoFechasInvalidoException


class FiltroPorRangoFechas(FiltroMovimiento):
    def __init__(self, desde, hasta):
        if desde is None or hasta is None:
            raise RangoFechasInvalidoException("Debe ingresar la fecha de inicio y la fecha de fin.")
        if desde > hasta:
            raise RangoFechasInvalidoException(
                "La fecha de inicio no puede ser posterior a la fecha de fin."
            )
        self._desde = desde
        self._hasta = hasta

    def cumple(self, movimiento):
        return self._desde <= movimiento.fecha <= self._hasta
