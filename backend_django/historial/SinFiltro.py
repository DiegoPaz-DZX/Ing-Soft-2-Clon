from .FiltroMovimiento import FiltroMovimiento


class SinFiltro(FiltroMovimiento):
    def cumple(self, movimiento):
        return True
