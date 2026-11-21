"""Pruebas de Raúl para la sección 10.6.6 del informe (HU9).

Prueba unitaria de ServicioAlertas.generar_alertas(), sección 10.6.6,
Tabla 94 (casos U-1 a U-6).

Si se ejecuta con KYZEN_REPORTE=1 también imprime una línea por caso para
copiar los resultados al informe sin cambiar la lógica de las pruebas.
"""

import os
from datetime import date
from decimal import Decimal

from django.test import TestCase

from usuarios.CuentaUsuario import CuentaUsuario

from config.FabricaServicios import FabricaServicios
from balance.Movimiento import Movimiento
from balance.TipoMovimiento import TipoMovimiento

REPORTE = os.environ.get("KYZEN_REPORTE") == "1"


def mostrar(caso, escenario, esperado, obtenido):
    if REPORTE:
        print(f"REPORTE|{caso}|{escenario}|{esperado}|{obtenido}")


class ServicioAlertasUnitariasTests(TestCase):
    """Tabla 94. Casos de prueba unitaria de generar_alertas() (HU9)."""

    def setUp(self):
        self.cuenta = CuentaUsuario.objects.create(correo="raul-u@correo.com", clave_hash="x")
        self.servicio = FabricaServicios.crear_servicio_alertas()

    def registrar_gasto(self, cuenta, categoria, monto):
        return Movimiento.objects.create(
            tipo=TipoMovimiento.GASTO,
            monto=Decimal(monto),
            fecha=date.today(),
            descripcion="prueba",
            categoria=categoria,
            moneda="PEN",
            usuario=cuenta,
        )

    def test_u1_sin_limites_configurados(self):
        alertas = self.servicio.generar_alertas(self.cuenta)
        self.assertEqual(alertas, [])
        mostrar("U-1", "Sin límites configurados", "Lista vacía", alertas)

    def test_u2_gasto_al_50_por_ciento_del_limite(self):
        self.servicio.establecer_limite(self.cuenta, "comida", "100")
        self.registrar_gasto(self.cuenta, "comida", "50")
        alertas = self.servicio.generar_alertas(self.cuenta)
        self.assertEqual(alertas, [])
        mostrar("U-2", "Gasto de comida al 50 % del límite", "Lista vacía", alertas)

    def test_u3_gasto_al_80_por_ciento_con_advertencia_pendiente(self):
        self.servicio.establecer_limite(self.cuenta, "comida", "100")
        self.registrar_gasto(self.cuenta, "comida", "80")
        self.servicio.generar_alertas(self.cuenta)
        alertas = self.servicio.generar_alertas(self.cuenta)
        tipos = [a.tipo_alerta.value for a in alertas]
        self.assertEqual(tipos, ["advertencia"])
        mostrar("U-3", "Gasto al 80 % y ya existe una ADVERTENCIA pendiente",
                "Sigue una sola ADVERTENCIA, sin duplicar", tipos)

    def test_u4_gasto_al_80_por_ciento_sin_alertas_previas(self):
        self.servicio.establecer_limite(self.cuenta, "comida", "100")
        self.registrar_gasto(self.cuenta, "comida", "80")
        alertas = self.servicio.generar_alertas(self.cuenta)
        tipos = [a.tipo_alerta.value for a in alertas]
        self.assertEqual(tipos, ["advertencia"])
        mostrar("U-4", "Gasto al 80 % sin alertas previas", "Se guarda una ADVERTENCIA", tipos)

    def test_u5_gasto_al_120_por_ciento_con_critica_pendiente(self):
        self.servicio.establecer_limite(self.cuenta, "comida", "100")
        self.registrar_gasto(self.cuenta, "comida", "120")
        self.servicio.generar_alertas(self.cuenta)
        alertas = self.servicio.generar_alertas(self.cuenta)
        tipos = [a.tipo_alerta.value for a in alertas]
        self.assertEqual(tipos, ["critica"])
        mostrar("U-5", "Gasto al 120 % y ya existe una CRITICA pendiente",
                "Sigue una sola CRITICA, sin duplicar", tipos)

    def test_u6_gasto_sobre_el_120_por_ciento_guarda_critica(self):
        self.servicio.establecer_limite(self.cuenta, "comida", "100")
        self.registrar_gasto(self.cuenta, "comida", "120")
        alertas = self.servicio.generar_alertas(self.cuenta)
        self.assertEqual([a.tipo_alerta.value for a in alertas], ["critica"])
        mostrar("U-6", "Gasto al 120 % sin alertas previas", "Se guarda una CRITICA",
                [a.tipo_alerta.value for a in alertas])