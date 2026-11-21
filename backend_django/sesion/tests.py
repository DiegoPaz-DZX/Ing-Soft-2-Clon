from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango

from .AutenticacionPorCuenta import AutenticacionPorCuenta
from .CredencialesInvalidasException import CredencialesInvalidasException
from .EstrategiaAutenticacion import EstrategiaAutenticacion
from .ProveedorAutenticacion import ProveedorAutenticacion


def crear_cuenta(correo, clave):
    cuenta = CuentaUsuario(correo=correo)
    cuenta.definir_clave(clave)
    cuenta.save()
    return cuenta


class AutenticacionEnMemoria(EstrategiaAutenticacion):
    def __init__(self, cuentas):
        self._cuentas = cuentas

    def autenticar(self, correo, clave):
        cuenta, clave_guardada = self._cuentas.get(correo, (None, None))
        return cuenta if clave == clave_guardada else None


class ProveedorAutenticacionTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta("mathias@correo.com", "Kyzen2026")
        self.proveedor = ProveedorAutenticacion(AutenticacionPorCuenta(RepositorioCuentasDjango()))

    def test_inicia_sesion_con_correo_y_clave_correctos(self):
        self.assertEqual(self.proveedor.iniciar_sesion("mathias@correo.com", "Kyzen2026"), self.cuenta)

    def test_el_correo_no_distingue_mayusculas_ni_espacios(self):
        self.assertEqual(self.proveedor.iniciar_sesion("  MATHIAS@correo.com ", "Kyzen2026"), self.cuenta)

    def test_rechaza_datos_incorrectos(self):
        casos = [
            ("mathias@correo.com", "otra-clave"),
            ("nadie@correo.com", "Kyzen2026"),
            ("correo-malo", "Kyzen2026"),
            ("", ""),
            (None, None),
        ]
        for datos in casos:
            with self.subTest(datos=datos):
                with self.assertRaises(CredencialesInvalidasException):
                    self.proveedor.iniciar_sesion(*datos)

    def test_cambia_de_estrategia_en_tiempo_de_ejecucion(self):
        self.proveedor.cambiar_estrategia(
            AutenticacionEnMemoria({"mathias@correo.com": (self.cuenta, "memoria1")})
        )
        self.assertEqual(self.proveedor.iniciar_sesion("mathias@correo.com", "memoria1"), self.cuenta)
        with self.assertRaises(CredencialesInvalidasException):
            self.proveedor.iniciar_sesion("mathias@correo.com", "Kyzen2026")


class LoginEndpointTests(TestCase):
    def login(self, correo, clave):
        return self.client.post(
            "/api/login", data={"correo": correo, "clave": clave}, content_type="application/json"
        )

    def test_inicia_sesion_con_una_cuenta_creada_en_el_registro(self):
        self.client.post(
            "/api/registro",
            data={"correo": "mathias@correo.com", "clave": "Kyzen2026", "confirmacion": "Kyzen2026"},
            content_type="application/json",
        )
        respuesta = self.login("mathias@correo.com", "Kyzen2026")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["correo"], "mathias@correo.com")
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_clave_incorrecta_responde_401_con_mensaje_generico(self):
        crear_cuenta("mathias@correo.com", "Kyzen2026")
        respuesta = self.login("mathias@correo.com", "otra-clave")
        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(respuesta.json()["error"], "Correo o contraseña incorrectos.")
        otra = self.login("nadie@correo.com", "Kyzen2026")
        self.assertEqual(otra.json()["error"], "Correo o contraseña incorrectos.")

    def test_campos_vacios_y_metodos_no_permitidos(self):
        self.assertEqual(self.login("", "").json()["error"], "Debe ingresar su correo y contraseña.")
        self.assertEqual(self.client.get("/api/login").status_code, 405)
