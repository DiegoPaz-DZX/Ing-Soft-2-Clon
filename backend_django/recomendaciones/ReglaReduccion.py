from decimal import Decimal

from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion

UMBRAL_REDUCCION = Decimal("0.20")


class ReglaReduccion(ReglaRecomendacion):
    def evaluar(self, resumen):
        resultado = []
        for categoria, anterior in resumen.gastos_mes_anterior.items():
            if anterior <= 0:
                continue
            actual = resumen.gastos_por_categoria.get(categoria, 0)
            reduccion = (anterior - actual) / anterior
            if reduccion < UMBRAL_REDUCCION:
                continue
            nombre = resumen.nombre(categoria)
            dato = f"-{reduccion * 100:.0f}%"
            resultado.append(
                Recomendacion(
                    id=f"reduccion-{categoria}",
                    nivel="positivo",
                    titulo=f"Bajó tu gasto en {nombre}",
                    mensaje=f"Gastaste {dato[1:]} menos en {nombre} que el mes pasado. Buen trabajo.",
                    dato=dato,
                )
            )
        return resultado