from .SinFiltro import SinFiltro


class HistorialMovimientos:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def obtener_movimientos(self, cuenta, filtro=None):
        filtro = filtro or SinFiltro()
        return [m for m in self._repositorio.listar_movimientos(cuenta) if filtro.cumple(m)]
