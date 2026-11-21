from decimal import Decimal

from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion

AHORRO_BUENO = Decimal("0.20")
AHORRO_BAJO = Decimal("0.10")


class ReglaAhorro(ReglaRecomendacion):
    def evaluar(self, resumen):
        if resumen.ingresos <= 0 or resumen.gastos > resumen.ingresos:
            return []  # el caso de déficit lo cubre ReglaDeficit
        porcentaje = (resumen.ingresos - resumen.gastos) / resumen.ingresos
        dato = f"{porcentaje * 100:.0f}%"
        if porcentaje >= AHORRO_BUENO:
            return [
                Recomendacion(
                    id="ahorro-bueno",
                    nivel="positivo",
                    titulo="Estás ahorrando bien",
                    mensaje=f"Ahorraste el {dato} de tus ingresos este mes. Sigue así.",
                    dato=dato,
                )
            ]
        if porcentaje < AHORRO_BAJO:
            return [
                Recomendacion(
                    id="ahorro-bajo",
                    nivel="informacion",
                    titulo="Ahorras poco",
                    mensaje=f"Solo ahorraste el {dato} de tus ingresos. Una meta común es ahorrar al menos el 10%.",
                    dato=dato,
                )
            ]
        return []