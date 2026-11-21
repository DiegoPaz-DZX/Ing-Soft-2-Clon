from datetime import date

from django.http import JsonResponse

from config.AutenticacionPeticion import obtener_token
from config.ManejadorBase import ManejadorBase
from usuarios.TokenInvalidoException import TokenInvalidoException


class ManejadorProyeccion(ManejadorBase):
    servicio_tokens = None

    def obtener_datos(self):
        cuenta = self.servicio_tokens.obtener_cuenta(obtener_token(self.request))
        return self.servicio.proyectar(date.today(), cuenta).a_dict()

    def get(self, peticion):
        try:
            return super().get(peticion)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
