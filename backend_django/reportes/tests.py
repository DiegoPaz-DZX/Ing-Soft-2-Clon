import json
from datetime import date
from decimal import Decimal

from django.test import TestCase

from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento
from historial.RangoFechasInvalidoException import RangoFechasInvalidoException
from historial.HistorialMovimientos import HistorialMovimientos
from historial.RepositorioHistorialDjango import RepositorioHistorialDjango
from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .ConstructorReporte import ConstructorReporte
from .ExportadorCsv import ExportadorCsv
from .ExportadorJson import ExportadorJson
from .ExportadorPdfGraficos import ExportadorPdfGraficos
from .FabricaReglasAnalisis import FabricaReglasAnalisis
from .Observacion import Observacion
from .ReglaAnalisis import ReglaAnalisis
from .FabricaExportadores import FabricaExportadores
from .FormatoNoSoportadoException import FormatoNoSoportadoException
from .ServicioReportes import ServicioReportes

NOMBRES = {"alimentacion": "Alimentación", "transporte": "Transporte"}


def obtener_cuenta(correo="ana@correo.com"):
    return CuentaUsuario.objects.get_or_create(correo=correo, defaults={"clave_hash": "x"})[0]


def cabecera():
    token = ServicioTokens(RepositorioCuentasDjango()).crear(obtener_cuenta())
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def crear(descripcion, fecha, monto, tipo=TipoMovimiento.GASTO, categoria="", moneda="PEN"):
    return Movimiento.objects.create(
        usuario=obtener_cuenta(),
        tipo=tipo,
        monto=Decimal(monto),
        fecha=fecha,
        descripcion=descripcion,
        categoria=categoria,
        moneda=moneda,
    )


def cargar_movimientos():
    crear("Salario", date(2026, 6, 1), "3000", TipoMovimiento.INGRESO)
    crear("Mercado", date(2026, 6, 5), "600", categoria="alimentacion")
    crear("Taxi", date(2026, 6, 12), "150", categoria="transporte")
    crear("Almuerzos", date(2026, 7, 3), "250", categoria="alimentacion")


class CategoriasFalsas:
    def obtener_todas(self):
        return []


class TipoCambioFalso:
    def __init__(self, soles_por_dolar="4.0000"):
        self.soles_por_dolar = Decimal(soles_por_dolar)
        self.consultas = 0

    def obtener_del_dia(self):
        self.consultas += 1
        return self


def crear_servicio(tipo_cambio=None):
    return ServicioReportes(
        HistorialMovimientos(RepositorioHistorialDjango()),
        CategoriasFalsas(),
        tipo_cambio or TipoCambioFalso(),
        FabricaReglasAnalisis.crear_todas(),
    )


class ConstructorReporteTests(TestCase):
    def setUp(self):
        cargar_movimientos()
        self.movimientos = list(Movimiento.objects.all())

    def test_el_resumen_siempre_se_calcula(self):
        reporte = ConstructorReporte(self.movimientos, NOMBRES).construir()
        self.assertEqual(reporte.cantidad_movimientos, 4)
        self.assertEqual(reporte.total_ingresos, Decimal("3000"))
        self.assertEqual(reporte.total_gastos, Decimal("1000"))
        self.assertEqual(reporte.balance, Decimal("2000"))
        self.assertEqual(reporte.tasa_ahorro, Decimal("66.7"))
        self.assertEqual(reporte.gastos_por_categoria, [])
        self.assertEqual(reporte.observaciones, [])

    def test_agrupa_los_gastos_por_categoria_de_mayor_a_menor(self):
        reporte = ConstructorReporte(self.movimientos, NOMBRES).con_gastos_por_categoria().construir()
        self.assertEqual(
            [(c.nombre, c.monto, c.porcentaje) for c in reporte.gastos_por_categoria],
            [("Alimentación", Decimal("850"), Decimal("85.0")), ("Transporte", Decimal("150"), Decimal("15.0"))],
        )

    def test_la_evolucion_mensual_va_en_orden_cronologico(self):
        reporte = ConstructorReporte(self.movimientos, NOMBRES).con_evolucion_mensual().construir()
        self.assertEqual(
            [(m.etiqueta, m.ingresos, m.gastos) for m in reporte.evolucion_mensual],
            [("Junio 2026", Decimal("3000"), Decimal("750")), ("Julio 2026", Decimal("0"), Decimal("250"))],
        )

    def test_el_analisis_resume_balance_categoria_y_meses(self):
        reglas = FabricaReglasAnalisis.crear_todas()
        reporte = ConstructorReporte(self.movimientos, NOMBRES).con_analisis(reglas).construir()
        titulos = [observacion.titulo for observacion in reporte.observaciones]
        self.assertEqual(
            titulos,
            ["Balance positivo", "Mayor gasto: Alimentación", "Gasto promedio mensual", "Mes con más gastos: Junio 2026"],
        )
        self.assertEqual(reporte.observaciones[0].nivel, "positivo")
        self.assertEqual(reporte.observaciones[2].monto, Decimal("500.00"))

    def test_avisa_cuando_los_gastos_superan_a_los_ingresos(self):
        gastos = [m for m in self.movimientos if m.tipo == TipoMovimiento.GASTO]
        reglas = FabricaReglasAnalisis.crear_todas()
        reporte = ConstructorReporte(gastos, NOMBRES).con_analisis(reglas).construir()
        self.assertEqual(reporte.observaciones[0].nivel, "advertencia")
        self.assertEqual(reporte.observaciones[0].monto, Decimal("1000"))
        self.assertIsNone(reporte.tasa_ahorro)

    def test_se_puede_agregar_una_regla_sin_modificar_el_constructor(self):
        class ReglaCantidad(ReglaAnalisis):
            def evaluar(self, reporte, categorias, meses):
                return [Observacion("informacion", "Movimientos", f"{reporte.cantidad_movimientos} en total.")]

        reporte = ConstructorReporte(self.movimientos, NOMBRES).con_analisis([ReglaCantidad()]).construir()
        self.assertEqual([o.mensaje for o in reporte.observaciones], ["4 en total."])

    def test_sin_movimientos_no_hay_analisis(self):
        reporte = (
            ConstructorReporte([], NOMBRES)
            .con_gastos_por_categoria()
            .con_evolucion_mensual()
            .con_analisis(FabricaReglasAnalisis.crear_todas())
            .construir()
        )
        self.assertEqual(reporte.cantidad_movimientos, 0)
        self.assertEqual(reporte.observaciones, [])


class ServicioReportesTests(TestCase):
    def setUp(self):
        cargar_movimientos()
        self.tipo_cambio = TipoCambioFalso()
        self.servicio = crear_servicio(self.tipo_cambio)

    def test_sin_fechas_incluye_todos_los_movimientos(self):
        self.assertEqual(self.servicio.generar_reporte(cuenta=obtener_cuenta()).cantidad_movimientos, 4)

    def test_filtra_por_rango_de_fechas(self):
        reporte = self.servicio.generar_reporte(date(2026, 6, 1), date(2026, 6, 30), cuenta=obtener_cuenta())
        self.assertEqual(reporte.cantidad_movimientos, 3)
        self.assertEqual(reporte.total_gastos, Decimal("750"))
        self.assertEqual([m.descripcion for m in reporte.movimientos], ["Taxi", "Mercado", "Salario"])

    def test_permite_omitir_graficos_y_analisis(self):
        reporte = self.servicio.generar_reporte(con_graficos=False, con_analisis=False, cuenta=obtener_cuenta())
        self.assertEqual(reporte.gastos_por_categoria, [])
        self.assertEqual(reporte.evolucion_mensual, [])
        self.assertEqual(reporte.observaciones, [])
        self.assertEqual(reporte.total_ingresos, Decimal("3000"))

    def test_rechaza_rangos_invalidos(self):
        with self.assertRaises(RangoFechasInvalidoException):
            self.servicio.generar_reporte(date(2026, 6, 30), date(2026, 6, 1), cuenta=obtener_cuenta())
        with self.assertRaises(RangoFechasInvalidoException):
            self.servicio.generar_reporte(date(2026, 6, 1), None, cuenta=obtener_cuenta())

    def test_sin_movimientos_en_dolares_no_consulta_el_tipo_de_cambio(self):
        reporte = self.servicio.generar_reporte(cuenta=obtener_cuenta())
        self.assertEqual(self.tipo_cambio.consultas, 0)
        self.assertIsNone(reporte.soles_por_dolar)

    def test_los_movimientos_en_dolares_se_pasan_a_soles(self):
        crear("Freelance", date(2026, 7, 10), "100", TipoMovimiento.INGRESO, moneda="USD")
        crear("Suscripcion", date(2026, 7, 11), "10.50", categoria="transporte", moneda="USD")
        reporte = self.servicio.generar_reporte(date(2026, 7, 1), date(2026, 7, 31), cuenta=obtener_cuenta())
        self.assertEqual(self.tipo_cambio.consultas, 1)
        self.assertEqual(reporte.soles_por_dolar, Decimal("4.0000"))
        self.assertEqual(reporte.total_ingresos, Decimal("400.00"))
        self.assertEqual(reporte.total_gastos, Decimal("292.00"))
        suscripcion = reporte.movimientos[0]
        self.assertEqual(
            (suscripcion.moneda, suscripcion.monto, suscripcion.monto_en_soles),
            ("USD", Decimal("10.50"), Decimal("42.00")),
        )
        self.assertEqual(reporte.movimientos[-1].monto_en_soles, Decimal("250"))


class ExportadoresTests(TestCase):
    def setUp(self):
        cargar_movimientos()
        self.reporte = crear_servicio().generar_reporte(cuenta=obtener_cuenta())

    def test_la_fabrica_crea_el_exportador_segun_el_formato(self):
        self.assertIsInstance(FabricaExportadores.crear("csv"), ExportadorCsv)
        self.assertIsInstance(FabricaExportadores.crear("JSON"), ExportadorJson)
        self.assertIsInstance(FabricaExportadores.crear("pdf"), ExportadorPdfGraficos)
        with self.assertRaises(FormatoNoSoportadoException):
            FabricaExportadores.crear("xml")

    def test_el_csv_incluye_resumen_graficos_analisis_y_movimientos(self):
        contenido = ExportadorCsv().exportar(self.reporte)
        self.assertTrue(contenido.startswith("﻿Reporte financiero Kyzen"))
        self.assertIn("Ingresos (PEN),3000.00", contenido)
        self.assertIn("Balance (PEN),2000.00", contenido)
        self.assertIn("Alimentacion,850.00,85.0", contenido)
        self.assertIn("Junio 2026,3000.00,750.00", contenido)
        self.assertIn("Balance positivo", contenido)
        self.assertIn("2026-06-05,GASTO,Mercado,alimentacion,PEN,600.00,600.00", contenido)

    def test_el_json_conserva_los_datos_del_reporte(self):
        datos = json.loads(ExportadorJson().exportar(self.reporte))
        self.assertEqual(datos["balance"], 2000.0)
        self.assertEqual(datos["tasaAhorro"], 66.7)
        self.assertEqual(len(datos["movimientos"]), 4)


def en_pdf(texto):
    escapado = texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return ("(" + escapado + ")").encode("cp1252")


class ExportadorPdfGraficosTests(TestCase):
    def setUp(self):
        cargar_movimientos()
        self.servicio = crear_servicio()

    def exportar(self, **opciones):
        reporte = self.servicio.generar_reporte(cuenta=obtener_cuenta(), **opciones)
        return ExportadorPdfGraficos().exportar(reporte)

    def test_genera_un_pdf_valido(self):
        pdf = self.exportar()
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"startxref", pdf)
        paginas = pdf.count(b"/Type /Page ")
        self.assertGreaterEqual(paginas, 1)
        self.assertIn(f"/Count {paginas} >>".encode("latin-1"), pdf)

    def test_exportacion_pdf_genera_estructura_correcta(self):
        pdf = self.exportar()

        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"startxref", pdf)
        self.assertIn(en_pdf("Reporte financiero Kyzen"), pdf)

    def test_incluye_resumen_graficos_analisis_y_movimientos(self):
        pdf = self.exportar()
        for texto in [
            "Reporte financiero Kyzen",
            "S/ 3,000.00",
            "Ingresos vs gastos por mes",
            "Gastos por categoría",
            "Análisis financiero",
            "Balance positivo",
            "Detalle de movimientos (4)",
            "Mercado",
        ]:
            with self.subTest(texto=texto):
                self.assertIn(en_pdf(texto), pdf)
        self.assertIn(b" c ", pdf)

    def test_sin_graficos_ni_analisis_solo_trae_resumen_y_movimientos(self):
        pdf = self.exportar(con_graficos=False, con_analisis=False)
        self.assertNotIn(en_pdf("Ingresos vs gastos por mes"), pdf)
        self.assertNotIn(en_pdf("Análisis financiero"), pdf)
        self.assertNotIn(b" c ", pdf)
        self.assertIn(en_pdf("Mercado"), pdf)

    def test_los_movimientos_en_dolares_muestran_su_monto_original_y_en_soles(self):
        crear("Suscripcion", date(2026, 7, 10), "20", categoria="transporte", moneda="USD")
        pdf = self.exportar()
        self.assertIn(en_pdf("$ 20.00"), pdf)
        self.assertIn(en_pdf("S/ 80.00"), pdf)
        self.assertIn(b"1 USD = S/ 4.0000", pdf)

    def test_muchos_movimientos_ocupan_varias_paginas(self):
        for numero in range(80):
            crear(f"Pasaje {numero}", date(2026, 8, 1), "5", categoria="transporte")
        pdf = self.exportar()
        paginas = pdf.count(b"/Type /Page ")
        self.assertGreater(paginas, 1)
        self.assertIn(en_pdf(f"Página {paginas} de {paginas}"), pdf)

    def test_un_periodo_sin_movimientos_tambien_genera_el_pdf(self):
        pdf = self.exportar(desde=date(2026, 1, 1), hasta=date(2026, 1, 31))
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(en_pdf("No hay movimientos en el periodo seleccionado."), pdf)


class ReporteEndpointTests(TestCase):
    def setUp(self):
        cargar_movimientos()

    def test_devuelve_el_reporte_completo(self):
        respuesta = self.client.get("/api/reportes/financiero", **cabecera())
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["totalIngresos"], 3000.0)
        self.assertEqual(datos["gastosPorCategoria"][0]["codigo"], "alimentacion")
        self.assertEqual(datos["gastosPorCategoria"][0]["monto"], 850.0)
        self.assertEqual(len(datos["evolucionMensual"]), 2)
        self.assertEqual(len(datos["observaciones"]), 4)
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_filtra_por_fechas_y_respeta_las_opciones(self):
        respuesta = self.client.get(
            "/api/reportes/financiero?desde=2026-07-01&hasta=2026-07-31&graficos=0&analisis=0",
            **cabecera(),
        )
        datos = respuesta.json()
        self.assertEqual(datos["desde"], "2026-07-01")
        self.assertEqual(datos["cantidadMovimientos"], 1)
        self.assertEqual(datos["gastosPorCategoria"], [])
        self.assertEqual(datos["observaciones"], [])

    def test_descarga_el_reporte_en_csv(self):
        respuesta = self.client.get("/api/reportes/financiero?formato=csv", **cabecera())
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("text/csv", respuesta["Content-Type"])
        self.assertIn("reporte-financiero-kyzen.csv", respuesta["Content-Disposition"])
        self.assertIn("Reporte financiero Kyzen", respuesta.content.decode("utf-8"))

    def test_descarga_el_reporte_en_pdf(self):
        respuesta = self.client.get("/api/reportes/financiero?formato=pdf&analisis=0", **cabecera())
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertIn("reporte-financiero-kyzen.pdf", respuesta["Content-Disposition"])
        self.assertTrue(respuesta.content.startswith(b"%PDF-1.4"))
        self.assertNotIn(en_pdf("Análisis financiero"), respuesta.content)

    def test_descargar_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get("/api/reportes/financiero?formato=pdf").status_code, 401)
        self.assertEqual(self.client.get("/api/reportes/financiero?formato=csv").status_code, 401)

    def test_errores_responden_400(self):
        self.assertEqual(self.client.get("/api/reportes/financiero?formato=xml", **cabecera()).status_code, 400)
        invertido = self.client.get("/api/reportes/financiero?desde=2026-07-31&hasta=2026-07-01", **cabecera())
        self.assertEqual(invertido.status_code, 400)
        self.assertIn("posterior", invertido.json()["error"])
        self.assertEqual(self.client.get("/api/reportes/financiero?desde=abc&hasta=2026-07-01", **cabecera()).status_code, 400)
        self.assertEqual(self.client.get("/api/reportes/financiero?desde=2026-07-01", **cabecera()).status_code, 400)

    def test_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get("/api/reportes/financiero").status_code, 401)

    def test_solo_acepta_get(self):
        self.assertEqual(self.client.post("/api/reportes/financiero", **cabecera()).status_code, 405)
