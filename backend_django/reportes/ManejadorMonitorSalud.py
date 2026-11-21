from django.http import JsonResponse

from config.ManejadorBase import ManejadorBase
from usuarios.TokenInvalidoException import TokenInvalidoException


class ManejadorMonitorSalud(ManejadorBase):
    servicio = None
    servicio_tokens = None

    def obtener_datos(self):
        autorizacion = self.request.headers.get("Authorization", "")
        if not autorizacion.startswith("Bearer "):
            raise TokenInvalidoException("La sesión es obligatoria.")

        token = autorizacion.removeprefix("Bearer ").strip()
        cuenta = self.servicio_tokens.obtener_cuenta(token)
        return self.servicio.evaluar(cuenta)

    def get(self, peticion):
        try:
            return super().get(peticion)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)