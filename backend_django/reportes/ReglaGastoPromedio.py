from decimal import Decimal

from .Observacion import Observacion
from .ReglaAnalisis import ReglaAnalisis

CENTAVOS = Decimal("0.01")


class ReglaGastoPromedio(ReglaAnalisis):
    def evaluar(self, reporte, categorias, meses):
        if not any(mes.gastos > 0 for mes in meses):
            return []
        promedio = (reporte.total_gastos / len(meses)).quantize(CENTAVOS)
        return [
            Observacion(
                "informacion",
                "Gasto promedio mensual",
                f"Calculado sobre {len(meses)} mes(es) con movimientos.",
                promedio,
            )
        ]
