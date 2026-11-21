import json

from django.http import JsonResponse

from config.AutenticacionPeticion import obtener_token
from config.ManejadorBase import ManejadorBase
from usuarios.TokenInvalidoException import TokenInvalidoException


class ManejadorLimites(ManejadorBase):
    http_method_names = ["get", "post", "options"]
    servicio = None
    servicio_tokens = None

    def post(self, peticion):
        try:
            cuenta = self.servicio_tokens.obtener_cuenta(obtener_token(peticion))
            datos = json.loads(peticion.body or b"{}")
            self.servicio.establecer_limite(cuenta, datos.get("categoria"), datos.get("limite_mensual"))
            return JsonResponse({"exito": True, "mensaje": "Límite establecido"})
        except TokenInvalidoException as error:
            return JsonResponse({"exito": False, "error": str(error)}, status=401)
        except Exception as error:
            return JsonResponse({"exito": False, "error": str(error)}, status=400)

    def get(self, peticion):
        try:
            return super().get(peticion)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)

    def obtener_datos(self):
        cuenta = self.servicio_tokens.obtener_cuenta(obtener_token(self.request))
        return self.servicio.obtener_limites(cuenta)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return respuesta
