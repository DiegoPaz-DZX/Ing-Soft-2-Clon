from datetime import date
from decimal import Decimal

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .Movimiento import Movimiento
from .RepositorioMovimientosDjango import RepositorioMovimientosDjango
from .ServicioBalance import ServicioBalance
from .TipoMovimiento import TipoMovimiento

RUTA_BALANCE = "/api/balance"


class BalanceCajaNegraTests(TestCase):
    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(correo="diego@example.com", clave_hash="hash")
        self.otra = CuentaUsuario.objects.create(correo="otra@example.com", clave_hash="hash")
        self.servicio = ServicioBalance(RepositorioMovimientosDjango())

    def _mov(self, tipo, monto, moneda, cuenta=None):
        return Movimiento.objects.create(
            usuario=cuenta or self.cuenta,
            tipo=tipo,
            monto=Decimal(monto),
            moneda=moneda,
            fecha=date(2026, 11, 14),
            descripcion="prueba",
        )

    def test_cn01_solo_soles(self):
        self._mov(TipoMovimiento.INGRESO, "500", "PEN")
        self._mov(TipoMovimiento.GASTO, "120", "PEN")

        t = self.servicio.obtener_tarjeta_balance(self.cuenta, "PEN")

        self.assertEqual((t.total_ingresos, t.total_gastos, t.balance),
                         (Decimal("500"), Decimal("120"), Decimal("380")))

    def test_cn02_solo_dolares_vistos_en_soles(self):
        self._mov(TipoMovimiento.INGRESO, "100", "USD")

        t = self.servicio.obtener_tarjeta_balance(self.cuenta, "PEN")

        self.assertEqual(t.balance, Decimal("342"))

    def test_cn03_mixto_en_soles(self):
        self._mov(TipoMovimiento.INGRESO, "342", "PEN")
        self._mov(TipoMovimiento.INGRESO, "100", "USD")

        self.assertEqual(self.servicio.obtener_tarjeta_balance(self.cuenta, "PEN").total_ingresos,
                         Decimal("684"))

    def test_cn04_mixto_en_dolares(self):
        self._mov(TipoMovimiento.INGRESO, "342", "PEN")
        self._mov(TipoMovimiento.INGRESO, "100", "USD")

        self.assertEqual(self.servicio.obtener_tarjeta_balance(self.cuenta, "USD").total_ingresos,
                         Decimal("200"))

    def test_cn05_sin_movimientos(self):
        for moneda in ("PEN", "USD"):
            with self.subTest(moneda=moneda):
                t = self.servicio.obtener_tarjeta_balance(self.cuenta, moneda)
                self.assertEqual((t.total_ingresos, t.total_gastos, t.balance),
                                 (Decimal("0"), Decimal("0"), Decimal("0")))

    def test_cn06_gastos_mayores_que_ingresos(self):
        self._mov(TipoMovimiento.INGRESO, "100", "PEN")
        self._mov(TipoMovimiento.GASTO, "250", "PEN")

        self.assertEqual(self.servicio.obtener_tarjeta_balance(self.cuenta, "PEN").balance,
                         Decimal("-150"))

    def test_cn07_divisa_invalida(self):
        with self.assertRaisesMessage(ValueError, "La divisa base no es válida."):
            self.servicio.obtener_tarjeta_balance(self.cuenta, "EUR")

    def test_cn08_no_suma_movimientos_de_otra_cuenta(self):
        self._mov(TipoMovimiento.INGRESO, "100", "PEN")
        self._mov(TipoMovimiento.INGRESO, "999", "PEN", cuenta=self.otra)

        self.assertEqual(self.servicio.obtener_tarjeta_balance(self.cuenta, "PEN").total_ingresos,
                         Decimal("100"))

    def test_cn09_monto_minimo(self):
        self._mov(TipoMovimiento.INGRESO, "0.01", "PEN")

        self.assertEqual(self.servicio.obtener_tarjeta_balance(self.cuenta, "PEN").balance,
                         Decimal("0.01"))

    def test_cn10_obtener_tarjetas(self):
        self._mov(TipoMovimiento.INGRESO, "342", "PEN")

        tarjetas = self.servicio.obtener_tarjetas(self.cuenta)

        self.assertEqual(set(tarjetas), {"PEN", "USD"})
        self.assertEqual(tarjetas["PEN"].balance, Decimal("342"))
        self.assertEqual(tarjetas["USD"].balance, Decimal("100"))

    def test_cn11_endpoint_sin_token(self):
        self.assertEqual(self.client.get(RUTA_BALANCE).status_code, SIN_TOKEN)

    def test_cn12_endpoint_con_token_valido(self):
        token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)

        respuesta = self.client.get(RUTA_BALANCE, HTTP_AUTHORIZATION=f"Bearer {token}")

        self.assertEqual(respuesta.status_code, 200)