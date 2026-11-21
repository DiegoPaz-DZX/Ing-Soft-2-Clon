import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from sesion.MixinSesion import MixinSesion
from usuarios.TokenInvalidoException import TokenInvalidoException

from .CuentaNoEncontradaException import CuentaNoEncontradaException
from .DivisaNoSoportadaException import DivisaNoSoportadaException


class ManejadorPreferenciaMoneda(MixinSesion, View):
    http_method_names = ["get", "put", "options"]
    servicio = None

    def get(self, peticion):
        try:
            cuenta = self.cuenta_de_la_sesion(peticion)
            return self._responder(self.servicio.obtener_preferencia(cuenta.pk))
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except CuentaNoEncontradaException as error:
            return JsonResponse({"error": str(error)}, status=404)

    def put(self, peticion):
        try:
            cuenta = self.cuenta_de_la_sesion(peticion)
            datos = json.loads(peticion.body or b"{}")
            return self._responder(self.servicio.cambiar_divisa(cuenta.pk, datos.get("divisa")))
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "El contenido enviado no es válido."}, status=400)
        except CuentaNoEncontradaException as error:
            return JsonResponse({"error": str(error)}, status=404)
        except DivisaNoSoportadaException as error:
            return JsonResponse({"error": str(error)}, status=400)

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "GET, PUT, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta

    def _responder(self, preferencia):
        tipo_cambio = preferencia.tipo_cambio
        return JsonResponse(
            {
                "divisa": self._a_dict(preferencia.divisa),
                "opciones": [self._a_dict(opcion) for opcion in preferencia.opciones],
                "tipoCambio": {
                    "fecha": tipo_cambio.fecha.isoformat(),
                    "solesPorDolar": float(tipo_cambio.soles_por_dolar),
                    "fuente": tipo_cambio.fuente,
                },
            },
            json_dumps_params={"ensure_ascii": False},
        )

    def _a_dict(self, conversor):
        return {
            "codigo": conversor.codigo,
            "nombre": conversor.nombre,
            "simbolo": conversor.simbolo,
            "solesPorUnidad": float(conversor.soles_por_unidad()),
        }
