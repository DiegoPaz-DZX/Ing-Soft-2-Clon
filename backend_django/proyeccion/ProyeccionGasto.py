from dataclasses import dataclass
from decimal import Decimal

@dataclass
class ProyeccionGasto:
    gasto_actual: Decimal
    gasto_atipico: Decimal
    gasto_proyectado: Decimal
    ingresos_mes: Decimal
    sugerencia: str

    # True si se espera gastar mas de lo que se ingresa en el mes
    @property
    def hay_sobregasto(self):
        return self.gasto_proyectado > self.ingresos_mes

    def a_dict(self):
        return {
            "gastoActual": float(self.gasto_actual),
            "gastoAtipico": float(self.gasto_atipico),
            "gastoProyectado": float(self.gasto_proyectado),
            "ingresosMes": float(self.ingresos_mes),
            "haySobregasto": self.hay_sobregasto,
            "sugerencia": self.sugerencia,
        }