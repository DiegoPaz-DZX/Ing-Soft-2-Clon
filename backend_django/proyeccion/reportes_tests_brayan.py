"""
Pruebas de Brayan Ulises Ponte Portugal.

CAJA NEGRA (HU30): exportar el reporte mensual en la divisa activa.
    Endpoint: GET /api/reportes/financiero/exportar?formato=&anio=&mes=
    Entradas (5): formato, anio, mes, divisa activa (preferencia guardada) y token.
    Tecnica: particiones de equivalencia y valores limite (CN-B01 a CN-B20).

PRUEBA UNITARIA (HU5): ConstructorReporte.con_evolucion_mensual()
    Datos del grafico de barras de ingresos y gastos por mes (U-B1 a U-B6).

Ejecutar:  python manage.py test reportes.tests_brayan
"""
import io
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from openpyxl import load_workbook

from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento
from preferencias.PreferenciaMoneda import PreferenciaMoneda
from preferencias.TipoCambioDiario import TipoCambioDiario
from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .ConstructorReporte import ConstructorReporte

URL = "/api/reportes/financiero/exportar"
TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
NOMBRES = {"alimentacion": "Alimentación", "transporte": "Transporte"}


# ======================================================================
#  CAJA NEGRA - HU30
# ======================================================================
class CajaNegraExportacionTests(TestCase):
    """
    Escenario (octubre 2026, 1 USD = 3.75 PEN):
        ingreso S/3750, gasto S/375 (alimentacion), gasto 20 USD (= S/75)
        En soles:   ingresos 3750, gastos 450, balance 3300
        En dolares: ingresos 1000, gastos 120, balance 880
    Tambien hay un gasto de septiembre y uno de otra cuenta (no deben salir).
    """

    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(correo="brayan@correo.com", clave_hash="x")
        otra = CuentaUsuario.objects.create(correo="otra@correo.com", clave_hash="x")
        token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        TipoCambioDiario.objects.create(
            fecha=timezone.localdate(), soles_por_dolar=Decimal("3.75"), fuente="prueba"
        )
        self._mov("Sueldo", date(2026, 10, 1), "3750", TipoMovimiento.INGRESO)
        self._mov("Almuerzo", date(2026, 10, 5), "375", categoria="alimentacion")
        self._mov("Suscripcion", date(2026, 10, 8), "20", moneda="USD")
        self._mov("Septiembre", date(2026, 9, 20), "999")
        self._mov("Ajeno", date(2026, 10, 3), "888", usuario=otra)

    def _mov(self, descripcion, fecha, monto, tipo=TipoMovimiento.GASTO,
             categoria="", moneda="PEN", usuario=None):
        return Movimiento.objects.create(
            usuario=usuario or self.cuenta, tipo=tipo, monto=Decimal(monto), fecha=fecha,
            descripcion=descripcion, categoria=categoria, moneda=moneda,
        )

    def _divisa(self, codigo):
        PreferenciaMoneda.objects.update_or_create(cuenta=self.cuenta, defaults={"divisa": codigo})

    def _exportar(self, **parametros):
        return self.client.get(URL, parametros, **self.auth)

    @staticmethod
    def _texto_pdf(respuesta):
        return respuesta.content.decode("latin-1")

    @staticmethod
    def _libro(respuesta):
        return load_workbook(io.BytesIO(respuesta.content))

    # --- Divisa activa y formato (clases validas) ---------------------
    def test_CN_B01_pdf_en_soles(self):
        self._divisa("PEN")
        r = self._exportar(formato="pdf", anio=2026, mes=10)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")
        self.assertIn("reporte-2026-10-PEN.pdf", r["Content-Disposition"])
        texto = self._texto_pdf(r)
        self.assertIn("Ingresos: S/ 3,750.00", texto)
        self.assertIn("Gastos: S/ 450.00", texto)
        self.assertIn("Balance: S/ 3,300.00", texto)

    def test_CN_B02_pdf_en_dolares(self):
        self._divisa("USD")
        r = self._exportar(formato="pdf", anio=2026, mes=10)
        self.assertEqual(r.status_code, 200)
        self.assertIn("reporte-2026-10-USD.pdf", r["Content-Disposition"])
        texto = self._texto_pdf(r)
        self.assertIn("1 USD = 3.7500 PEN", texto)
        self.assertIn("Ingresos: $ 1,000.00", texto)
        self.assertIn("Gastos: $ 120.00", texto)
        self.assertIn("Balance: $ 880.00", texto)
        self.assertNotIn("S/ 3,750.00", texto)

    def test_CN_B03_excel_en_dolares_hoja_resumen(self):
        self._divisa("USD")
        r = self._exportar(formato="excel", anio=2026, mes=10)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], TIPO_XLSX)
        self.assertIn("reporte-2026-10-USD.xlsx", r["Content-Disposition"])
        resumen = {fila[0]: fila[1] for fila in self._libro(r)["Resumen"].iter_rows(values_only=True) if fila[0]}
        self.assertEqual(resumen["Ingresos (USD)"], 1000)
        self.assertEqual(resumen["Gastos (USD)"], 120)
        self.assertEqual(resumen["Balance (USD)"], 880)
        self.assertEqual(resumen["Tipo de cambio (soles por 1 USD)"], 3.75)
        self.assertEqual(resumen["Movimientos"], 3)

    def test_CN_B04_excel_en_soles(self):
        self._divisa("PEN")
        r = self._exportar(formato="excel", anio=2026, mes=10)
        self.assertEqual(r.status_code, 200)
        resumen = {fila[0]: fila[1] for fila in self._libro(r)["Resumen"].iter_rows(values_only=True) if fila[0]}
        self.assertEqual(resumen["Ingresos (PEN)"], 3750)
        self.assertEqual(resumen["Gastos (PEN)"], 450)
        self.assertEqual(resumen["Tipo de cambio (soles por 1 PEN)"], 1)

    def test_CN_B05_excel_dolares_hoja_movimientos(self):
        self._divisa("USD")
        r = self._exportar(formato="excel", anio=2026, mes=10)
        montos = {fila[2]: fila[3] for fila in list(self._libro(r)["Movimientos"].iter_rows(values_only=True))[1:]}
        self.assertEqual(montos["Suscripcion"], 20)   # 20 USD
        self.assertEqual(montos["Almuerzo"], 100)     # S/375 / 3.75

    def test_CN_B06_la_divisa_se_lee_en_cada_descarga(self):
        self._divisa("PEN")
        primero = self._exportar(formato="pdf", anio=2026, mes=10)
        self._divisa("USD")
        segundo = self._exportar(formato="pdf", anio=2026, mes=10)
        self.assertIn("reporte-2026-10-PEN.pdf", primero["Content-Disposition"])
        self.assertIn("reporte-2026-10-USD.pdf", segundo["Content-Disposition"])

    def test_CN_B07_sin_preferencia_guardada_usa_soles(self):
        r = self._exportar(formato="pdf", anio=2026, mes=10)
        self.assertEqual(r.status_code, 200)
        self.assertIn("reporte-2026-10-PEN.pdf", r["Content-Disposition"])

    def test_CN_B08_formato_en_mayusculas(self):
        r = self._exportar(formato="PDF", anio=2026, mes=10)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")

    def test_CN_B09_formato_omitido_usa_pdf(self):
        r = self._exportar(anio=2026, mes=10)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")

    # --- Clases invalidas y valores limite ----------------------------
    def test_CN_B10_formato_invalido(self):
        r = self._exportar(formato="csv", anio=2026, mes=10)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "El formato debe ser pdf o excel.")

    def test_CN_B11_limite_mes_1_y_mes_12_son_validos(self):
        self.assertEqual(self._exportar(formato="pdf", anio=2026, mes=1).status_code, 200)
        self.assertEqual(self._exportar(formato="pdf", anio=2026, mes=12).status_code, 200)

    def test_CN_B12_limite_mes_0_y_mes_13_son_invalidos(self):
        for mes in (0, 13):
            r = self._exportar(formato="pdf", anio=2026, mes=mes)
            self.assertEqual(r.status_code, 400)
            self.assertEqual(r.json()["error"], "El año o el mes no son válidos.")

    def test_CN_B13_valores_no_numericos(self):
        self.assertEqual(self._exportar(formato="pdf", anio=2026, mes="abc").status_code, 400)
        r = self._exportar(formato="pdf", anio="dos mil", mes=10)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "El año o el mes no son válidos.")

    def test_CN_B14_limite_anio_0_y_anio_10000(self):
        for anio in (0, 10000):
            self.assertEqual(self._exportar(formato="pdf", anio=anio, mes=10).status_code, 400)

    def test_CN_B15_anio_y_mes_omitidos_usan_la_fecha_de_hoy(self):
        r = self._exportar(formato="pdf")
        hoy = timezone.localdate()
        self.assertEqual(r.status_code, 200)
        self.assertIn(f"reporte-{hoy.year}-{hoy.month:02d}-PEN.pdf", r["Content-Disposition"])

    def test_CN_B16_mes_sin_movimientos(self):
        r = self._exportar(formato="pdf", anio=2026, mes=2)
        self.assertEqual(r.status_code, 200)
        texto = self._texto_pdf(r)
        self.assertIn("Movimientos: 0", texto)
        self.assertIn("Ingresos: S/ 0.00", texto)

    def test_CN_B17_solo_incluye_el_mes_y_la_cuenta_pedidos(self):
        texto = self._texto_pdf(self._exportar(formato="pdf", anio=2026, mes=10))
        self.assertIn("Movimientos: 3", texto)
        self.assertNotIn("Septiembre", texto)
        self.assertNotIn("Ajeno", texto)

    # --- Token / sesion ------------------------------------------------
    def test_CN_B18_sin_cabecera_authorization(self):
        r = self.client.get(URL, {"formato": "pdf", "anio": 2026, "mes": 10})
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json()["error"], "La sesión es obligatoria.")

    def test_CN_B19_token_alterado(self):
        r = self.client.get(URL, {"formato": "pdf"}, HTTP_AUTHORIZATION="Bearer token.alterado")
        self.assertEqual(r.status_code, 401)

    def test_CN_B20_metodo_post_no_permitido(self):
        self.assertEqual(self.client.post(URL, {}, **self.auth).status_code, 405)

    # --- Falla interna del exportador ----------------------------------
    def test_si_el_exportador_falla_responde_500_con_mensaje_claro(self):
        with patch("reportes.ExportadorPdfMoneda.ExportadorPdfMoneda.exportar", side_effect=RuntimeError("boom")):
            r = self._exportar(formato="pdf", anio=2026, mes=10)
        self.assertEqual(r.status_code, 500)
        self.assertEqual(r.json()["error"], "No se pudo generar el reporte, intente más tarde")


# ======================================================================
#  PRUEBA UNITARIA - HU5 : ConstructorReporte.con_evolucion_mensual()
# ======================================================================
def movimiento(tipo, monto, fecha, categoria="", moneda="PEN"):
    """Movimiento en memoria (sin base de datos): la prueba es unitaria."""
    return Movimiento(tipo=tipo, monto=Decimal(monto), fecha=fecha,
                      descripcion="x", categoria=categoria, moneda=moneda)


def gasto(monto, fecha, **extra):
    return movimiento(TipoMovimiento.GASTO, monto, fecha, **extra)


def ingreso(monto, fecha):
    return movimiento(TipoMovimiento.INGRESO, monto, fecha)


def evolucion(movimientos, soles_por_dolar=None):
    constructor = ConstructorReporte(movimientos, NOMBRES, soles_por_dolar=soles_por_dolar)
    return constructor.con_evolucion_mensual().construir().evolucion_mensual


class UnitariaEvolucionMensualTests(SimpleTestCase):

    def test_U_B1_sin_movimientos_devuelve_lista_vacia(self):
        self.assertEqual(evolucion([]), [])

    def test_U_B2_un_mes_suma_ingresos_y_gastos(self):
        meses = evolucion([
            ingreso("3000", date(2026, 10, 1)),
            gasto("400", date(2026, 10, 5)),
            gasto("100.50", date(2026, 10, 20)),
        ])
        self.assertEqual(len(meses), 1)
        self.assertEqual(meses[0].periodo, "2026-10")
        self.assertEqual(meses[0].etiqueta, "Octubre 2026")
        self.assertEqual(meses[0].ingresos, Decimal("3000.00"))
        self.assertEqual(meses[0].gastos, Decimal("500.50"))

    def test_U_B3_los_meses_salen_en_orden_cronologico(self):
        meses = evolucion([
            gasto("10", date(2026, 3, 1)),
            gasto("10", date(2026, 1, 1)),
            gasto("10", date(2026, 2, 1)),
        ])
        self.assertEqual([m.periodo for m in meses], ["2026-01", "2026-02", "2026-03"])

    def test_U_B4_limite_diciembre_va_antes_que_enero_del_anio_siguiente(self):
        meses = evolucion([
            gasto("10", date(2027, 1, 3)),
            gasto("10", date(2026, 12, 28)),
        ])
        self.assertEqual([m.etiqueta for m in meses], ["Diciembre 2026", "Enero 2027"])

    def test_U_B5_un_mes_con_solo_gastos_tiene_ingresos_en_cero(self):
        meses = evolucion([gasto("80", date(2026, 10, 9))])
        self.assertEqual(meses[0].ingresos, Decimal("0.00"))
        self.assertEqual(meses[0].gastos, Decimal("80.00"))

    def test_U_B6_gasto_en_dolares_se_convierte_a_soles(self):
        meses = evolucion(
            [gasto("100", date(2026, 10, 2)), gasto("20", date(2026, 10, 3), moneda="USD")],
            soles_por_dolar=Decimal("3.75"),
        )
        self.assertEqual(meses[0].gastos, Decimal("175.00"))  # 100 + 20 * 3.75


class UnitariaGraficoCircularTests(SimpleTestCase):
    """Datos del grafico circular de gastos por categoria (complemento de HU5)."""

    def _categorias(self, movimientos):
        return ConstructorReporte(movimientos, NOMBRES).con_gastos_por_categoria().construir().gastos_por_categoria

    def test_los_porcentajes_se_calculan_sobre_el_total_de_gastos(self):
        categorias = self._categorias([
            gasto("300", date(2026, 10, 1), categoria="alimentacion"),
            gasto("100", date(2026, 10, 2), categoria="transporte"),
        ])
        self.assertEqual([c.nombre for c in categorias], ["Alimentación", "Transporte"])
        self.assertEqual([c.porcentaje for c in categorias], [Decimal("75.0"), Decimal("25.0")])

    def test_un_gasto_sin_categoria_se_agrupa_en_otros(self):
        categorias = self._categorias([gasto("50", date(2026, 10, 1))])
        self.assertEqual(categorias[0].codigo, "otros")

    def test_los_ingresos_no_aparecen_en_el_grafico(self):
        categorias = self._categorias([
            ingreso("5000", date(2026, 10, 1)),
            gasto("100", date(2026, 10, 2), categoria="transporte"),
        ])
        self.assertEqual(len(categorias), 1)
        self.assertEqual(categorias[0].codigo, "transporte")
