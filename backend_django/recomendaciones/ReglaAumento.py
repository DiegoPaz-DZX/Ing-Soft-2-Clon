from decimal import Decimal

from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion

UMBRAL_AUMENTO = Decimal("0.30")


class ReglaAumento(ReglaRecomendacion):
    def evaluar(self, resumen):
        resultado = []
        for categoria, actual in resumen.gastos_por_categoria.items():
            anterior = resumen.gastos_mes_anterior.get(categoria, 0)
            if anterior <= 0:
                continue
            aumento = (actual - anterior) / anterior
            if aumento < UMBRAL_AUMENTO:
                continue
            nombre = resumen.nombre(categoria)
            dato = f"+{aumento * 100:.0f}%"
            resultado.append(
                Recomendacion(
                    id=f"aumento-{categoria}",
                    nivel="informacion",
                    titulo=f"Subió tu gasto en {nombre}",
                    mensaje=f"Gastaste {dato[1:]} más en {nombre} que el mes pasado.",
                    dato=dato,
                )
            )
        return resultado