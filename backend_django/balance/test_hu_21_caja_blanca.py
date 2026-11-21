import os
from decimal import Decimal
from unittest.mock import Mock

from django.test import SimpleTestCase

from .RepositorioMovimientos import RepositorioMovimientos
from .ServicioBalance import ServicioBalance
from .TipoMovimiento import TipoMovimiento

ING = TipoMovimiento.INGRESO
GAS = TipoMovimiento.GASTO
REPORTE = os.environ.get("KYZEN_REPORTE") == "1"

ERR_DIVISA = "ValueError: La divisa base no es válida."


def mostrar(camino, entrada, esperado, obtenido):
    if REPORTE:
        print(f"REPORTE|{camino}|{entrada}|{esperado}|{obtenido}")


class ObtenerTarjetaBalanceCajaBlancaTests(SimpleTestCase):
    def setUp(self):
        totales = {(ING, "PEN"): "400", (ING, "USD"): "50", (GAS, "PEN"): "40", (GAS, "USD"): "5"}
        self.repositorio = Mock(spec=RepositorioMovimientos)
        self.repositorio.sumar_por_tipo.side_effect = (
            lambda cuenta, tipo, moneda="PEN": Decimal(totales.get((tipo, moneda), "0"))
        )
        self.servicio = ServicioBalance(self.repositorio, soles_por_dolar="4")

    def _intentar(self, camino, entrada, esperado, *argumentos):
        try:
            tarjeta = self.servicio.obtener_tarjeta_balance("cuenta", *argumentos)
            obtenido = f"OK balance={tarjeta.balance:.2f}"
        except ValueError as error:
            obtenido = f"ValueError: {error}"
        mostrar(camino, entrada, esperado, obtenido)
        return obtenido

    def test_c1_divisa_invalida(self):
        self.assertEqual(self._intentar("C1", "moneda='EUR'", ERR_DIVISA, "EUR"), ERR_DIVISA)

    def test_c2_balance_en_dolares(self):
        esperado = "OK balance=135.00"
        self.assertEqual(self._intentar("C2", "moneda='USD'", esperado, "USD"), esperado)

    def test_c3_balance_en_soles(self):
        esperado = "OK balance=540.00"
        self.assertEqual(self._intentar("C3", "moneda='PEN'", esperado, "PEN"), esperado)

    def test_l1_divisa_en_minuscula(self):
        self.assertEqual(self._intentar("L1", "moneda='usd'", ERR_DIVISA, "usd"), ERR_DIVISA)

    def test_l2_divisa_por_defecto(self):
        esperado = "OK balance=540.00"
        self.assertEqual(self._intentar("L2", "sin moneda", esperado), esperado)

    def test_c4_obtener_tarjetas_recorre_las_dos_divisas(self):
        tarjetas = self.servicio.obtener_tarjetas("cuenta")
        mostrar("C4", "obtener_tarjetas()", "PEN=540.00 USD=135.00",
                f"PEN={tarjetas['PEN'].balance:.2f} USD={tarjetas['USD'].balance:.2f}")

        self.assertEqual(set(tarjetas), {"PEN", "USD"})
        self.assertEqual(tarjetas["PEN"].balance, Decimal("540"))
        self.assertEqual(tarjetas["USD"].balance, Decimal("135"))