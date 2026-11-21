import calendar
import logging
from datetime import date
from .ConvertidorReporte import ConvertidorReporte
from .ErrorGeneracionReporteException import ErrorGeneracionReporteException
from .ExportadorExcelMoneda import ExportadorExcelMoneda
from .ExportadorPdfMoneda import ExportadorPdfMoneda
from .FormatoNoSoportadoException import FormatoNoSoportadoException

logger = logging.getLogger(__name__)

MENSAJE_ERROR = "No se pudo generar el reporte, intente más tarde"


class ServicioExportacionReporte:
    """Contexto del patrón Strategy: elige el exportador (PDF, Excel...) según el formato pedido."""

    def __init__(self, servicio_reportes, servicio_preferencias, exportadores=None):
        self._reportes = servicio_reportes
        self._preferencias = servicio_preferencias
        # Para agregar un formato nuevo solo se agrega una entrada aquí (OCP).
        self._exportadores = exportadores or {
            "pdf": ExportadorPdfMoneda(),
            "excel": ExportadorExcelMoneda(),
        }

    def exportar_mensual(self, cuenta, formato, anio, mes):
        exportador = self._exportadores.get(str(formato).lower())
        if exportador is None:
            raise FormatoNoSoportadoException("El formato debe ser pdf o excel.")

        desde = date(anio, mes, 1)
        hasta = date(anio, mes, calendar.monthrange(anio, mes)[1])

        reporte = self._reportes.generar_reporte(desde, hasta, cuenta=cuenta)
        conversor = self._preferencias.obtener_preferencia(cuenta.pk).divisa  # divisa activa AHORA
        reporte_convertido = ConvertidorReporte(conversor).convertir(reporte)

        try:
            contenido = exportador.exportar(reporte_convertido)
        except Exception as error:
            logger.exception("Falló la generación del reporte")
            raise ErrorGeneracionReporteException(MENSAJE_ERROR) from error

        nombre = "reporte-" + str(anio) + "-" + format(mes, "02d") + "-" + conversor.codigo + "." + exportador.extension
        return contenido, exportador.tipo_contenido, nombre