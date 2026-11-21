from decimal import Decimal

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario

from .models import MetaAhorro
from .RepositorioMetas import RepositorioMetas
from .ServicioMetas import ServicioMetas


class ServicioMetasTests(TestCase):
    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(
            correo="joaquin@example.com",
            clave_hash="hash-inicial",
        )
        self.otra = CuentaUsuario.objects.create(
            correo="otra@example.com",
            clave_hash="hash-inicial",
        )
        self.servicio = ServicioMetas(RepositorioMetas())

    def test_crear_meta_asigna_usuario_correctamente(self):
        meta = self.servicio.crear(
            self.cuenta,
            "Fondo de emergencia",
            "2500.00",
        )

        self.assertEqual(meta.usuario_id, self.cuenta.id)
        self.assertEqual(meta.objetivo_pen, Decimal("2500.00"))
        self.assertEqual(meta.total_abonado_pen, Decimal("0.00"))

    def test_no_permite_nombre_repetido_para_el_mismo_usuario(self):
        self.servicio.crear(self.cuenta, "Viaje", "1000")

        with self.assertRaisesMessage(ValueError, "Ya tienes una meta"):
            self.servicio.crear(self.cuenta, "viaje", "1500")

    def test_permite_el_mismo_nombre_en_otro_usuario(self):
        self.servicio.crear(self.cuenta, "Viaje", "1000")
        self.servicio.crear(self.otra, "viaje", "1500")

        self.assertEqual(MetaAhorro.objects.filter(nombre__iexact="viaje").count(), 2)

    def test_el_nombre_se_guarda_sin_espacios_laterales(self):
        meta = self.servicio.crear(self.cuenta, "  Viaje  ", "100")

        self.assertEqual(meta.nombre, "Viaje")

    def test_rechaza_nombre_de_mas_de_120_caracteres(self):
        with self.assertRaisesMessage(ValueError, "120 caracteres"):
            self.servicio.crear(self.cuenta, "a" * 121, "100")

    def test_rechaza_montos_invalidos(self):
        for valor in ("0", "-5", "abc", None, "NaN", "Infinity"):
            with self.subTest(valor=valor):
                with self.assertRaisesMessage(ValueError, "mayor que cero"):
                    self.servicio.crear(self.cuenta, "Casa", valor)

        self.assertEqual(MetaAhorro.objects.count(), 0)
