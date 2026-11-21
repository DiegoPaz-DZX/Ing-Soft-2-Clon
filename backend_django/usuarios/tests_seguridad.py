from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth.hashers import make_password
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento

from .CuentaUsuario import CuentaUsuario
from .CodigoCambioClave import CodigoCambioClave
from .PermisoDenegadoException import PermisoDenegadoException
from .RepositorioCuentasDjango import RepositorioCuentasDjango
from .RepositorioCodigosCambioClaveDjango import RepositorioCodigosCambioClaveDjango
from .RolUsuario import RolUsuario
from .ServicioAdministracionUsuarios import ServicioAdministracionUsuarios
from .ServicioTokens import ServicioTokens
from .ServicioCambioClave import ServicioCambioClave


def crear_cuenta(correo, rol=RolUsuario.USUARIO):
    cuenta = CuentaUsuario(correo=correo, rol=rol)
    cuenta.definir_clave("Kyzen2026")
    cuenta.save()
    return cuenta


class CifradoMovimientosTests(TestCase):
    def test_la_descripcion_se_guarda_cifrada_y_se_recupera_normal(self):
        movimiento = Movimiento.objects.create(
            tipo=TipoMovimiento.GASTO,
            monto=Decimal("24.50"),
            fecha="2026-11-02",
            descripcion="Compra personal",
            categoria="otros",
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT descripcion FROM balance_movimiento WHERE id = %s", [movimiento.pk])
            valor_guardado = cursor.fetchone()[0]

        self.assertNotEqual(valor_guardado, "Compra personal")
        self.assertTrue(valor_guardado.startswith("kyzen:cifrado:"))
        self.assertEqual(Movimiento.objects.get(pk=movimiento.pk).descripcion, "Compra personal")


class ServicioCambioClaveWhiteBoxTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta("joaquin@example.com")
        self.repositorio = Mock()
        self.repositorio.buscar_por_correo.return_value = self.cuenta
        self.servicio = ServicioCambioClave(
            self.repositorio,
            RepositorioCodigosCambioClaveDjango(),
            Mock(),
        )

    def crear_solicitud(self, **cambios):
        valores = {
            "cuenta": self.cuenta,
            "codigo_hash": make_password("ABC123"),
            "expira_en": timezone.now() + timedelta(minutes=10),
            "intentos": 0,
            "usado": False,
        }
        valores.update(cambios)
        return CodigoCambioClave.objects.create(**valores)

    def test_cb01_rechaza_correo_no_registrado(self):
        self.repositorio.buscar_por_correo.return_value = None

        with self.assertRaisesMessage(ValueError, "No existe una cuenta"):
            self.servicio.cambiar_clave(
                "no-existe@example.com", "ABC123", "NuevaClave123", "NuevaClave123"
            )

    def test_cb02_rechaza_solicitud_inexistente_o_usada(self):
        with self.assertRaisesMessage(ValueError, "El código expiró"):
            self.servicio.cambiar_clave(
                self.cuenta.correo, "ABC123", "NuevaClave123", "NuevaClave123"
            )

    def test_cb03_rechaza_codigo_expirado(self):
        self.crear_solicitud(expira_en=timezone.now() - timedelta(seconds=1))

        with self.assertRaisesMessage(ValueError, "El código expiró"):
            self.servicio.cambiar_clave(
                self.cuenta.correo, "ABC123", "NuevaClave123", "NuevaClave123"
            )

    def test_cb04_bloquea_quinto_intento_superado(self):
        self.crear_solicitud(intentos=5)

        with self.assertRaisesMessage(ValueError, "límite de intentos"):
            self.servicio.cambiar_clave(
                self.cuenta.correo, "ABC123", "NuevaClave123", "NuevaClave123"
            )

    @patch("usuarios.ServicioCambioClave.check_password", return_value=False)
    def test_cb05_rechaza_codigo_incorrecto(self, check_password_mock):
        solicitud = self.crear_solicitud()

        with self.assertRaisesMessage(ValueError, "El código no es correcto"):
            self.servicio.cambiar_clave(
                self.cuenta.correo, "INCORRECTO", "NuevaClave123", "NuevaClave123"
            )

        solicitud.refresh_from_db()
        self.assertEqual(solicitud.intentos, 1)
        check_password_mock.assert_called_once()

    @patch("usuarios.ServicioCambioClave.check_password", return_value=True)
    def test_cb06_rechaza_clave_demasiado_corta(self, check_password_mock):
        self.crear_solicitud()

        with self.assertRaisesMessage(ValueError, "al menos 8 caracteres"):
            self.servicio.cambiar_clave(
                self.cuenta.correo, "ABC123", "corta", "corta"
            )

    def test_cb07_cambia_clave_y_usa_codigo(self):
        solicitud = self.crear_solicitud()

        self.servicio.cambiar_clave(
            self.cuenta.correo,
            "ABC123",
            "NuevaClave123",
            "NuevaClave123",
        )

        solicitud.refresh_from_db()
        self.cuenta.refresh_from_db()
        self.assertTrue(solicitud.usado)
        self.assertEqual(solicitud.intentos, 1)
        self.assertTrue(self.cuenta.verificar_clave("NuevaClave123"))

    @patch("usuarios.ServicioCambioClave.check_password", return_value=True)
    def test_cb08_rechaza_confirmacion_de_clave_diferente(self, check_password_mock):
        self.crear_solicitud()

        with self.assertRaisesMessage(ValueError, "no coinciden"):
            self.servicio.cambiar_clave(
                self.cuenta.correo,
                "ABC123",
                "NuevaClave123",
                "OtraClave123",
            )

        self.cuenta.refresh_from_db()
        self.assertFalse(self.cuenta.verificar_clave("NuevaClave123"))


class CambioClaveEndpointBlackBoxTests(TestCase):
    def test_rechaza_cuerpo_json_invalido(self):
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data="{",
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_rechaza_codigo_con_correo_no_registrado(self):
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": "no-existe@example.com",
                "codigo": "ABC123",
                "nueva_clave": "NuevaClave123",
                "confirmacion_clave": "NuevaClave123",
            },
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_rechaza_cambio_cuando_se_superan_cinco_intentos(self):
        cuenta = crear_cuenta("limite@example.com")
        CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=make_password("ABC123"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=5,
        )

        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": cuenta.correo,
                "codigo": "ABC123",
                "nueva_clave": "NuevaClave123",
            },
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)


class ServicioAdministracionUsuariosTests(TestCase):
    def setUp(self):
        self.repositorio = RepositorioCuentasDjango()
        self.tokens = ServicioTokens(self.repositorio)
        self.servicio = ServicioAdministracionUsuarios(self.repositorio, self.tokens)
        self.admin = crear_cuenta("admin@kyzen.local", RolUsuario.ADMINISTRADOR)
        self.usuario = crear_cuenta("edu@correo.com")

    def test_administrador_lista_y_cambia_roles(self):
        token = self.tokens.crear(self.admin)
        self.assertEqual(len(self.servicio.listar_usuarios(token)), 2)

        actualizado = self.servicio.cambiar_rol(
            token, self.usuario.pk, RolUsuario.ADMINISTRADOR
        )
        self.assertEqual(actualizado.rol, RolUsuario.ADMINISTRADOR)

    def test_usuario_normal_no_puede_administrar(self):
        token = self.tokens.crear(self.usuario)
        with self.assertRaises(PermisoDenegadoException):
            self.servicio.listar_usuarios(token)

    def test_administrador_no_puede_quitarse_su_propio_rol(self):
        token = self.tokens.crear(self.admin)
        with self.assertRaises(PermisoDenegadoException):
            self.servicio.cambiar_rol(token, self.admin.pk, RolUsuario.USUARIO)


class AdministracionEndpointTests(TestCase):
    def setUp(self):
        self.admin = crear_cuenta("admin@kyzen.local", RolUsuario.ADMINISTRADOR)
        self.usuario = crear_cuenta("edu@correo.com")
        self.token_admin = ServicioTokens(RepositorioCuentasDjango()).crear(self.admin)

    def test_login_devuelve_rol_y_token(self):
        respuesta = self.client.post(
            "/api/login",
            data={"correo": "admin@kyzen.local", "clave": "Kyzen2026"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["rol"], RolUsuario.ADMINISTRADOR)
        self.assertTrue(respuesta.json()["token"])

    def test_endpoint_admin_lista_y_actualiza(self):
        cabecera = {"HTTP_AUTHORIZATION": f"Bearer {self.token_admin}"}
        listado = self.client.get("/api/admin/usuarios", **cabecera)
        self.assertEqual(listado.status_code, 200)
        self.assertEqual(len(listado.json()["usuarios"]), 2)

        respuesta = self.client.put(
            f"/api/admin/usuarios/{self.usuario.pk}/rol",
            data={"rol": RolUsuario.ADMINISTRADOR},
            content_type="application/json",
            **cabecera,
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["rol"], RolUsuario.ADMINISTRADOR)

    def test_endpoint_rechaza_sesion_sin_permisos(self):
        token_usuario = ServicioTokens(RepositorioCuentasDjango()).crear(self.usuario)
        respuesta = self.client.get(
            "/api/admin/usuarios", HTTP_AUTHORIZATION=f"Bearer {token_usuario}"
        )
        self.assertEqual(respuesta.status_code, 403)
