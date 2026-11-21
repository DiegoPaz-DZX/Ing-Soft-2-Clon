from datetime import date
from decimal import Decimal

from django.test import TestCase

from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento
from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens


def crear_cuenta(correo="ana@correo.com"):
    return CuentaUsuario.objects.create(correo=correo, clave_hash="x")


def cabecera(cuenta):
    token = ServicioTokens(RepositorioCuentasDjango()).crear(cuenta)
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def gastar(cuenta, monto, categoria="alimentacion"):
    return Movimiento.objects.create(
        tipo=TipoMovimiento.GASTO, monto=Decimal(monto), fecha=date.today(),
        descripcion="prueba", categoria=categoria, usuario=cuenta,
    )


class AlertasEndpointTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()
        self.cabecera = cabecera(self.cuenta)

    def poner_limite(self, monto, categoria="alimentacion", cuenta=None):
        return self.client.post(
            "/api/limites",
            data={"categoria": categoria, "limite_mensual": monto},
            content_type="application/json",
            **(cabecera(cuenta) if cuenta else self.cabecera),
        )

    def test_sin_limites_no_hay_alertas(self):
        respuesta = self.client.get("/api/alertas", **self.cabecera)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), [])

    def test_un_gasto_sobre_el_limite_genera_alerta_critica(self):
        self.poner_limite(100)
        gastar(self.cuenta, "150")
        respuesta = self.client.get("/api/alertas", **self.cabecera)
        self.assertEqual(respuesta.status_code, 200)
        tipos = {alerta["tipo_alerta"] for alerta in respuesta.json()}
        self.assertIn("critica", tipos)

    def test_un_gasto_bajo_el_limite_no_genera_alerta(self):
        self.poner_limite(1000)
        gastar(self.cuenta, "10")
        self.assertEqual(self.client.get("/api/alertas", **self.cabecera).json(), [])

    def test_no_repite_la_misma_alerta(self):
        self.poner_limite(100)
        gastar(self.cuenta, "150")
        primera = self.client.get("/api/alertas", **self.cabecera).json()
        segunda = self.client.get("/api/alertas", **self.cabecera).json()
        self.assertEqual(len(primera), len(segunda))

    def test_las_alertas_son_por_cuenta(self):
        otra = crear_cuenta("luis@correo.com")
        self.poner_limite(100, cuenta=otra)
        gastar(otra, "150")
        self.assertEqual(self.client.get("/api/alertas", **self.cabecera).json(), [])

    def test_los_gastos_de_otra_cuenta_no_cuentan(self):
        self.poner_limite(100)
        gastar(crear_cuenta("luis@correo.com"), "999")
        self.assertEqual(self.client.get("/api/alertas", **self.cabecera).json(), [])

    def test_limite_invalido_responde_400(self):
        self.assertEqual(self.poner_limite(0).status_code, 400)

    def test_los_limites_se_listan_por_cuenta(self):
        self.poner_limite(250)
        self.assertEqual(self.client.get("/api/limites", **self.cabecera).json(), {"alimentacion": "250.00"})

    def test_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get("/api/alertas").status_code, 401)
        self.assertEqual(self.client.get("/api/limites").status_code, 401)
        self.assertEqual(self.client.post("/api/limites", data={}, content_type="application/json").status_code, 401)
