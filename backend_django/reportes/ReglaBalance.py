from .Observacion import Observacion
from .ReglaAnalisis import ReglaAnalisis


class ReglaBalance(ReglaAnalisis):
    def evaluar(self, reporte, categorias, meses):
        if reporte.balance < 0:
            return [
                Observacion(
                    "advertencia",
                    "Gastaste más de lo que ingresó",
                    "Tus gastos superaron a tus ingresos en el periodo.",
                    -reporte.balance,
                )
            ]
        return [
            Observacion(
                "positivo",
                "Balance positivo",
                f"Conservaste el {reporte.tasa_ahorro}% de tus ingresos del periodo.",
                reporte.balance,
            )
        ]
