from django.http import HttpResponse, JsonResponse
from django.views import View

from usuarios.TokenInvalidoException import TokenInvalidoException

from .MovimientoNoEncontradoException import MovimientoNoEncontradoException


class ManejadorEliminarMovimiento(View):
    http_method_names = ["delete", "options"]
    servicio = None
    servicio_tokens = None

    def delete(self, peticion, movimiento_id):
        try:
            autorizacion = peticion.headers.get('Authorization', '')

            if not autorizacion.startswith('Bearer '):
                return JsonResponse(
                    {'error': 'La sesión es obligatoria.'},
                    status = 401,
                )

            token = autorizacion.removeprefix('Bearer ').strip()
            cuenta = self.servicio_tokens.obtener_cuenta(token)

            self.servicio.eliminar_movimiento(cuenta, movimiento_id)
            return JsonResponse({"eliminado": movimiento_id})
        except TokenInvalidoException as error:
            return JsonResponse({'error': str(error)}, status = 401)
        except MovimientoNoEncontradoException as error:
            return JsonResponse({"error": str(error)}, status=404)

    def options(self, peticion, movimiento_id):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta