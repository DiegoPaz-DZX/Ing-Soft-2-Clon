from datetime import date
from decimal import Decimal

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .MontoInvalidoException import MontoInvalidoException
from .Movimiento import Movimiento
from .RepositorioMovimientos import RepositorioMovimientos
from .RepositorioMovimientosDjango import RepositorioMovimientosDjango
from .ServicioBalance import ServicioBalance
from .TipoMovimiento import TipoMovimiento


def crear_cuenta(correo="ana@correo.com"):
    return CuentaUsuario.objects.create(correo=correo, clave_hash="x")


def crear(tipo, monto, cuenta=None, moneda="PEN"):
    return Movimiento.objects.create(
        tipo=tipo,
        monto=Decimal(monto),
        fecha=date(2026, 10, 1),
        descripcion="prueba",
        moneda=moneda,
        usuario=cuenta,
    )


def balance_de(cuenta, moneda="PEN"):
    servicio = ServicioBalance(RepositorioMovimientosDjango())
    return servicio.obtener_tarjeta_balance(cuenta, moneda)


class ServicioBalanceTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()

    def test_sin_movimientos_el_balance_es_cero(self):
        tarjeta = balance_de(self.cuenta)
        self.assertEqual(tarjeta.total_ingresos, Decimal("0"))
        self.assertEqual(tarjeta.total_gastos, Decimal("0"))
        self.assertEqual(tarjeta.balance, Decimal("0"))

    def test_el_balance_es_ingresos_menos_gastos(self):
        crear(TipoMovimiento.INGRESO, "1500", self.cuenta)
        crear(TipoMovimiento.GASTO, "200", self.cuenta)
        crear(TipoMovimiento.GASTO, "350.50", self.cuenta)
        tarjeta = balance_de(self.cuenta)
        self.assertEqual(tarjeta.total_ingresos, Decimal("1500"))
        self.assertEqual(tarjeta.total_gastos, Decimal("550.50"))
        self.assertEqual(tarjeta.balance, Decimal("949.50"))

    def test_el_balance_se_actualiza_al_agregar_un_movimiento(self):
        crear(TipoMovimiento.INGRESO, "100", self.cuenta)
        self.assertEqual(balance_de(self.cuenta).balance, Decimal("100"))
        crear(TipoMovimiento.GASTO, "40", self.cuenta)
        self.assertEqual(balance_de(self.cuenta).balance, Decimal("60"))

    def test_el_balance_puede_ser_negativo(self):
        crear(TipoMovimiento.GASTO, "25", self.cuenta)
        self.assertEqual(balance_de(self.cuenta).balance, Decimal("-25"))

    def test_cada_moneda_tiene_su_propio_balance(self):
        crear(TipoMovimiento.INGRESO, "1000", self.cuenta, "PEN")
        crear(TipoMovimiento.INGRESO, "50", self.cuenta, "USD")
        crear(TipoMovimiento.GASTO, "20", self.cuenta, "USD")
        self.assertEqual(balance_de(self.cuenta, "PEN").balance, Decimal("1112.5"))
        self.assertAlmostEqual(
            balance_de(self.cuenta, "USD").balance,
            Decimal("296.6666666667"),
            places=10,
        )

    def test_no_suma_los_movimientos_de_otra_cuenta(self):
        otra = crear_cuenta("luis@correo.com")
        crear(TipoMovimiento.INGRESO, "700", self.cuenta)
        crear(TipoMovimiento.INGRESO, "9999", otra)
        self.assertEqual(balance_de(self.cuenta).balance, Decimal("700"))


class RepositorioFalso(RepositorioMovimientos):
    def agregar(self, movimiento):
        pass

    def sumar_por_tipo(self, cuenta, tipo, moneda="PEN"):
        return Decimal("100") if tipo == TipoMovimiento.INGRESO else Decimal("30")

    def sumar_gasto_categoria_mes(self, cuenta, categoria, anio, mes):
        return Decimal("0")

    def eliminar(self, cuenta, movimiento_id):
        return False

    def obtener_por_id(self, cuenta, movimiento_id):
        return None

    def actualizar(self, movimiento):
        pass


class ServicioBalanceConRepositorioFalsoTests(TestCase):
    def test_el_servicio_funciona_con_cualquier_repositorio(self):
        tarjeta = ServicioBalance(RepositorioFalso()).obtener_tarjeta_balance(None)
        self.assertEqual(tarjeta.balance, Decimal("332.5"))


class MovimientoTests(TestCase):
    def test_monto_cero_o_negativo_lanza_error(self):
        with self.assertRaises(MontoInvalidoException):
            crear(TipoMovimiento.GASTO, "0")
        with self.assertRaises(MontoInvalidoException):
            crear(TipoMovimiento.GASTO, "-10")
        self.assertEqual(Movimiento.objects.count(), 0)


class BalanceEndpointTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()
        token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)
        self.cabecera = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_responde_el_json_de_la_tarjeta(self):
        crear(TipoMovimiento.INGRESO, "1500", self.cuenta)
        crear(TipoMovimiento.GASTO, "550.50", self.cuenta)
        respuesta = self.client.get("/api/balance", **self.cabecera)
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(
            {clave: datos[clave] for clave in ("totalIngresos", "totalGastos", "balance")},
            {"totalIngresos": 1500.0, "totalGastos": 550.5, "balance": 949.5},
        )

    def test_incluye_el_balance_en_dolares(self):
        crear(TipoMovimiento.INGRESO, "80", self.cuenta, "USD")
        datos = self.client.get("/api/balance", **self.cabecera).json()
        self.assertEqual(datos["USD"]["balance"], 80.0)

    def test_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get("/api/balance").status_code, 401)

    def test_con_token_invalido_responde_401(self):
        respuesta = self.client.get("/api/balance", HTTP_AUTHORIZATION="Bearer falso")
        self.assertEqual(respuesta.status_code, 401)

    def test_incluye_los_permisos_para_el_frontend(self):
        respuesta = self.client.get("/api/balance", **self.cabecera)
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_solo_acepta_get(self):
        respuesta = self.client.post("/api/balance", **self.cabecera)
        self.assertEqual(respuesta.status_code, 405)


class EditarYEliminarEndpointTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()
        token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)
        self.cabecera = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        self.movimiento = crear(TipoMovimiento.GASTO, "40", self.cuenta)
        self.movimiento.categoria = "alimentacion"
        self.movimiento.save()

    def editar(self, datos, id_movimiento=None, **cabecera):
        return self.client.put(
            f"/api/movimientos/{id_movimiento or self.movimiento.pk}/editar",
            data=datos,
            content_type="application/json",
            **(cabecera or self.cabecera),
        )

    def datos(self, **cambios):
        base = {"tipo": "gasto", "monto": "55", "fecha": "2026-10-02", "categoria": "transporte", "moneda": "PEN"}
        return {**base, **cambios}

    def test_edita_un_movimiento_propio(self):
        respuesta = self.editar(self.datos(descripcion="taxi"))
        self.assertEqual(respuesta.status_code, 200)
        self.movimiento.refresh_from_db()
        self.assertEqual(self.movimiento.monto, Decimal("55"))
        self.assertEqual(self.movimiento.categoria, "transporte")

    def test_editar_con_monto_invalido_responde_400(self):
        self.assertEqual(self.editar(self.datos(monto="0")).status_code, 400)

    def test_editar_sin_sesion_responde_401(self):
        self.assertEqual(self.editar(self.datos(), HTTP_AUTHORIZATION="").status_code, 401)

    def test_editar_con_token_falso_responde_401(self):
        self.assertEqual(self.editar(self.datos(), HTTP_AUTHORIZATION="Bearer falso").status_code, 401)

    def test_no_puede_editar_el_movimiento_de_otra_cuenta(self):
        ajeno = crear(TipoMovimiento.GASTO, "10", crear_cuenta("luis@correo.com"))
        self.assertEqual(self.editar(self.datos(), ajeno.pk).status_code, 404)

    def test_elimina_un_movimiento_propio(self):
        respuesta = self.client.delete(f"/api/movimientos/{self.movimiento.pk}/eliminar", **self.cabecera)
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Movimiento.objects.filter(pk=self.movimiento.pk).exists())

    def test_no_puede_eliminar_el_movimiento_de_otra_cuenta(self):
        ajeno = crear(TipoMovimiento.GASTO, "10", crear_cuenta("luis@correo.com"))
        respuesta = self.client.delete(f"/api/movimientos/{ajeno.pk}/eliminar", **self.cabecera)
        self.assertEqual(respuesta.status_code, 404)
        self.assertTrue(Movimiento.objects.filter(pk=ajeno.pk).exists())

    def test_eliminar_sin_sesion_responde_401(self):
        self.assertEqual(self.client.delete(f"/api/movimientos/{self.movimiento.pk}/eliminar").status_code, 401)

    def test_registrar_con_token_falso_responde_401(self):
        respuesta = self.client.post(
            "/api/movimientos/nuevo", data={}, content_type="application/json",
            HTTP_AUTHORIZATION="Bearer falso",
        )
        self.assertEqual(respuesta.status_code, 401)
