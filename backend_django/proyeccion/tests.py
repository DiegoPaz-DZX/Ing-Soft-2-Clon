from datetime import date
from decimal import Decimal
from django.test import SimpleTestCase, TestCase
from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento
from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens
from historial.RepositorioHistorial import RepositorioHistorial
from .DetectorGastoAtipico import DetectorGastoAtipico
from .ProyeccionPorRitmoDiario import ProyeccionPorRitmoDiario
from .ServicioProyeccion import ServicioProyeccion

def mov(tipo, monto, dia, descripcion="prueba"):
    return Movimiento(tipo=tipo, monto=Decimal(monto), fecha=date(2026, 11, dia), descripcion=descripcion)

class RepositorioFalso(RepositorioHistorial):
    def __init__(self, movimientos):
        self._movimientos = movimientos

    def listar_movimientos(self, cuenta):
        return self._movimientos

def crear_servicio(movimientos):
    return ServicioProyeccion(RepositorioFalso(movimientos), ProyeccionPorRitmoDiario(), DetectorGastoAtipico())

class ProyeccionTests(SimpleTestCase):
    hoy = date(2026, 11, 10)

    def test_escenario_1_ritmo_acelerado_proyecta_sobregasto(self):
        proyeccion = crear_servicio([
            mov(TipoMovimiento.INGRESO, "1500", 1),
            mov(TipoMovimiento.GASTO, "200", 3),
            mov(TipoMovimiento.GASTO, "180", 6),
            mov(TipoMovimiento.GASTO, "220", 9),
        ]).proyectar(self.hoy, None)
        self.assertEqual(proyeccion.gasto_actual, Decimal("600"))
        self.assertEqual(proyeccion.gasto_proyectado, Decimal("1800"))
        self.assertTrue(proyeccion.hay_sobregasto)
        self.assertIn("Reduce tu gasto diario", proyeccion.sugerencia)

    def test_escenario_2_gasto_atipico_no_falsea_la_tendencia(self):
        proyeccion = crear_servicio([
            mov(TipoMovimiento.INGRESO, "3000", 1),
            mov(TipoMovimiento.GASTO, "100", 2),
            mov(TipoMovimiento.GASTO, "80", 5),
            mov(TipoMovimiento.GASTO, "90", 8),
            mov(TipoMovimiento.GASTO, "1200", 4, "Pago de pension"),
        ]).proyectar(self.hoy, None)
        self.assertEqual(proyeccion.gasto_atipico, Decimal("1200"))
        # 1200 + (270 / 10 * 30) = 2010, no 1470 / 10 * 30 = 4410
        self.assertEqual(proyeccion.gasto_proyectado, Decimal("2010"))
        self.assertFalse(proyeccion.hay_sobregasto)
        self.assertIn("gasto único", proyeccion.sugerencia)

    def test_sin_gastos_no_hay_proyeccion(self):
        proyeccion = crear_servicio([mov(TipoMovimiento.INGRESO, "1000", 1)]).proyectar(self.hoy, None)
        self.assertEqual(proyeccion.gasto_proyectado, Decimal("0"))
        self.assertIn("Aún no hay gastos", proyeccion.sugerencia)

    def test_ignora_movimientos_de_otros_meses(self):
        octubre = Movimiento(
            tipo=TipoMovimiento.GASTO, monto=Decimal("500"), fecha=date(2026, 10, 5), descripcion="viejo"
        )
        proyeccion = crear_servicio([octubre, mov(TipoMovimiento.GASTO, "100", 2)]).proyectar(self.hoy, None)
        self.assertEqual(proyeccion.gasto_actual, Decimal("100"))

class EndpointProyeccionTests(TestCase):
    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(correo="ana@correo.com", clave_hash="x")
        token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)
        self.cabecera = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_responde_la_proyeccion_para_el_frontend(self):
        hoy = date.today()
        Movimiento.objects.create(tipo=TipoMovimiento.INGRESO, monto=Decimal("1000"), fecha=hoy, descripcion="Pago", usuario=self.cuenta)
        Movimiento.objects.create(tipo=TipoMovimiento.GASTO, monto=Decimal("100"), fecha=hoy, descripcion="Almuerzo", usuario=self.cuenta)
        respuesta = self.client.get("/api/proyeccion", **self.cabecera)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            set(respuesta.json()),
            {"gastoActual", "gastoAtipico", "gastoProyectado", "ingresosMes", "haySobregasto", "sugerencia"},
        )
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_no_incluye_los_movimientos_de_otra_cuenta(self):
        otra = CuentaUsuario.objects.create(correo="luis@correo.com", clave_hash="x")
        Movimiento.objects.create(tipo=TipoMovimiento.GASTO, monto=Decimal("500"), fecha=date.today(), descripcion="ajeno", usuario=otra)
        datos = self.client.get("/api/proyeccion", **self.cabecera).json()
        self.assertEqual(datos["gastoActual"], 0.0)

    def test_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get("/api/proyeccion").status_code, 401)

    def test_solo_acepta_get(self):
        self.assertEqual(self.client.post("/api/proyeccion", **self.cabecera).status_code, 405)
