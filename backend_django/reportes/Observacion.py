from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Observacion:
    nivel: str
    titulo: str
    mensaje: str
    monto: Optional[Decimal] = None
