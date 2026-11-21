
import json

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario

from .CredencialesInvalidasException import CredencialesInvalidasException
from .EstrategiaAutenticacion import EstrategiaAutenticacion
from .ProveedorAutenticacion import ProveedorAutenticacion


class EstrategiaQueSiempreAcepta(EstrategiaAutenticacion):
    def autenticar(self, correo, clave):
        return "cuenta"


class CajaBlancaValidarTests(TestCase):


    def setUp(self):
        self.proveedor = ProveedorAutenticacion(EstrategiaQueSiempreAcepta())

    def assertRechaza(self, correo, clave, mensaje):
        with self.assertRaises(CredencialesInvalidasException) as error:
            self.proveedor._validar(correo, clave)
        self.assertEqual(str(error.exception), mensaje)

    def test_cb01_correo_que_no_es_texto(self):
        self.assertRechaza(123, "Clave123!", "Debe ingresar su correo y contraseña.")

    def test_cb02_correo_vacio_o_con_espacios(self):
        self.assertRechaza("   ", "Clave123!", "Debe ingresar su correo y contraseña.")

    def test_cb03_clave_que_no_es_texto(self):
        self.assertRechaza("a@b.com", None, "Debe ingresar su correo y contraseña.")

    def test_cb04_clave_vacia(self):
        self.assertRechaza("a@b.com", "", "Debe ingresar su correo y contraseña.")

    def test_cb05_correo_con_formato_invalido(self):
        self.assertRechaza("correo-sin-arroba", "Clave123!", "El formato del correo no es válido.")

    def test_cb06_datos_validos(self):
        self.assertIsNone(self.proveedor._validar("a@b.com", "Clave123!"))


class InicioSesionEndpointTests(TestCase):
    def setUp(self):
        cuenta = CuentaUsuario(correo="mathias@correo.com")
        cuenta.definir_clave("Kyzen2026")
        cuenta.save()

    def login(self, correo, clave):
        return self.client.post(
            "/api/login", json.dumps({"correo": correo, "clave": clave}), content_type="application/json"
        )

    def test_login_correcto_entrega_un_token(self):
        respuesta = self.login("mathias@correo.com", "Kyzen2026")
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()["token"])

    def test_el_correo_no_distingue_mayusculas_ni_espacios(self):
        self.assertEqual(self.login("  MATHIAS@correo.com ", "Kyzen2026").status_code, 200)

    def test_clave_incorrecta_responde_401(self):
        self.assertEqual(self.login("mathias@correo.com", "otra-clave").status_code, 401)

    def test_correo_con_formato_invalido_responde_401(self):
        self.assertEqual(self.login("mathias-correo.com", "Kyzen2026").status_code, 401)
