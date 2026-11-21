from collections import defaultdict
from decimal import Decimal

from balance.TipoMovimiento import TipoMovimiento

from .GastoPorCategoria import GastoPorCategoria
from .MovimientoReporte import MovimientoReporte
from .PeriodoMensual import PeriodoMensual
from .ReporteFinanciero import ReporteFinanciero

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
CENTAVOS = Decimal("0.01")
DOLARES = "USD"
DECIMA = Decimal("0.1")


class ConstructorReporte:
    def __init__(self, movimientos, nombres_categorias, desde=None, hasta=None, soles_por_dolar=None):
        self._soles_por_dolar = soles_por_dolar
        ordenados = sorted(movimientos, key=lambda m: (m.fecha, m.pk or 0))
        self._movimientos = [self._convertir(movimiento) for movimiento in ordenados]
        self._nombres = nombres_categorias
        self._reporte = ReporteFinanciero(desde=desde, hasta=hasta, soles_por_dolar=soles_por_dolar)
        self._agregar_resumen()

    def con_gastos_por_categoria(self):
        self._reporte.gastos_por_categoria = self._calcular_gastos_por_categoria()
        return self

    def con_evolucion_mensual(self):
        self._reporte.evolucion_mensual = self._calcular_evolucion_mensual()
        return self

    def con_analisis(self, reglas):
        reporte = self._reporte
        if reporte.cantidad_movimientos == 0:
            return self
        categorias = self._calcular_gastos_por_categoria()
        meses = self._calcular_evolucion_mensual()
        reporte.observaciones = [
            observacion
            for regla in reglas
            for observacion in regla.evaluar(reporte, categorias, meses)
        ]
        return self

    def con_movimientos(self):
        self._reporte.movimientos = list(reversed(self._movimientos))
        return self

    def construir(self):
        return self._reporte

    def _convertir(self, movimiento):
        moneda = getattr(movimiento, "moneda", "PEN")
        monto_en_soles = movimiento.monto
        if moneda == DOLARES:
            monto_en_soles = (movimiento.monto * self._soles_por_dolar).quantize(CENTAVOS)
        return MovimientoReporte(
            id=movimiento.pk,
            fecha=movimiento.fecha,
            tipo=movimiento.tipo,
            descripcion=movimiento.descripcion,
            categoria=movimiento.categoria,
            moneda=moneda,
            monto=movimiento.monto,
            monto_en_soles=monto_en_soles,
        )

    def _agregar_resumen(self):
        reporte = self._reporte
        for movimiento in self._movimientos:
            if movimiento.tipo == TipoMovimiento.INGRESO:
                reporte.total_ingresos += movimiento.monto_en_soles
            else:
                reporte.total_gastos += movimiento.monto_en_soles
        reporte.cantidad_movimientos = len(self._movimientos)
        reporte.balance = reporte.total_ingresos - reporte.total_gastos
        if reporte.total_ingresos > 0:
            reporte.tasa_ahorro = self._porcentaje(reporte.balance, reporte.total_ingresos)

    def _calcular_gastos_por_categoria(self):
        totales = defaultdict(Decimal)
        for movimiento in self._movimientos:
            if movimiento.tipo == TipoMovimiento.GASTO:
                totales[movimiento.categoria or "otros"] += movimiento.monto_en_soles
        total = self._reporte.total_gastos
        categorias = [
            GastoPorCategoria(
                codigo,
                self._nombres.get(codigo, codigo.capitalize()),
                monto,
                self._porcentaje(monto, total),
            )
            for codigo, monto in totales.items()
        ]
        return sorted(categorias, key=lambda categoria: categoria.monto, reverse=True)

    def _calcular_evolucion_mensual(self):
        meses = defaultdict(lambda: {"ingresos": Decimal("0.00"), "gastos": Decimal("0.00")})
        for movimiento in self._movimientos:
            clave = (movimiento.fecha.year, movimiento.fecha.month)
            campo = "ingresos" if movimiento.tipo == TipoMovimiento.INGRESO else "gastos"
            meses[clave][campo] += movimiento.monto_en_soles
        return [
            PeriodoMensual(
                f"{anio}-{mes:02d}", f"{MESES[mes - 1]} {anio}", totales["ingresos"], totales["gastos"]
            )
            for (anio, mes), totales in sorted(meses.items())
        ]

    def _porcentaje(self, parte, total):
        return (parte * 100 / total).quantize(DECIMA)
