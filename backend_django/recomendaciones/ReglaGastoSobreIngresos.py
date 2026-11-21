from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion


class ReglaGastoSobreIngresos(ReglaRecomendacion):
    def evaluar(self, resumen):
        if resumen.ingresos <= 0 or resumen.gastos <= 0 or resumen.gastos > resumen.ingresos:
            return []  # el déficit lo cubre ReglaDeficit
        porcentaje = resumen.gastos / resumen.ingresos
        dato = f"{porcentaje * 100:.0f}%"
        return [
            Recomendacion(
                id="gasto-sobre-ingresos",
                nivel="informacion",
                titulo="Cuánto de tus ingresos gastas",
                mensaje=f"Este mes gastaste el {dato} de tus ingresos. Lo ideal es dejar un margen para ahorrar.",
                dato=dato,
            )
        ]