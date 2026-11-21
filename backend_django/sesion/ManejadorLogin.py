import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from .CredencialesInvalidasException import CredencialesInvalidasException


class ManejadorLogin(View):
    http_method_names = ["post", "options"]
    servicio = None
    servicio_tokens = None

    def post(self, peticion):
        try:
            datos = json.loads(peticion.body or b"{}")
            cuenta = self.servicio.iniciar_sesion(datos.get("correo"), datos.get("clave"))
            return JsonResponse({
                "id": cuenta.pk,
                "correo": cuenta.correo,
                "rol": cuenta.rol,
                "token": self.servicio_tokens.crear(cuenta),
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "El contenido enviado no es válido."}, status=400)
        except CredencialesInvalidasException as error:
            return JsonResponse({"error": str(error)}, status=401)

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type"
        return respuesta
