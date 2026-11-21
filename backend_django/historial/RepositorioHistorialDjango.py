from balance.Movimiento import Movimiento

from .RepositorioHistorial import RepositorioHistorial


class RepositorioHistorialDjango(RepositorioHistorial):
    def listar_movimientos(self, cuenta):
        return list(
            Movimiento.objects.filter(usuario = cuenta).order_by("-fecha", "-id"))
