from unittest.mock import patch

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario

from .MetaAhorroFacade import MetaAhorroFacade
from .models import MetaAhorro
from .RepositorioMetas import RepositorioMetas
from usuarios.TokenInvalidoException import TokenInvalidoException

URL = "/api/metas"


class CrearMetaCajaNegraTests(TestCase):
    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(correo="joaquin@correo.com", clave_hash="x")
        self.otra = CuentaUsuario.objects.create(correo="otra@correo.com", clave_hash="x")
        RepositorioMetas().crear(self.cuenta, "Viaje", 1000)

    def _post(self, cuerpo, cuenta=None, con_sesion=True):
        """Con sesión: simula la autenticación devolviendo la cuenta. Sin sesión: código real."""
        if not con_sesion:
            return self.client.post(URL, data=cuerpo, content_type="application/json")
        with patch.object(MetaAhorroFacade, "cuenta", return_value=cuenta or self.cuenta):
            return self.client.post(URL, data=cuerpo, content_type="application/json")

    def test_cn01_meta_valida(self):
        r = self._post({"nombre": "Fondo", "objetivo_pen": "2500.00"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["nombre"], "Fondo")
        self.assertEqual(r.json()["objetivoPEN"], "2500.00")

    def test_cn02_monto_minimo_valido(self):
        self.assertEqual(self._post({"nombre": "Min", "objetivo_pen": "0.01"}).status_code, 201)

    def test_cn03_monto_cero(self):
        self.assertEqual(self._post({"nombre": "Cero", "objetivo_pen": "0"}).status_code, 400)

    def test_cn04_monto_negativo(self):
        self.assertEqual(self._post({"nombre": "Neg", "objetivo_pen": "-1"}).status_code, 400)

    def test_cn05_monto_texto(self):
        self.assertEqual(self._post({"nombre": "Txt", "objetivo_pen": "abc"}).status_code, 400)

    def test_cn06_sin_monto(self):
        self.assertEqual(self._post({"nombre": "SinMonto"}).status_code, 400)

    def test_cn07_nombre_vacio(self):
        self.assertEqual(self._post({"nombre": "   ", "objetivo_pen": "100"}).status_code, 400)

    def test_cn08_nombre_repetido(self):
        antes = MetaAhorro.objects.count()
        self.assertEqual(self._post({"nombre": "viaje", "objetivo_pen": "100"}).status_code, 400)
        self.assertEqual(MetaAhorro.objects.count(), antes)

    def test_cn09_mismo_nombre_otra_cuenta(self):
        r = self._post({"nombre": "Viaje", "objetivo_pen": "100"}, cuenta=self.otra)
        self.assertEqual(r.status_code, 201)

    def test_cn10_sin_sesion(self):
        r = self._post({"nombre": "X", "objetivo_pen": "1"}, con_sesion=False)
        self.assertEqual(r.status_code, 400)

    def test_cn11_json_malformado(self):
        self.assertEqual(self._post("{").status_code, 400)

    def test_cn12_monto_nan(self):
        self.assertEqual(self._post({"nombre": "Nan", "objetivo_pen": "NaN"}).status_code, 400)

    def test_cn13_nombre_de_121_caracteres(self):
        self.assertEqual(self._post({"nombre": "a" * 121, "objetivo_pen": "100"}).status_code, 400)

    def test_cn14_nombre_de_120_caracteres(self):
        self.assertEqual(self._post({"nombre": "b" * 120, "objetivo_pen": "100"}).status_code, 201)

    def test_cn15_token_invalido_con_servicio_real(self):
        r = self.client.post(
            URL,
            data={"nombre": "X", "objetivo_pen": "1"},
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer token-que-no-existe",
        )
        self.assertEqual(r.status_code, 401)

    def test_cn15b_token_invalido_simulado(self):
        with patch.object(
            MetaAhorroFacade, "cuenta",
            side_effect=TokenInvalidoException("Token inválido."),
        ):
            r = self.client.post(
                URL,
                data={"nombre": "X", "objetivo_pen": "1"},
                content_type="application/json",
            )
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json()["error"], "Token inválido.")
