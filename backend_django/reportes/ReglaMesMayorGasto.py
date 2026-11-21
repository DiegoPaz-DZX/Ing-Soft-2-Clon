from .Observacion import Observacion
from .ReglaAnalisis import ReglaAnalisis


class ReglaMesMayorGasto(ReglaAnalisis):
    def evaluar(self, reporte, categorias, meses):
        meses_con_gasto = [mes for mes in meses if mes.gastos > 0]
        if len(meses_con_gasto) < 2:
            return []
        mayor = max(meses_con_gasto, key=lambda mes: mes.gastos)
        return [
            Observacion(
                "informacion",
                f"Mes con más gastos: {mayor.etiqueta}",
                "Revisa qué movimientos elevaron el gasto ese mes.",
                mayor.gastos,
            )
        ]
