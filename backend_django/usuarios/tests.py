from django.test import TestCase

from .CorreoRegistradoException import CorreoRegistradoException
from .DatosRegistroInvalidosException import DatosRegistroInvalidosException
from .RepositorioCuentasDjango import RepositorioCuentasDjango
from .ServicioRegistro import ServicioRegistro


class ServicioRegistroTests(TestCase):
    def setUp(self):
        self.servicio = ServicioRegistro(RepositorioCuentasDjango())

    def test_guarda_el_correo_normalizado_y_la_clave_como_hash(self):
        cuenta = self.servicio.registrar(" EDU@Correo.com ", "Kyzen2026", "Kyzen2026")
        self.assertEqual(cuenta.correo, "edu@correo.com")
        self.assertNotEqual(cuenta.clave_hash, "Kyzen2026")
        self.assertTrue(cuenta.verificar_clave("Kyzen2026"))

    def test_no_permite_correos_repetidos(self):
        self.servicio.registrar("edu@correo.com", "Kyzen2026", "Kyzen2026")
        with self.assertRaises(CorreoRegistradoException):
            self.servicio.registrar("EDU@correo.com", "Kyzen2026", "Kyzen2026")

    def test_valida_correo_clave_y_confirmacion(self):
        casos = [
            ("correo-malo", "Kyzen2026", "Kyzen2026"),
            ("edu@correo.com", "123", "123"),
            ("edu@correo.com", "Kyzen2026", "otra-clave"),
        ]
        for datos in casos:
            with self.subTest(datos=datos):
                with self.assertRaises(DatosRegistroInvalidosException):
                    self.servicio.registrar(*datos)


class RegistroEndpointTests(TestCase):
    def test_registra_una_cuenta(self):
        respuesta = self.client.post(
            "/api/registro",
            data={
                "correo": "edu@correo.com",
                "clave": "Kyzen2026",
                "confirmacion": "Kyzen2026",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()["correo"], "edu@correo.com")
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_responde_409_si_el_correo_ya_existe(self):
        datos = {
            "correo": "edu@correo.com",
            "clave": "Kyzen2026",
            "confirmacion": "Kyzen2026",
        }
        self.client.post("/api/registro", data=datos, content_type="application/json")
        respuesta = self.client.post("/api/registro", data=datos, content_type="application/json")
        self.assertEqual(respuesta.status_code, 409)

    def test_rechaza_datos_invalidos_y_metodos_no_permitidos(self):
        respuesta = self.client.post(
            "/api/registro",
            data={"correo": "mal", "clave": "123", "confirmacion": "456"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(self.client.get("/api/registro").status_code, 405)
