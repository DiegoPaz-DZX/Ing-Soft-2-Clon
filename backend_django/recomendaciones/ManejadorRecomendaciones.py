from django.http import JsonResponse
from config.ConversorJson import ConversorJson
from config.ManejadorBase import ManejadorBase
from usuarios.TokenInvalidoException import TokenInvalidoException

class ManejadorRecomendaciones(ManejadorBase):
    servicio_tokens = None
    def obtener_datos(self):
        autorizacion = self.request.headers.get('Authorization', '')

        if not autorizacion.startswith('Bearer '):
            raise TokenInvalidoException('La sesión es obligatoria.')

        token = autorizacion.removeprefix('Bearer ').strip()
        cuenta = self.servicio_tokens.obtener_cuenta(token)

        recomendaciones = self.servicio.obtener_recomendaciones(cuenta)
        return ConversorJson.recomendaciones_a_lista(recomendaciones)

    def get(self, peticion):
        try:
            return super().get(peticion)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)