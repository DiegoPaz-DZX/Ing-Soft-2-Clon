from django.conf import settings

from balance.RepositorioMovimientosDjango import RepositorioMovimientosDjango
from balance.ServicioBalance import ServicioBalance
from balance.ServicioImportacionMovimientos import ServicioImportacionMovimientos
from balance.ServicioMovimientos import ServicioMovimientos
from categorias.RepositorioCategoriasMemoria import RepositorioCategoriasMemoria
from categorias.ServicioCategorias import ServicioCategorias
from tips.RepositorioTipsMemoria import RepositorioTipsMemoria
from tips.ServicioTips import ServicioTips
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioRegistro import ServicioRegistro
from usuarios.ServicioCambioClave import ServicioCambioClave
from usuarios.ServicioCorreoResend import ServicioCorreoResend
from usuarios.RepositorioCodigosCambioClaveDjango import RepositorioCodigosCambioClaveDjango
from usuarios.ServicioAdministracionUsuarios import ServicioAdministracionUsuarios
from usuarios.ServicioTokens import ServicioTokens
from alertas.RepositorioLimitesDjango import RepositorioLimitesDjango
from alertas.RepositorioAlertasDjango import RepositorioAlertasDjango
from alertas.ServicioAlertas import ServicioAlertas
from historial.HistorialMovimientos import HistorialMovimientos
from historial.RepositorioHistorialDjango import RepositorioHistorialDjango
from sesion.AutenticacionPorCuenta import AutenticacionPorCuenta
from sesion.ProveedorAutenticacion import ProveedorAutenticacion
from sesion.RepositorioTokensRevocadosDjango import RepositorioTokensRevocadosDjango
from recomendaciones.ServicioRecomendaciones import ServicioRecomendaciones
from preferencias.ProveedorTipoCambioApi import ProveedorTipoCambioApi
from preferencias.RepositorioPreferenciasDjango import RepositorioPreferenciasDjango
from preferencias.RepositorioTipoCambioDjango import RepositorioTipoCambioDjango
from preferencias.ServicioPreferencias import ServicioPreferencias
from preferencias.ServicioTipoCambio import ServicioTipoCambio
from reportes.FabricaReglasAnalisis import FabricaReglasAnalisis
from reportes.ServicioReportes import ServicioReportes
from metas.MetaAhorroFacade import MetaAhorroFacade
from metas.RepositorioMetas import RepositorioMetas
from metas.ServicioMetas import ServicioMetas


class FabricaServicios:
    @staticmethod
    def crear_servicio_balance():
        return ServicioBalance(
            RepositorioMovimientosDjango(),
            settings.TIPO_CAMBIO_SOLES_POR_DOLAR,
        )

    @staticmethod
    def crear_servicio_movimientos():
        return ServicioMovimientos(RepositorioMovimientosDjango())

    @staticmethod
    def crear_servicio_importacion_movimientos():
        repositorio = RepositorioMovimientosDjango()
        return ServicioImportacionMovimientos(
            repositorio,
            ServicioMovimientos(repositorio),
        )

    @staticmethod
    def crear_servicio_tips():
        return ServicioTips(RepositorioTipsMemoria())

    @staticmethod
    def crear_servicio_categorias():
        return ServicioCategorias(RepositorioCategoriasMemoria())

    @staticmethod
    def crear_servicio_registro():
        return ServicioRegistro(RepositorioCuentasDjango())

    @staticmethod
    def crear_servicio_cambio_clave():
        return ServicioCambioClave(
            RepositorioCuentasDjango(),
            RepositorioCodigosCambioClaveDjango(),
            ServicioCorreoResend(),
        )

    @staticmethod
    def crear_facade_metas():
        return MetaAhorroFacade(
            ServicioMetas(RepositorioMetas()),
            FabricaServicios.crear_servicio_tokens(),
        )

    @staticmethod
    def crear_servicio_administracion_usuarios():
        repositorio = RepositorioCuentasDjango()
        return ServicioAdministracionUsuarios(repositorio, ServicioTokens(repositorio))

    @staticmethod
    def crear_servicio_tokens():
        repositorio = RepositorioCuentasDjango()
        return ServicioTokens(
            repositorio,
            RepositorioTokensRevocadosDjango(),
        )

    @staticmethod
    def crear_servicio_alertas():
        return ServicioAlertas(
            repositorio_limites=RepositorioLimitesDjango(),
            repositorio_alertas=RepositorioAlertasDjango(),
            repositorio_movimientos=RepositorioMovimientosDjango()
    )

    @staticmethod
    def crear_historial_movimientos():
        return HistorialMovimientos(RepositorioHistorialDjango())

    @staticmethod
    def crear_proveedor_autenticacion():
        return ProveedorAutenticacion(AutenticacionPorCuenta(RepositorioCuentasDjango()))

    @staticmethod
    def crear_servicio_recomendaciones():
        return ServicioRecomendaciones(
            RepositorioMovimientosDjango(),
            FabricaServicios.crear_servicio_categorias(),
        )

    @staticmethod
    def crear_servicio_tipo_cambio():
        return ServicioTipoCambio(
            ProveedorTipoCambioApi(settings.TIPO_CAMBIO_URL),
            RepositorioTipoCambioDjango(),
            settings.TIPO_CAMBIO_SOLES_POR_DOLAR,
        )

    @staticmethod
    def crear_servicio_preferencias():
        return ServicioPreferencias(
            RepositorioPreferenciasDjango(),
            FabricaServicios.crear_servicio_tipo_cambio(),
        )

    @staticmethod
    def crear_servicio_reportes():
        return ServicioReportes(
            FabricaServicios.crear_historial_movimientos(),
            FabricaServicios.crear_servicio_categorias(),
            FabricaServicios.crear_servicio_tipo_cambio(),
            FabricaReglasAnalisis.crear_todas(),
        )
