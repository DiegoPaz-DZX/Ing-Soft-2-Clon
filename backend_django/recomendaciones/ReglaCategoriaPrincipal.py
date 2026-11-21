from decimal import Decimal

from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion

UMBRAL = Decimal("0.40")  # si pasa de aquí, ya sale ReglaConcentracion


class ReglaCategoriaPrincipal(ReglaRecomendacion):
    def evaluar(self, resumen):
        if resumen.gastos <= 0 or not resumen.gastos_por_categoria:
            return []
        categoria, total = max(resumen.gastos_por_categoria.items(), key=lambda p: p[1])
        porcentaje = total / resumen.gastos
        if porcentaje >= UMBRAL:
            return []
        nombre = resumen.nombre(categoria)
        return [
            Recomendacion(
                id=f"principal-{categoria}",
                nivel="informacion",
                titulo=f"Tu mayor gasto es {nombre}",
                mensaje=f"Gastaste S/ {total:,.2f} en {nombre} este mes ({porcentaje * 100:.0f}% del total).",
                dato=f"{porcentaje * 100:.0f}%",
            )
        ]