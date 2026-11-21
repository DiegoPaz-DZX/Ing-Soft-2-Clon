from .ReglaBalance import ReglaBalance
from .ReglaGastoPromedio import ReglaGastoPromedio
from .ReglaMayorGasto import ReglaMayorGasto
from .ReglaMesMayorGasto import ReglaMesMayorGasto


class FabricaReglasAnalisis:
    @staticmethod
    def crear_todas():
        return [ReglaBalance(), ReglaMayorGasto(), ReglaGastoPromedio(), ReglaMesMayorGasto()]
