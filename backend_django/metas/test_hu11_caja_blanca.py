import os
from decimal import Decimal

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario

from .models import MetaAhorro
from .RepositorioMetas import RepositorioMetas
from .ServicioMetas import ServicioMetas

REPORTE = os.environ.get("KYZEN_REPORTE") == "1"

ERR_NOMBRE = "ValueError: Escribe un nombre para la meta."
ERR_LARGO = "ValueError: El nombre no puede superar los 120 caracteres."
ERR_DUPLICADO = "ValueError: Ya tienes una meta con ese nombre. Elige un título diferente."
ERR_MONTO = "ValueError: El monto objetivo debe ser mayor que cero."


def mostrar(camino, entrada, esperado, obtenido):
    if REPORTE:
        print(f"REPORTE|{camino}|{entrada}|{esperado}|{obtenido}")


class CrearMetaCajaBlancaTests(TestCase):
    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(correo="joaquin@correo.com", clave_hash="x")
        self.repo = RepositorioMetas()
        self.servicio = ServicioMetas(self.repo)
        self.repo.crear(self.cuenta, "Viaje", 1000)

    def _intentar(self, camino, entrada, nombre, objetivo, esperado):
        try:
            meta = self.servicio.crear(self.cuenta, nombre, objetivo)
            obtenido = f"OK nombre={meta.nombre}"
        except ValueError as error:
            obtenido = f"ValueError: {error}"
        mostrar(camino, entrada, esperado, obtenido)
        return obtenido

    def test_c1_nombre_none(self):
        self.assertEqual(self._intentar("C1", "nombre=None", None, "100", ERR_NOMBRE), ERR_NOMBRE)

    def test_c2_nombre_solo_espacios(self):
        self.assertEqual(self._intentar("C2", "nombre='   '", "   ", "100", ERR_NOMBRE), ERR_NOMBRE)

    def test_c3_nombre_de_121_caracteres(self):
        self.assertEqual(self._intentar("C3", "nombre='a'*121", "a" * 121, "100", ERR_LARGO), ERR_LARGO)

    def test_c4_nombre_repetido(self):
        self.assertEqual(self._intentar("C4", "nombre='viaje'", "viaje", "100", ERR_DUPLICADO), ERR_DUPLICADO)

    def test_c5_objetivo_no_numerico(self):
        self.assertEqual(self._intentar("C5", "objetivo='abc'", "Casa", "abc", ERR_MONTO), ERR_MONTO)

    def test_c6_objetivo_no_finito(self):
        self.assertEqual(self._intentar("C6", "objetivo='NaN'", "Casa", "NaN", ERR_MONTO), ERR_MONTO)

    def test_c7_objetivo_cero(self):
        self.assertEqual(self._intentar("C7", "objetivo='0'", "Casa", "0", ERR_MONTO), ERR_MONTO)

    def test_c8_meta_valida(self):
        obtenido = self._intentar("C8", "'Fondo', '2500.00'", "Fondo", "2500.00", "OK nombre=Fondo")
        self.assertEqual(obtenido, "OK nombre=Fondo")
        meta = MetaAhorro.objects.get(usuario=self.cuenta, nombre="Fondo")
        self.assertEqual(meta.objetivo_pen, Decimal("2500.00"))
        self.assertEqual(meta.total_abonado_pen, Decimal("0"))

    def test_limite_120_caracteres_es_valido(self):
        nombre = "b" * 120
        obtenido = self._intentar("L1", "nombre='b'*120", nombre, "100", f"OK nombre={nombre}")
        self.assertEqual(obtenido, f"OK nombre={nombre}")
