from decimal import Decimal

from .TarjetaBalance import TarjetaBalance
from .TipoMovimiento import TipoMovimiento

MONEDAS = ("PEN", "USD")


class ServicioBalance:
    def __init__(self, repositorio, soles_por_dolar="3.42"):
        self._repositorio = repositorio
        self._soles_por_dolar = Decimal(str(soles_por_dolar))

    def obtener_tarjeta_balance(self, cuenta, moneda="PEN"):
        if moneda not in MONEDAS:
            raise ValueError("La divisa base no es válida.")
        tipo_cambio = self._soles_por_dolar
        ingresos_pen = self._repositorio.sumar_por_tipo(cuenta, TipoMovimiento.INGRESO, "PEN")
        gastos_pen = self._repositorio.sumar_por_tipo(cuenta, TipoMovimiento.GASTO, "PEN")
        ingresos_usd = self._repositorio.sumar_por_tipo(cuenta, TipoMovimiento.INGRESO, "USD")
        gastos_usd = self._repositorio.sumar_por_tipo(cuenta, TipoMovimiento.GASTO, "USD")
        if moneda == "USD":
            return TarjetaBalance(
                (ingresos_pen / tipo_cambio) + ingresos_usd,
                (gastos_pen / tipo_cambio) + gastos_usd,
            )
        return TarjetaBalance(
            ingresos_pen + (ingresos_usd * tipo_cambio),
            gastos_pen + (gastos_usd * tipo_cambio),
        )

    def obtener_tarjetas(self, cuenta):
        return {moneda: self.obtener_tarjeta_balance(cuenta, moneda) for moneda in MONEDAS}