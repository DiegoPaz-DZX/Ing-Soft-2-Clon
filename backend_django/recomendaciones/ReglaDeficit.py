from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion


class ReglaDeficit(ReglaRecomendacion):
    def evaluar(self, resumen):
        if resumen.gastos <= resumen.ingresos:
            return []
        diferencia = resumen.gastos - resumen.ingresos
        return [
            Recomendacion(
                id="deficit",
                nivel="advertencia",
                titulo="Gastas más de lo que ingresas",
                mensaje=(
                    f"Este mes tus gastos superan tus ingresos por S/ {diferencia:,.2f}. "
                    "Prioriza lo esencial y recorta gastos no necesarios."
                ),
                dato=f"-S/ {diferencia:,.2f}",
            )
        ]