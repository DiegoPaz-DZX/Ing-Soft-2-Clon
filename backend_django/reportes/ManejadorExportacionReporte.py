from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views import View
from config.AutenticacionPeticion import obtener_token
from usuarios.TokenInvalidoException import TokenInvalidoException
from .ErrorGeneracionReporteException import ErrorGeneracionReporteException
from .FormatoNoSoportadoException import FormatoNoSoportadoException


class ManejadorExportacionReporte(View):
    http_method_names = ["get", "options"]
    servicio = None
    servicio_tokens = None

    def get(self, peticion):
        hoy = timezone.localdate()
        try:
            cuenta = self.servicio_tokens.obtener_cuenta(obtener_token(peticion))
            formato = peticion.GET.get("formato", "pdf")
            anio = int(peticion.GET.get("anio", hoy.year))
            mes = int(peticion.GET.get("mes", hoy.month))
            contenido, tipo, nombre = self.servicio.exportar_mensual(cuenta, formato, anio, mes)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except FormatoNoSoportadoException as error:
            return JsonResponse({"error": str(error)}, status=400)
        except ValueError:
            return JsonResponse({"error": "El año o el mes no son válidos."}, status=400)
        except ErrorGeneracionReporteException as error:
            return JsonResponse({"error": str(error)}, status=500, json_dumps_params={"ensure_ascii": False})

        respuesta = HttpResponse(contenido, content_type=tipo)
        respuesta["Content-Disposition"] = "attachment; filename=" + nombre
        return respuesta

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        respuesta["Access-Control-Expose-Headers"] = "Content-Disposition"
        return respuesta