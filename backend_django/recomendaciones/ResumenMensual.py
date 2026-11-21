from collections import defaultdict
from decimal import Decimal

from balance.TipoMovimiento import TipoMovimiento


class ResumenMensual:
    def __init__(self, movimientos, hoy, nombres_categorias):
        self._nombres = nombres_categorias
        self.ingresos = Decimal("0")
        self.gastos = Decimal("0")
        self.gastos_por_categoria = defaultdict(Decimal)
        self.gastos_mes_anterior = defaultdict(Decimal)
        self.cantidad = 0  # movimientos del mes actual

        actual = (hoy.year, hoy.month)
        anterior = (hoy.year, hoy.month - 1) if hoy.month > 1 else (hoy.year - 1, 12)

        for m in movimientos:
            periodo = (m.fecha.year, m.fecha.month)
            categoria = m.categoria or "otros"
            if periodo == actual:
                self.cantidad += 1
                if m.tipo == TipoMovimiento.INGRESO:
                    self.ingresos += m.monto
                else:
                    self.gastos += m.monto
                    self.gastos_por_categoria[categoria] += m.monto
            elif periodo == anterior and m.tipo == TipoMovimiento.GASTO:
                self.gastos_mes_anterior[categoria] += m.monto

    def nombre(self, codigo):
        return self._nombres.get(codigo, codigo.capitalize())