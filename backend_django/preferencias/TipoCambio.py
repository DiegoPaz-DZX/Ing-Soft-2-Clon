from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class TipoCambio:
    fecha: date
    soles_por_dolar: Decimal
    fuente: str
