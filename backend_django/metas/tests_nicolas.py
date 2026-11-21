"""Caja blanca de ServicioMetas.renombrar (HU25). V(G) = 7 -> 7 caminos básicos independientes.

Decisiones del método (cada `or`/`and`/`if` suma 1):
  D1  nombre or ""                      (operador or)
  D2  if not nombre
  D3  if len(nombre) > 120
  D4  if meta is None
  D5  if (meta.nombre.casefold() != nombre.casefold() and existe_nombre(...))  -> if
  D6                                                                          -> operador and
V(G) = 6 decisiones + 1 = 7.
"""
import os

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario

from .RepositorioMetas import RepositorioMetas
from .ServicioMetas import ServicioMetas

REPORTE = os.environ.get("KYZEN_REPORTE") == "1"


def mostrar(camino, entrada, esperado, obtenido):
    if REPORTE:
        print(f"REPORTE|{camino}|{entrada}|{esperado}|{obtenido}")


class RenombrarMetaCajaBlancaTests(TestCase):
    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(correo="nico@correo.com", clave_hash="x")
        self.otra = CuentaUsuario.objects.create(correo="otra@correo.com", clave_hash="x")
        self.repo = RepositorioMetas()
        self.servicio = ServicioMetas(self.repo)
        self.viaje = self.repo.crear(self.cuenta, "Viaje", 1000)
        self.laptop = self.repo.crear(self.cuenta, "Laptop", 3000)

    def _intentar(self, camino, entrada, meta_id, nombre, esperado):
        try:
            resultado = self.servicio.renombrar(self.cuenta, meta_id, nombre)
            obtenido = f"OK nombre={resultado.nombre}"
        except ValueError as error:
            obtenido = f"ValueError: {error}"
        mostrar(camino, entrada, esperado, obtenido)
        return obtenido

    # C1: nombre None -> la rama derecha del `or` (""), D2 verdadera
    def test_c1_nombre_none(self):
        obtenido = self._intentar("C1", "nombre=None", self.viaje.pk, None, "ValueError: Escribe un nombre para la meta.")
        self.assertEqual(obtenido, "ValueError: Escribe un nombre para la meta.")

    # C2: nombre solo espacios -> rama izquierda del `or`, D2 verdadera tras strip()
    def test_c2_nombre_solo_espacios(self):
        obtenido = self._intentar("C2", "nombre='   '", self.viaje.pk, "   ", "ValueError: Escribe un nombre para la meta.")
        self.assertEqual(obtenido, "ValueError: Escribe un nombre para la meta.")

    # C3: D2 falsa, D3 verdadera
    def test_c3_nombre_de_121_caracteres(self):
        obtenido = self._intentar("C3", "nombre='a'*121", self.viaje.pk, "a" * 121,
                                  "ValueError: El nombre no puede superar los 120 caracteres.")
        self.assertEqual(obtenido, "ValueError: El nombre no puede superar los 120 caracteres.")

    # C4: D3 falsa, D4 verdadera (meta inexistente o de otra cuenta)
    def test_c4_meta_inexistente(self):
        obtenido = self._intentar("C4", "meta_id=9999, nombre='Casa'", 9999, "Casa", "ValueError: La meta no existe.")
        self.assertEqual(obtenido, "ValueError: La meta no existe.")

    def test_c4b_meta_de_otra_cuenta(self):
        ajena = self.repo.crear(self.otra, "Ajena", 100)
        obtenido = self._intentar("C4b", "meta de otra cuenta", ajena.pk, "Casa", "ValueError: La meta no existe.")
        self.assertEqual(obtenido, "ValueError: La meta no existe.")

    # C5: D5 falsa por el primer operando del `and` (mismo nombre, otra capitalización): no consulta duplicados
    def test_c5_mismo_nombre_distinta_capitalizacion(self):
        obtenido = self._intentar("C5", "'Viaje' -> 'VIAJE'", self.viaje.pk, "VIAJE", "OK nombre=VIAJE")
        self.assertEqual(obtenido, "OK nombre=VIAJE")

    # C6: primer operando verdadero y segundo verdadero -> duplicado
    def test_c6_nombre_repetido_en_otra_meta(self):
        obtenido = self._intentar("C6", "'Viaje' -> 'laptop'", self.viaje.pk, "laptop",
                                  "ValueError: Ya tienes una meta con ese nombre. Elige un título diferente.")
        self.assertEqual(obtenido, "ValueError: Ya tienes una meta con ese nombre. Elige un título diferente.")

    # C7: primer operando verdadero y segundo falso -> se actualiza
    def test_c7_nombre_nuevo_libre(self):
        obtenido = self._intentar("C7", "'Viaje' -> 'Casa propia'", self.viaje.pk, "Casa propia", "OK nombre=Casa propia")
        self.assertEqual(obtenido, "OK nombre=Casa propia")
        self.viaje.refresh_from_db()
        self.assertEqual(self.viaje.nombre, "Casa propia")

    # Valor límite adicional: 120 caracteres exactos es válido
    def test_limite_120_caracteres_es_valido(self):
        nombre = "b" * 120
        obtenido = self._intentar("L1", "nombre='b'*120", self.viaje.pk, nombre, f"OK nombre={nombre}")
        self.assertEqual(obtenido, f"OK nombre={nombre}")
