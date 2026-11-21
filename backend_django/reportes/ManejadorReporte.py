from datetime import date

from django.http import HttpResponse, JsonResponse

from config.ManejadorBase import ManejadorBase
from historial.RangoFechasInvalidoException import RangoFechasInvalidoException
from sesion.MixinSesion import MixinSesion
from usuarios.TokenInvalidoException import TokenInvalidoException

from .ConversorReporte import ConversorReporte
from .FabricaExportadores import FabricaExportadores
from .FormatoNoSoportadoException import FormatoNoSoportadoException


class ManejadorReporte(MixinSesion, ManejadorBase):
    def get(self, peticion):
        try:
            formato = peticion.GET.get("formato")
            if formato is None:
                return super().get(peticion)
            return self._descargar(self._generar_reporte(), FabricaExportadores.crear(formato))
        except (RangoFechasInvalidoException, FormatoNoSoportadoException) as error:
            return JsonResponse({"error": str(error)}, status=400)
        except ValueError:
            return JsonResponse({"error": "Formato de fecha inválido. Use AAAA-MM-DD."}, status=400)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)

    def obtener_datos(self):
        return ConversorReporte.a_dict(self._generar_reporte())

    def _generar_reporte(self):
        cuenta = self.cuenta_de_la_sesion(self.request)
        parametros = self.request.GET
        return self.servicio.generar_reporte(
            self._convertir_fecha(parametros.get("desde")),
            self._convertir_fecha(parametros.get("hasta")),
            con_graficos=parametros.get("graficos", "1") != "0",
            con_analisis=parametros.get("analisis", "1") != "0",
            cuenta=cuenta,
        )

    def _descargar(self, reporte, exportador):
        respuesta = HttpResponse(exportador.exportar(reporte), content_type=exportador.tipo_contenido)
        nombre = "reporte-financiero-kyzen." + exportador.extension
        respuesta["Content-Disposition"] = "attachment; filename=" + nombre
        return respuesta

    def _convertir_fecha(self, texto):
        if not texto:
            return None
        return date.fromisoformat(texto)
