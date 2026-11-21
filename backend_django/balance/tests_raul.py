"""Pruebas de Raúl para la sección 10 del informe (HU9, HU18).

Incluye:
- caja blanca de MovimientoConValidacion.validar() (V(G) = 10, sección 10.2),
- caja negra de PUT /api/movimientos/<id>/editar (sección 10.6.6).

Si se ejecuta con KYZEN_REPORTE=1 también imprime una línea por caso para
copiar los resultados al informe sin cambiar la lógica de las pruebas.
"""

import json
import os
from datetime import date
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .Movimiento import Movimiento
from .MovimientoConValidacion import MovimientoConValidacion
from .DatosMovimientoInvalidosException import DatosMovimientoInvalidosException
from .MontoInvalidoException import MontoInvalidoException
from .TipoMovimiento import TipoMovimiento

REPORTE = os.environ.get("KYZEN_REPORTE") == "1"


def mostrar(caso, entrada, esperado, obtenido):
    if REPORTE:
        print(f"REPORTE|{caso}|{entrada}|{esperado}|{obtenido}")


def _movimiento(**campos):
    base = dict(tipo="GASTO", monto="50", fecha="2026-10-12", moneda="PEN", categoria="transporte")
    base.update(campos)
    return SimpleNamespace(**base)


def crear_cuenta(correo="raul-cb@correo.com"):
    return CuentaUsuario.objects.create(correo=correo, clave_hash="x")


def cabecera(cuenta):
    token = ServicioTokens(RepositorioCuentasDjango()).crear(cuenta)
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def crear_movimiento(cuenta, categoria="comida"):
    return Movimiento.objects.create(
        tipo=TipoMovimiento.GASTO,
        monto="40",
        fecha=date(2026, 11, 10),
        descripcion="prueba",
        categoria=categoria,
        moneda="PEN",
        usuario=cuenta,
    )


class ValidarMovimientoCajaBlancaTests(SimpleTestCase):
    """Tabla 69. Casos de caja blanca - caminos básicos de validar() (HU18)."""

    def test_cb01_monto_vacio(self):
        with self.assertRaises(MontoInvalidoException) as ctx:
            MovimientoConValidacion(_movimiento(monto=None)).validar()
        esperado = "El monto debe ser mayor que cero"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-01", "monto=None", esperado, str(ctx.exception))

    def test_cb02_monto_menor_o_igual_a_cero(self):
        with self.assertRaises(MontoInvalidoException) as ctx:
            MovimientoConValidacion(_movimiento(monto="0")).validar()
        esperado = "El monto debe ser mayor que cero"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-02", "monto=\"0\"", esperado, str(ctx.exception))

    def test_cb03_tipo_vacio(self):
        with self.assertRaises(DatosMovimientoInvalidosException) as ctx:
            MovimientoConValidacion(_movimiento(tipo="")).validar()
        esperado = "El tipo debe ser INGRESO o GASTO"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-03", "tipo=\"\"", esperado, str(ctx.exception))

    def test_cb04_tipo_no_permitido(self):
        with self.assertRaises(DatosMovimientoInvalidosException) as ctx:
            MovimientoConValidacion(_movimiento(tipo="AHORRO")).validar()
        esperado = "El tipo debe ser INGRESO o GASTO"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-04", "tipo=\"AHORRO\"", esperado, str(ctx.exception))

    def test_cb05_fecha_vacia(self):
        with self.assertRaises(DatosMovimientoInvalidosException) as ctx:
            MovimientoConValidacion(_movimiento(fecha=None)).validar()
        esperado = "La fecha es obligatoria"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-05", "fecha=None", esperado, str(ctx.exception))

    def test_cb06_fecha_con_formato_invalido(self):
        with self.assertRaises(DatosMovimientoInvalidosException) as ctx:
            MovimientoConValidacion(_movimiento(fecha="12/10/2026")).validar()
        esperado = "La fecha debe estar en formato AAAA-MM-DD"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-06", "fecha=\"12/10/2026\"", esperado, str(ctx.exception))

    def test_cb07_moneda_no_permitida(self):
        with self.assertRaises(DatosMovimientoInvalidosException) as ctx:
            MovimientoConValidacion(_movimiento(moneda="EUR")).validar()
        esperado = "La moneda debe ser PEN o USD"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-07", "moneda=\"EUR\"", esperado, str(ctx.exception))

    def test_cb08_gasto_sin_categoria(self):
        with self.assertRaises(DatosMovimientoInvalidosException) as ctx:
            MovimientoConValidacion(_movimiento(categoria="")).validar()
        esperado = "Los gastos deben tener una categoría"
        self.assertEqual(str(ctx.exception), esperado)
        mostrar("CB-08", "tipo=\"GASTO\", categoria=\"\"", esperado, str(ctx.exception))

    def test_cb09_gasto_valido(self):
        resultado = MovimientoConValidacion(_movimiento()).validar()
        self.assertTrue(resultado)
        mostrar("CB-09", "GASTO, 50, 2026-10-12, PEN, transporte", True, resultado)

    def test_cb10_ingreso_valido_sin_categoria(self):
        datos = _movimiento(tipo="INGRESO", monto="1500", fecha="2026-10-01", moneda="USD", categoria="")
        resultado = MovimientoConValidacion(datos).validar()
        self.assertTrue(resultado)
        mostrar("CB-10", "INGRESO, 1500, 2026-10-01, USD, \"\"", True, resultado)


class EdicionMovimientoCajaNegraTests(TestCase):
    """Tabla 93. Casos de caja negra de la edición de transacciones (HU18)."""

    def setUp(self):
        self.cuenta = crear_cuenta()
        self.cabecera = cabecera(self.cuenta)
        self.movimiento = crear_movimiento(self.cuenta)

    def editar(self, datos, movimiento_id=None):
        return self.client.put(
            f"/api/movimientos/{movimiento_id or self.movimiento.pk}/editar",
            data=json.dumps(datos),
            content_type="application/json",
            **self.cabecera,
        )

    def datos(self, **cambios):
        base = {"tipo": "GASTO", "monto": "40.00", "fecha": "2026-11-10",
                "categoria": "comida", "moneda": "PEN"}
        return {**base, **cambios}

    def test_cnh01_gasto_valido(self):
        respuesta = self.editar(self.datos())
        self.assertEqual(respuesta.status_code, 200)
        mostrar("CN-H01", "GASTO, 40.00, 2026-11-10, comida, PEN",
                "Se actualiza el movimiento", respuesta.status_code)

    def test_cnh02_monto_limite_inferior(self):
        respuesta = self.editar(self.datos(monto="0.01"))
        self.assertEqual(respuesta.status_code, 200)
        mostrar("CN-H02", "GASTO, 0.01, 2026-11-10, comida, PEN",
                "Se actualiza el movimiento", respuesta.status_code)

    def test_cnh03_monto_cero(self):
        respuesta = self.editar(self.datos(monto="0"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "El monto debe ser mayor que cero"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H03", "GASTO, 0, 2026-11-10, comida, PEN", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh04_monto_negativo(self):
        respuesta = self.editar(self.datos(monto="-10"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "El monto debe ser mayor que cero"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H04", "GASTO, -10, 2026-11-10, comida, PEN", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh05_monto_no_numerico(self):
        respuesta = self.editar(self.datos(monto="abc"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "El monto debe ser un número"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H05", "GASTO, abc, 2026-11-10, comida, PEN", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh06_fecha_con_otro_formato(self):
        respuesta = self.editar(self.datos(fecha="13/11/2026"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "La fecha es obligatoria (AAAA-MM-DD)"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H06", "GASTO, 40, 13/11/2026, comida, PEN", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh07_fecha_inexistente(self):
        respuesta = self.editar(self.datos(fecha="2026-02-30"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "La fecha es obligatoria (AAAA-MM-DD)"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H07", "GASTO, 40, 2026-02-30, comida, PEN", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh08_tipo_invalido(self):
        respuesta = self.editar(self.datos(tipo="TRANSFERENCIA"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "El tipo debe ser ingreso o gasto"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H08", "TRANSFERENCIA, 40, 2026-11-10, comida, PEN", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh09_gasto_sin_categoria(self):
        respuesta = self.editar(self.datos(categoria=""))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "Los gastos deben tener una categoría"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H09", "GASTO, 40, 2026-11-10, sin categoría, PEN", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh10_ingreso_sin_categoria(self):
        respuesta = self.editar(self.datos(tipo="INGRESO", monto="1500", fecha="2026-11-01",
                                            categoria="", moneda="USD"))
        self.assertEqual(respuesta.status_code, 200)
        mostrar("CN-H10", "INGRESO, 1500, 2026-11-01, sin categoría, USD",
                "Se actualiza el movimiento (un ingreso no necesita categoría)", respuesta.status_code)

    def test_cnh11_ahorro_sin_meta(self):
        respuesta = self.editar(self.datos(categoria="ahorro"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "Selecciona la meta que recibirá este ahorro."
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H11", "GASTO, 40, 2026-11-10, ahorro, PEN, sin meta", f"Error: {esperado}", respuesta.json()["error"])

    def test_cnh12_moneda_no_soportada(self):
        respuesta = self.editar(self.datos(moneda="EUR"))
        self.assertEqual(respuesta.status_code, 400)
        esperado = "La moneda debe ser Soles (PEN) o Dólares (USD)"
        self.assertEqual(respuesta.json()["error"], esperado)
        mostrar("CN-H12", "GASTO, 40, 2026-11-10, comida, EUR", f"Error: {esperado}", respuesta.json()["error"])