from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PeriodoMensual:
    periodo: str
    etiqueta: str
    ingresos: Decimal
    gastos: Decimal
