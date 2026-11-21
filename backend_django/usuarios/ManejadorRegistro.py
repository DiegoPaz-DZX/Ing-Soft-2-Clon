import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from .CorreoRegistradoException import CorreoRegistradoException
from .DatosRegistroInvalidosException import DatosRegistroInvalidosException


class ManejadorRegistro(View):
    http_method_names = ["post", "options"]
    servicio = None

    def post(self, peticion):
        try:
            datos = json.loads(peticion.body or b"{}")
            cuenta = self.servicio.registrar(
                datos.get("correo"), datos.get("clave"), datos.get("confirmacion")
            )
            return JsonResponse({"id": cuenta.pk, "correo": cuenta.correo}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "El contenido enviado no es válido."}, status=400)
        except CorreoRegistradoException as error:
            return JsonResponse({"error": str(error)}, status=409)
        except DatosRegistroInvalidosException as error:
            return JsonResponse({"error": str(error)}, status=400)

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type"
        return respuesta
