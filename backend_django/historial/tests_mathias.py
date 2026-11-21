
import json
from datetime import date
from types import SimpleNamespace

from django.test import TestCase

from .FiltroPorRangoFechas import FiltroPorRangoFechas
from .RangoFechasInvalidoException import RangoFechasInvalidoException

DESDE = date(2026, 10, 1)
HASTA = date(2026, 10, 31)


def movimiento(fecha):
    return SimpleNamespace(fecha=fecha)


class FiltroPorRangoFechasTests(TestCase):
    def setUp(self):
        self.filtro = FiltroPorRangoFechas(DESDE, HASTA)

    def test_incluye_el_primer_dia_del_rango(self):
        self.assertTrue(self.filtro.cumple(movimiento(DESDE)))

    def test_incluye_el_ultimo_dia_del_rango(self):
        self.assertTrue(self.filtro.cumple(movimiento(HASTA)))

    def test_excluye_el_dia_anterior_al_rango(self):
        self.assertFalse(self.filtro.cumple(movimiento(date(2026, 9, 30))))

    def test_excluye_el_dia_posterior_al_rango(self):
        self.assertFalse(self.filtro.cumple(movimiento(date(2026, 11, 1))))

    def test_acepta_un_rango_de_un_solo_dia(self):
        filtro = FiltroPorRangoFechas(DESDE, DESDE)
        self.assertTrue(filtro.cumple(movimiento(DESDE)))

    def test_rechaza_rango_invertido(self):
        with self.assertRaises(RangoFechasInvalidoException):
            FiltroPorRangoFechas(HASTA, DESDE)

    def test_rechaza_si_falta_una_fecha(self):
        with self.assertRaises(RangoFechasInvalidoException):
            FiltroPorRangoFechas(DESDE, None)
        with self.assertRaises(RangoFechasInvalidoException):
            FiltroPorRangoFechas(None, HASTA)


class HistorialFiltradoEndpointTests(TestCase):
    def crear_usuario(self, correo):
        j = "application/json"
        self.client.post("/api/registro", json.dumps({"correo": correo, "clave": "Clave123!", "confirmacion": "Clave123!"}), content_type=j)
        token = self.client.post("/api/login", json.dumps({"correo": correo, "clave": "Clave123!"}), content_type=j).json()["token"]
        return {"HTTP_AUTHORIZATION": "Bearer " + token}

    def registrar(self, cabecera, fecha):
        self.client.post(
            "/api/movimientos/nuevo",
            json.dumps({"tipo": "ingreso", "monto": "100", "fecha": fecha, "descripcion": "x", "categoria": "", "moneda": "PEN"}),
            content_type="application/json",
            **cabecera,
        )

    def setUp(self):
        self.a = self.crear_usuario("a@correo.com")
        self.b = self.crear_usuario("b@correo.com")
        for fecha in ("2026-09-30", "2026-10-01", "2026-10-31", "2026-11-01"):
            self.registrar(self.a, fecha)
        self.registrar(self.b, "2026-10-15")

    def test_devuelve_solo_los_movimientos_del_rango(self):
        respuesta = self.client.get("/api/movimientos?desde=2026-10-01&hasta=2026-10-31", **self.a)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(sorted(m["fecha"] for m in respuesta.json()), ["2026-10-01", "2026-10-31"])

    def test_no_muestra_movimientos_de_otra_cuenta(self):
        respuesta = self.client.get("/api/movimientos?desde=2026-10-01&hasta=2026-10-31", **self.b)
        self.assertEqual([m["fecha"] for m in respuesta.json()], ["2026-10-15"])

    def test_rango_invertido_responde_400(self):
        self.assertEqual(self.client.get("/api/movimientos?desde=2026-10-31&hasta=2026-10-01", **self.a).status_code, 400)

    def test_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get("/api/movimientos?desde=2026-10-01&hasta=2026-10-31").status_code, 401)
