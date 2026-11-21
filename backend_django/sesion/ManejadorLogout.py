from django.http import HttpResponse, JsonResponse
from django.views import View

from usuarios.TokenInvalidoException import TokenInvalidoException


class ManejadorLogout(View):
    http_method_names = ["post", "options"]
    servicio_tokens = None

    def post(self, peticion):
        autorizacion = peticion.headers.get("Authorization", "")
        if not autorizacion.startswith("Bearer "):
            return JsonResponse({"error": "La sesión es obligatoria."}, status=401)
        try:
            self.servicio_tokens.revocar(autorizacion.removeprefix("Bearer ").strip())
            return JsonResponse({"mensaje": "Sesión cerrada."})
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta
