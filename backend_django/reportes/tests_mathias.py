
import json

from django.test import TestCase

J = "application/json"
RANGO = "desde=2026-11-01&hasta=2026-11-30"


class ReporteFinancieroCajaNegraTests(TestCase):
    def setUp(self):
        self.client.post("/api/registro", json.dumps({"correo": "m@correo.com", "clave": "Clave123!", "confirmacion": "Clave123!"}), content_type=J)
        token = self.client.post("/api/login", json.dumps({"correo": "m@correo.com", "clave": "Clave123!"}), content_type=J).json()["token"]
        self.h = {"HTTP_AUTHORIZATION": "Bearer " + token}
        for tipo, monto, categoria, fecha in [
            ("ingreso", "1000", "", "2026-11-03"),
            ("gasto", "300", "alimentación", "2026-11-05"),
            ("gasto", "100", "transporte", "2026-10-10"),
        ]:
            self.client.post(
                "/api/movimientos/nuevo",
                json.dumps({"tipo": tipo, "monto": monto, "fecha": fecha, "descripcion": "x", "categoria": categoria, "moneda": "PEN"}),
                content_type=J,
                **self.h,
            )

    def pedir(self, consulta, con_sesion=True):
        return self.client.get("/api/reportes/financiero?" + consulta, **(self.h if con_sesion else {}))

    def test_cn01_descarga_pdf_con_graficos_y_analisis(self):
        r = self.pedir(RANGO + "&formato=pdf&graficos=1&analisis=1")
        self.assertEqual(r.status_code, 200)
        self.assertIn("reporte-financiero-kyzen.pdf", r["Content-Disposition"])

    def test_cn02_descarga_csv_sin_graficos_ni_analisis(self):
        r = self.pedir(RANGO + "&formato=csv&graficos=0&analisis=0")
        self.assertEqual(r.status_code, 200)
        self.assertIn("reporte-financiero-kyzen.csv", r["Content-Disposition"])

    def test_cn03_descarga_json(self):
        r = self.pedir(RANGO + "&formato=json&graficos=1&analisis=0")
        self.assertEqual(r.status_code, 200)
        self.assertIn("reporte-financiero-kyzen.json", r["Content-Disposition"])

    def test_cn04_reporte_en_pantalla_con_totales_del_rango(self):
        datos = self.pedir(RANGO + "&graficos=1&analisis=1").json()
        self.assertEqual(datos["totalIngresos"], 1000.0)
        self.assertEqual(datos["totalGastos"], 300.0)
        self.assertEqual(datos["balance"], 700.0)

    def test_cn05_rango_invertido(self):
        r = self.pedir("desde=2026-11-30&hasta=2026-11-01&formato=pdf")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "La fecha de inicio no puede ser posterior a la fecha de fin.")

    def test_cn06_fecha_mal_escrita(self):
        r = self.pedir("desde=01-11-2026&hasta=2026-11-30&formato=pdf")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "Formato de fecha inválido. Use AAAA-MM-DD.")

    def test_cn07_formato_no_permitido(self):
        r = self.pedir(RANGO + "&formato=docx")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "El formato debe ser csv, json o pdf.")

    def test_cn08_sin_sesion(self):
        self.assertEqual(self.pedir(RANGO + "&formato=pdf", con_sesion=False).status_code, 401)
