from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class ReporteFinanciero:
    desde: Optional[date] = None
    hasta: Optional[date] = None
    cantidad_movimientos: int = 0
    total_ingresos: Decimal = Decimal("0")
    total_gastos: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")
    tasa_ahorro: Optional[Decimal] = None
    gastos_por_categoria: list = field(default_factory=list)
    evolucion_mensual: list = field(default_factory=list)
    observaciones: list = field(default_factory=list)
    movimientos: list = field(default_factory=list)
    soles_por_dolar: Optional[Decimal] = None
