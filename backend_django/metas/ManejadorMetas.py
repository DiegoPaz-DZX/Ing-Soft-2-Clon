import json

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views import View

from usuarios.TokenInvalidoException import TokenInvalidoException


def serializar(meta):
    return {
        "id": meta.pk,
        "nombre": meta.nombre,
        "objetivoPEN": str(meta.objetivo_pen),
        "totalAbonadoPEN": str(meta.total_abonado_pen),
    }


class ManejadorMetas(View):
    http_method_names = ["get", "post", "put", "delete", "options"]
    facade = None

    def get(self, peticion):
        try:
            return JsonResponse({"metas": [serializar(meta) for meta in self.facade.listar(peticion)]})
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

    def post(self, peticion, meta_id=None):
        try:
            datos = json.loads(peticion.body or b"{}")
            meta = (
                self.facade.abonar(peticion, meta_id, datos)
                if meta_id
                else self.facade.crear(peticion, datos)
            )
            return JsonResponse(serializar(meta), status=201)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        except IntegrityError:
            return JsonResponse(
                {"error": "Ya tienes una meta con ese nombre. Elige un título diferente."},
                status=400,
            )

    def delete(self, peticion, meta_id=None):
        try:
            self.facade.eliminar(peticion, meta_id)
            return JsonResponse({"mensaje": "Meta eliminada."})
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=404)

    def put(self, peticion, meta_id=None):
        try:
            datos = json.loads(peticion.body or b"{}")
            meta = self.facade.renombrar(peticion, meta_id, datos)
            return JsonResponse(serializar(meta))
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        except IntegrityError:
            return JsonResponse(
                {"error": "Ya tienes una meta con ese nombre. Elige un título diferente."},
                status=400,
            )

    def options(self, peticion, *args, **kwargs):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta
