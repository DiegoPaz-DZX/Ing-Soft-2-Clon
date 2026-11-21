from datetime import date
from decimal import Decimal

from django.test import TestCase

from sesion.models import TokenRevocado
from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .Movimiento import Movimiento
from .ServicioBalance import ServicioBalance
from .TipoMovimiento import TipoMovimiento
from .RepositorioMovimientosDjango import RepositorioMovimientosDjango


class DiegoPazBalanceTests(TestCase):
    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(
            correo="diego@example.com",
            clave_hash="hash",
        )

    def movimiento(self, tipo, monto, moneda):
        return Movimiento.objects.create(
            usuario=self.cuenta,
            tipo=tipo,
            monto=Decimal(monto),
            moneda=moneda,
            fecha=date(2026, 11, 14),
            descripcion="prueba",
        )

    def test_obtener_tarjeta_balance_unifica_soles_y_dolares(self):
        self.movimiento(TipoMovimiento.INGRESO, "1000", "PEN")
        self.movimiento(TipoMovimiento.INGRESO, "100", "USD")
        self.movimiento(TipoMovimiento.GASTO, "200", "PEN")
        self.movimiento(TipoMovimiento.GASTO, "20", "USD")

        tarjeta = ServicioBalance(
            RepositorioMovimientosDjango()
        ).obtener_tarjeta_balance(self.cuenta, "PEN")

        self.assertEqual(tarjeta.total_ingresos, Decimal("1375.00"))
        self.assertEqual(tarjeta.total_gastos, Decimal("275.00"))
        self.assertEqual(tarjeta.balance, Decimal("1100.00"))

    def test_cierre_sesion_endpoint_responde_200_e_invalida_token(self):
        token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)
        cabecera = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        respuesta = self.client.post("/api/logout", **cabecera)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(TokenRevocado.objects.exists())
        self.assertEqual(self.client.get("/api/balance", **cabecera).status_code, 401)

    def test_dashboard_balance_cambia_segun_divisa_base(self):
        self.movimiento(TipoMovimiento.INGRESO, "342", "PEN")
        self.movimiento(TipoMovimiento.INGRESO, "100", "USD")

        servicio = ServicioBalance(RepositorioMovimientosDjango())
        soles = servicio.obtener_tarjeta_balance(self.cuenta, "PEN")
        dolares = servicio.obtener_tarjeta_balance(self.cuenta, "USD")

        self.assertEqual(soles.total_ingresos, Decimal("684.00"))
        self.assertEqual(dolares.total_ingresos, Decimal("200.00"))
