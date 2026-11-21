from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .ConversorDolares import ConversorDolares
from .ConversorSoles import ConversorSoles
from .CuentaNoEncontradaException import CuentaNoEncontradaException
from .Divisa import Divisa
from .DivisaNoSoportadaException import DivisaNoSoportadaException
from .FabricaConversores import FabricaConversores
from .ProveedorTipoCambio import ProveedorTipoCambio
from .ProveedorTipoCambioApi import ProveedorTipoCambioApi
from .RepositorioPreferencias import RepositorioPreferencias
from .RepositorioPreferenciasDjango import RepositorioPreferenciasDjango
from .RepositorioTipoCambioDjango import RepositorioTipoCambioDjango
from .ServicioPreferencias import ServicioPreferencias
from .ServicioTipoCambio import ServicioTipoCambio
from .TipoCambio import TipoCambio
from .TipoCambioDiario import TipoCambioDiario
from .TipoCambioNoDisponibleException import TipoCambioNoDisponibleException

HOY = date(2026, 10, 10)
AYER = date(2026, 10, 9)


def crear_cuenta(correo="mathias@correo.com"):
    cuenta = CuentaUsuario(correo=correo)
    cuenta.definir_clave("Kyzen2026")
    cuenta.save()
    return cuenta


class ProveedorFalso(ProveedorTipoCambio):
    nombre = "proveedor-falso"

    def __init__(self, valor):
        self._valor = Decimal(valor)
        self.consultas = 0

    def obtener_soles_por_dolar(self):
        self.consultas += 1
        return self._valor


class ProveedorCaido(ProveedorTipoCambio):
    nombre = "proveedor-caido"

    def obtener_soles_por_dolar(self):
        raise TipoCambioNoDisponibleException("sin conexión")


def crear_servicio_tipo_cambio(proveedor=None):
    return ServicioTipoCambio(proveedor or ProveedorFalso("3.5000"), RepositorioTipoCambioDjango(), "3.75")


class ConversoresTests(TestCase):
    def test_soles_no_cambia_el_monto(self):
        self.assertEqual(ConversorSoles().convertir(Decimal("150.50")), Decimal("150.50"))

    def test_dolares_divide_entre_el_tipo_de_cambio(self):
        self.assertEqual(ConversorDolares("3.75").convertir(Decimal("375")), Decimal("100.00"))
        self.assertEqual(ConversorDolares("3.75").convertir(Decimal("10")), Decimal("2.67"))

    def test_la_fabrica_crea_el_conversor_de_cada_divisa(self):
        self.assertIsInstance(FabricaConversores.crear("PEN", Decimal("4")), ConversorSoles)
        dolares = FabricaConversores.crear("USD", Decimal("4"))
        self.assertIsInstance(dolares, ConversorDolares)
        self.assertEqual(dolares.soles_por_unidad(), Decimal("4"))

    def test_la_fabrica_rechaza_divisas_desconocidas(self):
        with self.assertRaises(DivisaNoSoportadaException):
            FabricaConversores.crear("EUR", Decimal("4"))


class ServicioTipoCambioTests(TestCase):
    def test_consulta_al_proveedor_y_guarda_el_valor_del_dia(self):
        proveedor = ProveedorFalso("3.4422")
        tipo_cambio = crear_servicio_tipo_cambio(proveedor).obtener_del_dia(HOY)
        self.assertEqual(tipo_cambio.soles_por_dolar, Decimal("3.4422"))
        self.assertEqual(tipo_cambio.fecha, HOY)
        self.assertEqual(tipo_cambio.fuente, "proveedor-falso")
        self.assertEqual(TipoCambioDiario.objects.count(), 1)

    def test_el_mismo_dia_no_vuelve_a_consultar(self):
        proveedor = ProveedorFalso("3.4422")
        servicio = crear_servicio_tipo_cambio(proveedor)
        servicio.obtener_del_dia(HOY)
        servicio.obtener_del_dia(HOY)
        self.assertEqual(proveedor.consultas, 1)

    def test_al_dia_siguiente_se_actualiza(self):
        crear_servicio_tipo_cambio(ProveedorFalso("3.4000")).obtener_del_dia(AYER)
        tipo_cambio = crear_servicio_tipo_cambio(ProveedorFalso("3.4600")).obtener_del_dia(HOY)
        self.assertEqual(tipo_cambio.soles_por_dolar, Decimal("3.4600"))
        self.assertEqual(TipoCambioDiario.objects.count(), 2)

    def test_si_el_proveedor_falla_usa_el_ultimo_valor_guardado(self):
        crear_servicio_tipo_cambio(ProveedorFalso("3.4000")).obtener_del_dia(AYER)
        tipo_cambio = crear_servicio_tipo_cambio(ProveedorCaido()).obtener_del_dia(HOY)
        self.assertEqual(tipo_cambio.soles_por_dolar, Decimal("3.4000"))
        self.assertEqual(tipo_cambio.fecha, AYER)

    def test_si_falla_y_no_hay_nada_guardado_usa_el_valor_referencial(self):
        tipo_cambio = crear_servicio_tipo_cambio(ProveedorCaido()).obtener_del_dia(HOY)
        self.assertEqual(tipo_cambio.soles_por_dolar, Decimal("3.75"))
        self.assertEqual(tipo_cambio.fuente, "Valor referencial")
        self.assertEqual(TipoCambioDiario.objects.count(), 0)

    def test_el_servicio_devuelve_un_tipo_de_cambio_y_no_el_modelo(self):
        tipo_cambio = crear_servicio_tipo_cambio().obtener_del_dia(HOY)
        self.assertIsInstance(tipo_cambio, TipoCambio)
        self.assertEqual(tipo_cambio.soles_por_dolar, Decimal("3.5000"))


class RespuestaFalsa:
    def __init__(self, contenido):
        self._contenido = contenido

    def read(self):
        return self._contenido

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ProveedorTipoCambioApiTests(TestCase):
    def consultar(self, contenido):
        with patch("preferencias.ProveedorTipoCambioApi.urlopen", return_value=RespuestaFalsa(contenido)):
            return ProveedorTipoCambioApi("https://ejemplo.test").obtener_soles_por_dolar()

    def test_lee_el_valor_del_sol_de_la_respuesta(self):
        self.assertEqual(self.consultar(b'{"rates": {"PEN": 3.442249}}'), Decimal("3.4422"))

    def test_respuestas_invalidas_lanzan_error(self):
        for contenido in [b"no es json", b'{"rates": {}}', b'{"rates": {"PEN": 0}}', b'{"rates": {"PEN": "x"}}']:
            with self.subTest(contenido=contenido):
                with self.assertRaises(TipoCambioNoDisponibleException):
                    self.consultar(contenido)

    def test_sin_conexion_lanza_error(self):
        with patch("preferencias.ProveedorTipoCambioApi.urlopen", side_effect=TimeoutError()):
            with self.assertRaises(TipoCambioNoDisponibleException):
                ProveedorTipoCambioApi("https://ejemplo.test").obtener_soles_por_dolar()


class ServicioPreferenciasTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()
        self.servicio = ServicioPreferencias(RepositorioPreferenciasDjango(), crear_servicio_tipo_cambio())

    def test_la_divisa_por_defecto_es_soles(self):
        preferencia = self.servicio.obtener_preferencia(self.cuenta.pk)
        self.assertEqual(preferencia.divisa.codigo, "PEN")
        self.assertEqual([opcion.codigo for opcion in preferencia.opciones], ["PEN", "USD"])

    def test_guarda_la_divisa_elegida(self):
        self.servicio.cambiar_divisa(self.cuenta.pk, "usd")
        self.assertEqual(self.servicio.obtener_preferencia(self.cuenta.pk).divisa.codigo, "USD")
        self.servicio.cambiar_divisa(self.cuenta.pk, "PEN")
        self.assertEqual(self.servicio.obtener_preferencia(self.cuenta.pk).divisa.codigo, "PEN")

    def test_los_dolares_usan_el_tipo_de_cambio_del_dia(self):
        preferencia = self.servicio.cambiar_divisa(self.cuenta.pk, "USD")
        self.assertEqual(preferencia.divisa.soles_por_unidad(), Decimal("3.5000"))
        self.assertEqual(preferencia.divisa.convertir(Decimal("350")), Decimal("100.00"))
        self.assertEqual(preferencia.tipo_cambio.fuente, "proveedor-falso")

    def test_cada_cuenta_tiene_su_propia_preferencia(self):
        otra = crear_cuenta("otra@correo.com")
        self.servicio.cambiar_divisa(self.cuenta.pk, "USD")
        self.assertEqual(self.servicio.obtener_preferencia(otra.pk).divisa.codigo, "PEN")

    def test_rechaza_divisas_no_soportadas_y_cuentas_inexistentes(self):
        with self.assertRaises(DivisaNoSoportadaException):
            self.servicio.cambiar_divisa(self.cuenta.pk, "EUR")
        with self.assertRaises(CuentaNoEncontradaException):
            self.servicio.cambiar_divisa(9999, "USD")
        with self.assertRaises(CuentaNoEncontradaException):
            self.servicio.obtener_preferencia(9999)


class RepositorioFalso(RepositorioPreferencias):
    def __init__(self):
        self._divisas = {}

    def existe_cuenta(self, cuenta_id):
        return cuenta_id == 1

    def obtener_divisa(self, cuenta_id):
        return self._divisas.get(cuenta_id)

    def guardar_divisa(self, cuenta_id, divisa):
        self._divisas[cuenta_id] = divisa


class ServicioConRepositorioFalsoTests(TestCase):
    def test_el_servicio_funciona_con_cualquier_repositorio(self):
        servicio = ServicioPreferencias(RepositorioFalso(), crear_servicio_tipo_cambio())
        servicio.cambiar_divisa(1, Divisa.USD)
        self.assertEqual(servicio.obtener_preferencia(1).divisa.simbolo, "$")


@patch.object(ProveedorTipoCambioApi, "obtener_soles_por_dolar", return_value=Decimal("3.5000"))
class PreferenciaMonedaEndpointTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta()

    def sesion(self, cuenta=None):
        token = ServicioTokens(RepositorioCuentasDjango()).crear(cuenta or self.cuenta)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def consultar(self, cuenta=None):
        return self.client.get("/api/preferencias/moneda", **self.sesion(cuenta))

    def cambiar(self, divisa, cuenta=None):
        return self.client.put(
            "/api/preferencias/moneda",
            data={"divisa": divisa},
            content_type="application/json",
            **self.sesion(cuenta),
        )

    def test_devuelve_la_divisa_las_opciones_y_el_tipo_de_cambio(self, proveedor):
        respuesta = self.consultar()
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["divisa"]["codigo"], "PEN")
        self.assertEqual(datos["divisa"]["simbolo"], "S/")
        self.assertEqual([opcion["codigo"] for opcion in datos["opciones"]], ["PEN", "USD"])
        self.assertEqual(datos["tipoCambio"]["solesPorDolar"], 3.5)
        self.assertEqual(datos["tipoCambio"]["fuente"], "open.er-api.com")
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_cambia_la_divisa_y_la_recuerda(self, proveedor):
        respuesta = self.cambiar("USD")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["divisa"]["nombre"], "Dólares")
        self.assertEqual(respuesta.json()["divisa"]["solesPorUnidad"], 3.5)
        self.assertEqual(self.consultar().json()["divisa"]["codigo"], "USD")
        self.assertEqual(proveedor.call_count, 1)

    def test_la_cuenta_sale_de_la_sesion_y_no_del_cuerpo(self, proveedor):
        otra = crear_cuenta("otra@correo.com")
        self.client.put(
            "/api/preferencias/moneda",
            data={"cuenta": otra.pk, "divisa": "USD"},
            content_type="application/json",
            **self.sesion(),
        )
        self.assertEqual(self.consultar().json()["divisa"]["codigo"], "USD")
        self.assertEqual(self.consultar(otra).json()["divisa"]["codigo"], "PEN")

    def test_sin_sesion_o_con_token_invalido_responde_401(self, proveedor):
        self.assertEqual(self.client.get("/api/preferencias/moneda").status_code, 401)
        self.assertEqual(self.client.get("/api/preferencias/moneda?cuenta=1").status_code, 401)
        invalido = self.client.get("/api/preferencias/moneda", HTTP_AUTHORIZATION="Bearer token-falso")
        self.assertEqual(invalido.status_code, 401)
        cambio = self.client.put(
            "/api/preferencias/moneda", data={"divisa": "USD"}, content_type="application/json"
        )
        self.assertEqual(cambio.status_code, 401)

    def test_divisa_invalida_responde_400(self, proveedor):
        respuesta = self.cambiar("EUR")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("Soles", respuesta.json()["error"])

    def test_permite_la_cabecera_de_autorizacion(self, proveedor):
        respuesta = self.client.options("/api/preferencias/moneda")
        self.assertEqual(respuesta.status_code, 204)
        self.assertIn("Authorization", respuesta["Access-Control-Allow-Headers"])

    def test_metodos_no_permitidos(self, proveedor):
        self.assertEqual(self.client.post("/api/preferencias/moneda", **self.sesion()).status_code, 405)
