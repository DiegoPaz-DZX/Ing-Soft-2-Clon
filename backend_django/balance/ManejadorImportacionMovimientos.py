from django.http import HttpResponse, JsonResponse
from django.views import View

from config.AutenticacionPeticion import obtener_token
from usuarios.TokenInvalidoException import TokenInvalidoException

from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException


class ManejadorImportacionMovimientos(View):
    http_method_names = ["post", "options"]
    servicio = None
    servicio_tokens = None

    def post(self, peticion):
        try:
            cuenta = self.servicio_tokens.obtener_cuenta(obtener_token(peticion))
            movimientos = self.servicio.importar(cuenta, peticion.FILES.get("archivo"))
            return JsonResponse(
                {"importados": len(movimientos), "mensaje": "Movimientos importados correctamente."},
                status=201,
            )
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except ArchivoImportacionInvalidoException as error:
            return JsonResponse({"error": str(error), "errores": error.errores}, status=400)

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta
