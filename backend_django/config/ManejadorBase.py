from abc import ABC, abstractmethod

from django.http import HttpResponse, JsonResponse
from django.views import View


class ManejadorBase(View, ABC):
    http_method_names = ["get", "options"]
    servicio = None

    @abstractmethod
    def obtener_datos(self):
        pass

    def get(self, peticion):
        return JsonResponse(
            self.obtener_datos(), safe=False, json_dumps_params={"ensure_ascii": False}
        )

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta
