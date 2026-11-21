from config.ConversorJson import ConversorJson
from config.ManejadorBase import ManejadorBase
from usuarios.TokenInvalidoException import TokenInvalidoException
from django.http import JsonResponse


class ManejadorBalance(ManejadorBase):
    servicio_tokens = None
    def obtener_datos(self):
        cabecera = self.request.headers.get('Authorization', '')
        if not cabecera.startswith('Bearer '):
            raise TokenInvalidoException('La sesión es obligatoria.')
        token = cabecera.removeprefix('Bearer ').strip()
        cuenta = self.servicio_tokens.obtener_cuenta(token)
        return ConversorJson.tarjetas_a_dict(self.servicio.obtener_tarjetas(cuenta))
    def get(self, peticion):
        try:
            return super().get(peticion)
        except TokenInvalidoException as error:
            return JsonResponse({'error': str(error)}, status = 401)