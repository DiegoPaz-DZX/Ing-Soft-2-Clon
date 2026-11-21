from .Observacion import Observacion
from .ReglaAnalisis import ReglaAnalisis


class ReglaMayorGasto(ReglaAnalisis):
    def evaluar(self, reporte, categorias, meses):
        if not categorias:
            return []
        principal = categorias[0]
        return [
            Observacion(
                "informacion",
                f"Mayor gasto: {principal.nombre}",
                f"Representa el {principal.porcentaje}% de tus gastos del periodo.",
                principal.monto,
            )
        ]
