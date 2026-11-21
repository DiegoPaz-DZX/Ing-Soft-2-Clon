from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TarjetaBalance:
    total_ingresos: Decimal
    total_gastos: Decimal

    @property
    def balance(self):
        return self.total_ingresos - self.total_gastos
