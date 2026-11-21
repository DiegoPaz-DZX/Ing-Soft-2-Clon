from decimal import Decimal

from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion

UMBRAL = Decimal("0.40")


class ReglaConcentracion(ReglaRecomendacion):
    def evaluar(self, resumen):
        if resumen.gastos <= 0:
            return []
        categoria, total = max(resumen.gastos_por_categoria.items(), key=lambda p: p[1])
        porcentaje = total / resumen.gastos
        if porcentaje < UMBRAL:
            return []
        nombre = resumen.nombre(categoria)
        dato = f"{porcentaje * 100:.0f}%"
        return [
            Recomendacion(
                id=f"concentracion-{categoria}",
                nivel="advertencia",
                titulo=f"{nombre} concentra tus gastos",
                mensaje=f"El {dato} de tus gastos de este mes es en {nombre}. Revisa si puedes reducirlo.",
                dato=dato,
            )
        ]