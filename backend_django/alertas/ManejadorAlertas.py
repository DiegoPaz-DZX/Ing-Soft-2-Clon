from django.http import JsonResponse

from config.AutenticacionPeticion import obtener_token
from config.ManejadorBase import ManejadorBase
from usuarios.TokenInvalidoException import TokenInvalidoException


class ManejadorAlertas(ManejadorBase):
    http_method_names = ["get", "options"]
    servicio = None
    servicio_tokens = None

    def obtener_datos(self):
        cuenta = self.servicio_tokens.obtener_cuenta(obtener_token(self.request))
        return [a.a_dict() for a in self.servicio.generar_alertas(cuenta)]

    def get(self, peticion):
        try:
            return super().get(peticion)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
