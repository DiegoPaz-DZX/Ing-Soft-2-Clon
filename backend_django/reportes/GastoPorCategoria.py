from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class GastoPorCategoria:
    codigo: str
    nombre: str
    monto: Decimal
    porcentaje: Decimal
