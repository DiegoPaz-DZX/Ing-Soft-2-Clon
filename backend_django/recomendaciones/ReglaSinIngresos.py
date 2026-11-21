from .Recomendacion import Recomendacion
from .ReglaRecomendacion import ReglaRecomendacion


class ReglaSinIngresos(ReglaRecomendacion):
    def evaluar(self, resumen):
        if resumen.gastos > 0 and resumen.ingresos <= 0:
            return [
                Recomendacion(
                    id="sin-ingresos",
                    nivel="advertencia",
                    titulo="No registraste ingresos este mes",
                    mensaje="Tienes gastos pero ningún ingreso registrado. Anótalos para ver tu balance real.",
                )
            ]
        return []