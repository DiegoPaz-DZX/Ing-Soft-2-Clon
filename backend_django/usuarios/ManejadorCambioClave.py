import json

from django.http import HttpResponse, JsonResponse
from django.views import View


class ManejadorCambioClave(View):
    http_method_names = ["post", "options"]
    servicio = None

    def post(self, peticion):
        try:
            datos = json.loads(peticion.body or b"{}")
            accion = datos.get("accion")

            if accion == "generar":
                self.servicio.generar_codigo(datos.get("correo", ""))
                return JsonResponse({"mensaje": "El código fue enviado al correo indicado."})

            if accion == "cambiar":
                self.servicio.cambiar_clave(
                    datos.get("correo", ""),
                    datos.get("codigo", ""),
                    datos.get("nueva_clave", ""),
                    datos.get("confirmacion_clave", ""),
                )
                return JsonResponse({"mensaje": "Contraseña actualizada."})

            return JsonResponse({"error": "La acción no es válida."}, status=400)
        except (json.JSONDecodeError, ValueError) as error:
            return JsonResponse({"error": str(error)}, status=400)
        except RuntimeError as error:
            return JsonResponse({"error": str(error)}, status=503)

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type"
        return respuesta
