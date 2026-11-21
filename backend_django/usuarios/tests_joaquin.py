from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone
from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento
from metas.RepositorioMetas import RepositorioMetas
from metas.ServicioMetas import ServicioMetas
from metas.models import MetaAhorro
from reportes.ConstructorReporte import ConstructorReporte
from reportes.ExportadorPdfGraficos import ExportadorPdfGraficos
from .CodigoCambioClave import CodigoCambioClave
from .CuentaUsuario import CuentaUsuario
from .RepositorioCodigosCambioClaveDjango import RepositorioCodigosCambioClaveDjango
from .ServicioCambioClave import ServicioCambioClave


def crear_cuenta(correo):
    cuenta = CuentaUsuario(correo=correo, clave_hash="")
    cuenta.definir_clave("ClaveInicial123")
    cuenta.save()
    return cuenta


class JoaquinCajaBlancaCambioClaveTests(TestCase):

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
        datos = {
            "cuenta": self.cuenta,
            "codigo_hash": make_password("ABC123"),
            "expira_en": timezone.now() + timedelta(minutes=10),
            "intentos": 0,
            "usado": False,
        }
        datos.update(cambios)
        return CodigoCambioClave.objects.create(**datos)

    def test_cb01_correo_no_registrado(self):
        self.repositorio.buscar_por_correo.return_value = None
        with self.assertRaisesMessage(ValueError, "No existe una cuenta"):
            self.servicio.cambiar_clave("nadie@example.com", "ABC123", "NuevaClave123", "NuevaClave123")

    def test_cb02_solicitud_inexistente_o_usada(self):
        with self.assertRaisesMessage(ValueError, "El código expiró"):
            self.servicio.cambiar_clave(self.cuenta.correo, "ABC123", "NuevaClave123", "NuevaClave123")

    def test_cb03_codigo_expirado(self):
        self.crear_solicitud(expira_en=timezone.now() - timedelta(seconds=1))
        with self.assertRaisesMessage(ValueError, "El código expiró"):
            self.servicio.cambiar_clave(self.cuenta.correo, "ABC123", "NuevaClave123", "NuevaClave123")

    def test_cb04_quinto_intento_superado(self):
        self.crear_solicitud(intentos=5)
        with self.assertRaisesMessage(ValueError, "límite de intentos"):
            self.servicio.cambiar_clave(self.cuenta.correo, "ABC123", "NuevaClave123", "NuevaClave123")

    @patch("usuarios.ServicioCambioClave.check_password", return_value=False)
    def test_cb05_codigo_incorrecto_incrementa_intentos(self, check_password_mock):
        solicitud = self.crear_solicitud()
        with self.assertRaisesMessage(ValueError, "El código no es correcto"):
            self.servicio.cambiar_clave(self.cuenta.correo, "INCORRECTO", "NuevaClave123", "NuevaClave123")
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.intentos, 1)
        check_password_mock.assert_called_once()

    @patch("usuarios.ServicioCambioClave.check_password", return_value=True)
    def test_cb06_clave_demasiado_corta(self, check_password_mock):
        self.crear_solicitud()
        with self.assertRaisesMessage(ValueError, "al menos 8 caracteres"):
            self.servicio.cambiar_clave(self.cuenta.correo, "ABC123", "corta", "corta")
        check_password_mock.assert_called_once()

    def test_cb07_cambio_valido(self):
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
        self.assertTrue(self.cuenta.verificar_clave("NuevaClave123"))

    @patch("usuarios.ServicioCambioClave.check_password", return_value=True)
    def test_cb08_confirmacion_diferente(self, check_password_mock):
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
        check_password_mock.assert_called_once()


class JoaquinCajaNegraCambioClaveTests(TestCase):

    def test_cn01_json_malformado(self):
        respuesta = self.client.post("/api/cambiar-clave", data="{", content_type="application/json")
        self.assertEqual(respuesta.status_code, 400)

    def test_cn02_correo_no_registrado(self):
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": "noexiste@ulima.edu.pe",
                "codigo": "123456",
                "nueva_clave": "Clave1234",
                "confirmacion_clave": "Clave1234",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    @patch("usuarios.ServicioCambioClave.check_password", return_value=False)
    def test_cn03_codigo_incorrecto(self, check_password_mock):
        cuenta = crear_cuenta("negra3@example.com")
        CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=0,
        )
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": cuenta.correo,
                "codigo": "999999",
                "nueva_clave": "Clave1234",
                "confirmacion_clave": "Clave1234",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)
        check_password_mock.assert_called_once()

    def test_cn04_codigo_expirado(self):
        cuenta = crear_cuenta("negra4@example.com")
        CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() - timedelta(minutes=1),
            intentos=0,
        )
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": cuenta.correo,
                "codigo": "123456",
                "nueva_clave": "Clave1234",
                "confirmacion_clave": "Clave1234",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_cn05_quinto_intento_fallido(self):
        cuenta = crear_cuenta("negra5@example.com")
        CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=5,
        )
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": cuenta.correo,
                "codigo": "000000",
                "nueva_clave": "Clave1234",
                "confirmacion_clave": "Clave1234",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_cn06_clave_de_siete_caracteres(self):
        cuenta = crear_cuenta("negra6@example.com")
        CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=0,
        )
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": cuenta.correo,
                "codigo": "123456",
                "nueva_clave": "1234567",
                "confirmacion_clave": "1234567",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    @patch("usuarios.ServicioCambioClave.check_password", return_value=True)
    def test_cn07_clave_de_ocho_caracteres(self, check_password_mock):
        cuenta = crear_cuenta("negra7@example.com")
        CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=0,
        )
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": cuenta.correo,
                "codigo": "123456",
                "nueva_clave": "12345678",
                "confirmacion_clave": "12345678",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 200)
        check_password_mock.assert_called_once()

    def test_cn08_confirmacion_no_coincide(self):
        cuenta = crear_cuenta("negra8@example.com")
        CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=0,
        )
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={
                "accion": "cambiar",
                "correo": cuenta.correo,
                "codigo": "123456",
                "nueva_clave": "Clave1234",
                "confirmacion_clave": "Clave5678",
            },
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    @patch("usuarios.ServicioCambioClave.ServicioCambioClave.generar_codigo", return_value=True)
    def test_cn09_generacion_de_codigo(self, generar_codigo_mock):
        respuesta = self.client.post(
            "/api/cambiar-clave",
            data={"accion": "generar", "correo": "joaquin@example.com"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 200)
        generar_codigo_mock.assert_called_once_with("joaquin@example.com")


class JoaquinPruebasUnitariasMetasPersistenciaTests(TestCase):

    def setUp(self):
        self.cuenta = crear_cuenta("joaquin@example.com")
        self.otra_cuenta = crear_cuenta("otra@example.com")
        self.servicio = ServicioMetas(RepositorioMetas())

    def test_codigo_cambio_clave_expira_a_diez_minutos(self):
        solicitud = CodigoCambioClave.objects.create(
            cuenta=self.cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=0,
        )
        diferencia = solicitud.expira_en - timezone.now()
        self.assertGreater(diferencia, timedelta(minutes=9, seconds=59))
        self.assertLessEqual(diferencia, timedelta(minutes=10))

    def test_cinco_intentos_bloquean_codigo(self):
        solicitud = CodigoCambioClave.objects.create(
            cuenta=self.cuenta,
            codigo_hash=make_password("123456"),
            expira_en=timezone.now() + timedelta(minutes=10),
            intentos=5,
        )
        self.assertGreaterEqual(solicitud.intentos, 5)

    def test_codigo_se_almacena_como_hash(self):
        codigo_hash = make_password("123456")
        solicitud = CodigoCambioClave.objects.create(
            cuenta=self.cuenta,
            codigo_hash=codigo_hash,
            expira_en=timezone.now() + timedelta(minutes=10),
        )
        self.assertNotEqual(solicitud.codigo_hash, "123456")
        self.assertTrue(codigo_hash.startswith("pbkdf2_sha256$"))

    def test_hu11_nombre_duplicado_se_valida_por_usuario(self):
        self.servicio.crear(self.cuenta, "Viaje", "1000")
        with self.assertRaisesMessage(ValueError, "Ya tienes una meta"):
            self.servicio.crear(self.cuenta, "viaje", "1500")
        self.servicio.crear(self.otra_cuenta, "viaje", "1500")
        self.assertEqual(MetaAhorro.objects.filter(nombre__iexact="viaje").count(), 2)

    def test_meta_de_otra_cuenta_no_se_puede_modificar(self):
        meta = self.servicio.crear(self.cuenta, "Ahorro privado", "1000")
        with self.assertRaisesMessage(ValueError, "La meta no existe"):
            self.servicio.abonar(self.otra_cuenta, meta.id, "100")
        meta.refresh_from_db()
        self.assertEqual(meta.total_abonado_pen, Decimal("0.00"))


class JoaquinPruebasUnitariasExportacionPdfTests(TestCase):

    def setUp(self):
        self.cuenta = crear_cuenta("joaquin-reporte@example.com")

    def test_exportacion_pdf_genera_encabezado_valido(self):
        movimiento = Movimiento.objects.create(
            usuario=self.cuenta,
            tipo=TipoMovimiento.INGRESO,
            monto=Decimal("1000.00"),
            fecha=date(2026, 10, 1),
            descripcion="Ingreso mensual",
            categoria="otros",
            moneda="PEN",
        )
        reporte = (
            ConstructorReporte([movimiento], {"otros": "Otros"})
            .con_gastos_por_categoria()
            .con_evolucion_mensual()
            .con_movimientos()
            .construir()
        )

        pdf = ExportadorPdfGraficos().exportar(reporte)

        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
        self.assertGreaterEqual(len(pdf), 1000)
