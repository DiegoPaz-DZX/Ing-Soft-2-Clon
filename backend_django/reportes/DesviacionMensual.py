from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


def _a_float(valor):
    return None if valor is None else float(valor)


@dataclass(frozen=True)
class DesviacionMensual:
    periodo: str
    etiqueta: str
    ingresos: Decimal
    gastos: Decimal
    balance: Decimal
    tasa_ahorro: Optional[Decimal]
    desviacion_gasto: Optional[Decimal]
    estado: str

    def a_dict(self):
        return {
            "periodo": self.periodo,
            "etiqueta": self.etiqueta,
            "ingresos": float(self.ingresos),
            "gastos": float(self.gastos),
            "balance": float(self.balance),
            "tasa_ahorro": _a_float(self.tasa_ahorro),
            "desviacion_gasto": _a_float(self.desviacion_gasto),
            "estado": self.estado,
        }