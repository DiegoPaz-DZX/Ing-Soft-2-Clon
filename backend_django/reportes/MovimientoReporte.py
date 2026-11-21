from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class MovimientoReporte:
    id: Optional[int]
    fecha: date
    tipo: str
    descripcion: str
    categoria: str
    moneda: str
    monto: Decimal
    monto_en_soles: Decimal
