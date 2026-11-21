from datetime import date
from decimal import Decimal

from django.test import TestCase

from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento
from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .FiltroPorRangoFechas import FiltroPorRangoFechas
from .HistorialMovimientos import HistorialMovimientos
from .RangoFechasInvalidoException import RangoFechasInvalidoException
from .RepositorioHistorial import RepositorioHistorial
from .RepositorioHistorialDjango import RepositorioHistorialDjango


def crear_cuenta(correo="ana@correo.com"):
    return CuentaUsuario.objects.create(correo=correo, clave_hash="x")


def crear(descripcion, fecha, monto="100", tipo=TipoMovimiento.GASTO, cuenta=None):
    return Movimiento.objects.create(
        tipo=tipo, monto=Decimal(monto), fecha=fecha, descripcion=descripcion, usuario=cuenta
    )


class FiltroPorRangoFechasTests(TestCase):
    def test_rechaza_fechas_vacias(self):
        with self.assertRaises(RangoFechasInvalidoException):
            FiltroPorRangoFechas(None, date(2026, 6, 30))

    def test_rechaza_rango_invertido(self):
        with self.assertRaises(RangoFechasInvalidoException):
            FiltroPorRangoFechas(date(2026, 6, 10), date(2026, 6, 1))


class HistorialMovimientosTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()
        crear("Salario", date(2026, 6, 1), "3000", TipoMovimiento.INGRESO, self.cuenta)
        crear("Luz", date(2026, 6, 10), cuenta=self.cuenta)
        crear("Cursos", date(2026, 7, 3), cuenta=self.cuenta)
        crear("Ajeno", date(2026, 6, 5), cuenta=crear_cuenta("luis@correo.com"))
        self.historial = HistorialMovimientos(RepositorioHistorialDjango())

    def test_sin_filtro_devuelve_todos_ordenados_por_fecha(self):
        descripciones = [m.descripcion for m in self.historial.obtener_movimientos(self.cuenta)]
        self.assertEqual(descripciones, ["Cursos", "Luz", "Salario"])

    def test_incluye_las_dos_fechas_del_rango(self):
        filtro = FiltroPorRangoFechas(date(2026, 6, 1), date(2026, 6, 10))
        descripciones = [m.descripcion for m in self.historial.obtener_movimientos(self.cuenta, filtro)]
        self.assertEqual(descripciones, ["Luz", "Salario"])

    def test_rango_sin_movimientos(self):
        filtro = FiltroPorRangoFechas(date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(self.historial.obtener_movimientos(self.cuenta, filtro), [])


    def test_un_filtro_no_afecta_a_la_siguiente_consulta(self):
        filtro = FiltroPorRangoFechas(date(2026, 1, 1), date(2026, 1, 31))
        self.historial.obtener_movimientos(self.cuenta, filtro)
        self.assertEqual(len(self.historial.obtener_movimientos(self.cuenta)), 3)


class RepositorioFalso(RepositorioHistorial):
    def __init__(self, movimientos):
        self._movimientos = movimientos

    def listar_movimientos(self, cuenta):
        return self._movimientos


class HistorialConRepositorioFalsoTests(TestCase):
    def test_el_historial_funciona_con_cualquier_repositorio(self):
        enero = Movimiento(tipo=TipoMovimiento.GASTO, monto=Decimal("5"), fecha=date(2026, 1, 5), descripcion="a")
        junio = Movimiento(tipo=TipoMovimiento.GASTO, monto=Decimal("5"), fecha=date(2026, 6, 5), descripcion="b")
        historial = HistorialMovimientos(RepositorioFalso([enero, junio]))
        filtro = FiltroPorRangoFechas(date(2026, 6, 1), date(2026, 6, 30))
        self.assertEqual(historial.obtener_movimientos(None, filtro), [junio])


class HistorialEndpointTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()
        token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)
        self.cabecera = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        self.salario = crear("Salario", date(2026, 6, 1), "3000", TipoMovimiento.INGRESO, self.cuenta)
        crear("Cursos", date(2026, 7, 3), "170", cuenta=self.cuenta)
        crear("Ajeno", date(2026, 6, 2), "50", cuenta=crear_cuenta("luis@correo.com"))

    def test_lista_todos_los_movimientos(self):
        respuesta = self.client.get("/api/movimientos", **self.cabecera)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()), 2)
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_filtra_por_rango_de_fechas(self):
        respuesta = self.client.get("/api/movimientos?desde=2026-06-01&hasta=2026-06-30", **self.cabecera)
        movimientos = respuesta.json()
        self.assertEqual(len(movimientos), 1)
        esperado = {
            "id": self.salario.pk,
            "tipo": "INGRESO",
            "descripcion": "Salario",
            "monto": 3000.0,
            "fecha": "2026-06-01",
        }
        self.assertEqual({campo: movimientos[0][campo] for campo in esperado}, esperado)

    def test_rango_invertido_responde_400(self):
        respuesta = self.client.get("/api/movimientos?desde=2026-06-30&hasta=2026-06-01", **self.cabecera)
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("posterior", respuesta.json()["error"])

    def test_fechas_vacias_responde_400(self):
        respuesta = self.client.get("/api/movimientos?desde=&hasta=", **self.cabecera)
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("Debe ingresar", respuesta.json()["error"])

    def test_fecha_mal_escrita_responde_400(self):
        respuesta = self.client.get("/api/movimientos?desde=abc&hasta=2026-06-01", **self.cabecera)
        self.assertEqual(respuesta.status_code, 400)

    def test_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get("/api/movimientos").status_code, 401)

    def test_solo_acepta_get(self):
        self.assertEqual(self.client.post("/api/movimientos", **self.cabecera).status_code, 405)
