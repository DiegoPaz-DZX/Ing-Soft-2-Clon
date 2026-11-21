import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from .CuentaNoEncontradaException import CuentaNoEncontradaException
from .PermisoDenegadoException import PermisoDenegadoException
from .RolInvalidoException import RolInvalidoException
from .TokenInvalidoException import TokenInvalidoException


class ManejadorAdministracionUsuarios(View):
    http_method_names = ["get", "put", "options"]
    servicio = None

    def get(self, peticion):
        try:
            usuarios = self.servicio.listar_usuarios(self._obtener_token(peticion))
            return JsonResponse({"usuarios": [self._a_dict(usuario) for usuario in usuarios]})
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except PermisoDenegadoException as error:
            return JsonResponse({"error": str(error)}, status=403)

    def put(self, peticion, cuenta_id):
        try:
            datos = json.loads(peticion.body or b"{}")
            cuenta = self.servicio.cambiar_rol(
                self._obtener_token(peticion), cuenta_id, datos.get("rol")
            )
            return JsonResponse(self._a_dict(cuenta))
        except json.JSONDecodeError:
            return JsonResponse({"error": "El contenido enviado no es válido."}, status=400)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except PermisoDenegadoException as error:
            return JsonResponse({"error": str(error)}, status=403)
        except RolInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=400)
        except CuentaNoEncontradaException as error:
            return JsonResponse({"error": str(error)}, status=404)

    def options(self, peticion, cuenta_id=None):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "GET, PUT, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta

    def _obtener_token(self, peticion):
        cabecera = peticion.headers.get("Authorization", "")
        return cabecera[7:] if cabecera.startswith("Bearer ") else ""

    def _a_dict(self, cuenta):
        return {"id": cuenta.pk, "correo": cuenta.correo, "rol": cuenta.rol}
