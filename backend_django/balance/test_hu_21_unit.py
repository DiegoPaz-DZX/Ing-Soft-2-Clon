from decimal import Decimal
from unittest.mock import Mock, call

from django.test import SimpleTestCase

from .RepositorioMovimientos import RepositorioMovimientos
from .ServicioBalance import ServicioBalance
from .TipoMovimiento import TipoMovimiento

ING = TipoMovimiento.INGRESO
GAS = TipoMovimiento.GASTO


def repositorio_con(totales):
    repositorio = Mock(spec=RepositorioMovimientos)
    repositorio.sumar_por_tipo.side_effect = (
        lambda cuenta, tipo, moneda="PEN": Decimal(totales.get((tipo, moneda), "0"))
    )
    return repositorio


class ServicioBalanceUnitariasTests(SimpleTestCase):
    def test_balance_en_soles_convierte_los_dolares(self):
        repositorio = repositorio_con(
            {(ING, "PEN"): "1000", (ING, "USD"): "100", (GAS, "PEN"): "200", (GAS, "USD"): "20"}
        )

        tarjeta = ServicioBalance(repositorio, soles_por_dolar="3.75").obtener_tarjeta_balance("c", "PEN")

        self.assertEqual(tarjeta.total_ingresos, Decimal("1375"))
        self.assertEqual(tarjeta.total_gastos, Decimal("275"))
        self.assertEqual(tarjeta.balance, Decimal("1100"))

    def test_balance_en_dolares_convierte_los_soles(self):
        repositorio = repositorio_con(
            {(ING, "PEN"): "400", (ING, "USD"): "50", (GAS, "PEN"): "40", (GAS, "USD"): "5"}
        )

        tarjeta = ServicioBalance(repositorio, soles_por_dolar="4").obtener_tarjeta_balance("c", "USD")

        self.assertEqual(tarjeta.total_ingresos, Decimal("150"))
        self.assertEqual(tarjeta.total_gastos, Decimal("15"))
        self.assertEqual(tarjeta.balance, Decimal("135"))

    def test_el_tipo_de_cambio_por_defecto_es_3_42(self):
        repositorio = repositorio_con({(ING, "USD"): "100"})

        tarjeta = ServicioBalance(repositorio).obtener_tarjeta_balance("c", "PEN")

        self.assertEqual(tarjeta.total_ingresos, Decimal("342"))

    def test_acepta_el_tipo_de_cambio_como_numero(self):
        repositorio = repositorio_con({(ING, "USD"): "10"})

        con_entero = ServicioBalance(repositorio, soles_por_dolar=4).obtener_tarjeta_balance("c", "PEN")
        con_decimal = ServicioBalance(repositorio, soles_por_dolar=3.75).obtener_tarjeta_balance("c", "PEN")

        self.assertEqual(con_entero.total_ingresos, Decimal("40"))
        self.assertEqual(con_decimal.total_ingresos, Decimal("37.5"))

    def test_la_divisa_por_defecto_es_soles(self):
        repositorio = repositorio_con({(ING, "PEN"): "100", (ING, "USD"): "10"})
        servicio = ServicioBalance(repositorio, soles_por_dolar="4")

        self.assertEqual(
            servicio.obtener_tarjeta_balance("c").balance,
            servicio.obtener_tarjeta_balance("c", "PEN").balance,
        )

    def test_cuenta_sin_movimientos_tiene_balance_cero(self):
        servicio = ServicioBalance(repositorio_con({}))

        for moneda in ("PEN", "USD"):
            with self.subTest(moneda=moneda):
                tarjeta = servicio.obtener_tarjeta_balance("c", moneda)
                self.assertEqual(tarjeta.total_ingresos, Decimal("0"))
                self.assertEqual(tarjeta.total_gastos, Decimal("0"))
                self.assertEqual(tarjeta.balance, Decimal("0"))

    def test_balance_negativo_cuando_los_gastos_superan_los_ingresos(self):
        repositorio = repositorio_con({(ING, "PEN"): "100", (GAS, "PEN"): "250"})

        tarjeta = ServicioBalance(repositorio).obtener_tarjeta_balance("c", "PEN")

        self.assertEqual(tarjeta.balance, Decimal("-150"))

    def test_divisa_invalida_es_rechazada_sin_consultar_el_repositorio(self):
        repositorio = repositorio_con({})
        servicio = ServicioBalance(repositorio)

        for moneda in ("EUR", "usd", "", None):
            with self.subTest(moneda=moneda):
                with self.assertRaisesMessage(ValueError, "La divisa base no es válida."):
                    servicio.obtener_tarjeta_balance("c", moneda)

        repositorio.sumar_por_tipo.assert_not_called()

    def test_consulta_las_cuatro_sumas_al_repositorio(self):
        repositorio = repositorio_con({})

        ServicioBalance(repositorio).obtener_tarjeta_balance("cuenta", "PEN")

        self.assertEqual(repositorio.sumar_por_tipo.call_count, 4)
        repositorio.sumar_por_tipo.assert_has_calls(
            [
                call("cuenta", ING, "PEN"),
                call("cuenta", GAS, "PEN"),
                call("cuenta", ING, "USD"),
                call("cuenta", GAS, "USD"),
            ],
            any_order=True,
        )

    def test_obtener_tarjetas_devuelve_soles_y_dolares(self):
        repositorio = repositorio_con({(ING, "PEN"): "400", (ING, "USD"): "50"})
        servicio = ServicioBalance(repositorio, soles_por_dolar="4")

        tarjetas = servicio.obtener_tarjetas("c")

        self.assertEqual(set(tarjetas), {"PEN", "USD"})
        self.assertEqual(tarjetas["PEN"].balance, Decimal("600"))
        self.assertEqual(tarjetas["USD"].balance, Decimal("150"))

    def test_el_mismo_dinero_vale_lo_mismo_en_ambas_divisas(self):
        repositorio = repositorio_con({(ING, "PEN"): "342", (ING, "USD"): "100"})
        servicio = ServicioBalance(repositorio, soles_por_dolar="3.42")

        self.assertEqual(servicio.obtener_tarjeta_balance("c", "PEN").total_ingresos, Decimal("684"))
        self.assertEqual(servicio.obtener_tarjeta_balance("c", "USD").total_ingresos, Decimal("200"))