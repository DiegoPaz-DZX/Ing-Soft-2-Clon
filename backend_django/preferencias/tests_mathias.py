
from datetime import date
from decimal import Decimal

from django.test import TestCase

from .ConversorDolares import ConversorDolares
from .ConversorSoles import ConversorSoles
from .DivisaNoSoportadaException import DivisaNoSoportadaException
from .FabricaConversores import FabricaConversores
from .ProveedorTipoCambio import ProveedorTipoCambio
from .RepositorioTipoCambioDjango import RepositorioTipoCambioDjango
from .ServicioTipoCambio import ServicioTipoCambio
from .TipoCambioDiario import TipoCambioDiario
from .TipoCambioNoDisponibleException import TipoCambioNoDisponibleException

LUNES = date(2026, 11, 2)
MARTES = date(2026, 11, 3)


class ProveedorQueCuenta(ProveedorTipoCambio):
    nombre = "proveedor-de-prueba"

    def __init__(self, valor):
        self.valor = Decimal(valor)
        self.consultas = 0

    def obtener_soles_por_dolar(self):
        self.consultas += 1
        return self.valor


class ProveedorSinConexion(ProveedorTipoCambio):
    nombre = "sin-conexion"

    def obtener_soles_por_dolar(self):
        raise TipoCambioNoDisponibleException("sin conexión")


def servicio(proveedor):
    return ServicioTipoCambio(proveedor, RepositorioTipoCambioDjango(), "3.75")


class ObtenerDelDiaTests(TestCase):
    def test_pu01_primera_consulta_del_dia_guarda_el_valor(self):
        tipo = servicio(ProveedorQueCuenta("3.7012")).obtener_del_dia(LUNES)
        self.assertEqual(tipo.soles_por_dolar, Decimal("3.7012"))
        self.assertEqual(TipoCambioDiario.objects.filter(fecha=LUNES).count(), 1)

    def test_pu02_segunda_consulta_del_mismo_dia_no_llama_al_proveedor(self):
        proveedor = ProveedorQueCuenta("3.7012")
        s = servicio(proveedor)
        s.obtener_del_dia(LUNES)
        s.obtener_del_dia(LUNES)
        s.obtener_del_dia(LUNES)
        self.assertEqual(proveedor.consultas, 1)

    def test_pu03_un_dia_nuevo_consulta_otra_vez(self):
        servicio(ProveedorQueCuenta("3.7000")).obtener_del_dia(LUNES)
        tipo = servicio(ProveedorQueCuenta("3.7100")).obtener_del_dia(MARTES)
        self.assertEqual(tipo.soles_por_dolar, Decimal("3.7100"))
        self.assertEqual(TipoCambioDiario.objects.count(), 2)

    def test_pu04_sin_conexion_usa_el_ultimo_valor_guardado(self):
        servicio(ProveedorQueCuenta("3.7000")).obtener_del_dia(LUNES)
        tipo = servicio(ProveedorSinConexion()).obtener_del_dia(MARTES)
        self.assertEqual(tipo.soles_por_dolar, Decimal("3.7000"))
        self.assertEqual(tipo.fecha, LUNES)

    def test_pu05_sin_conexion_y_sin_historial_usa_el_valor_de_respaldo(self):
        tipo = servicio(ProveedorSinConexion()).obtener_del_dia(MARTES)
        self.assertEqual(tipo.soles_por_dolar, Decimal("3.75"))
        self.assertEqual(TipoCambioDiario.objects.count(), 0)

    def test_pu06_el_valor_de_respaldo_no_se_guarda_como_dato_real(self):
        servicio(ProveedorSinConexion()).obtener_del_dia(MARTES)
        tipo = servicio(ProveedorQueCuenta("3.6900")).obtener_del_dia(MARTES)
        self.assertEqual(tipo.soles_por_dolar, Decimal("3.6900"))


class ConversionDeMontosTests(TestCase):
    def test_soles_no_cambia_el_monto(self):
        self.assertEqual(ConversorSoles().convertir(Decimal("350.00")), Decimal("350.00"))

    def test_dolares_divide_entre_el_tipo_de_cambio_y_redondea(self):
        self.assertEqual(ConversorDolares("3.75").convertir(Decimal("100")), Decimal("26.67"))

    def test_la_fabrica_rechaza_otras_divisas(self):
        with self.assertRaises(DivisaNoSoportadaException):
            FabricaConversores.crear("EUR", Decimal("3.75"))
