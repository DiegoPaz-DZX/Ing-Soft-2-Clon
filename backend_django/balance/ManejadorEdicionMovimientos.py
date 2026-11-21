import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from usuarios.TokenInvalidoException import TokenInvalidoException

from .DatosMovimientoInvalidosException import DatosMovimientoInvalidosException
from .MontoInvalidoException import MontoInvalidoException
from .MovimientoNoEncontradoException import MovimientoNoEncontradoException


class ManejadorEdicionMovimientos(View):
    http_method_names = ["put", "options"]
    servicio = None
    servicio_tokens = None

    def put(self, peticion, movimiento_id):
        try:
            autorizacion = peticion.headers.get("Authorization", "")

            if not autorizacion.startswith("Bearer "):
                return JsonResponse(
                    {"error": "La sesión es obligatoria."},
                    status=401,
                )

            token = autorizacion.removeprefix("Bearer ").strip()
            cuenta = self.servicio_tokens.obtener_cuenta(token)

            datos = json.loads(peticion.body or b"{}")
            if not isinstance(datos, dict):
                raise DatosMovimientoInvalidosException("El contenido enviado no es válido.")

            movimiento = self.servicio.editar_movimiento(
                cuenta,
                movimiento_id,
                datos.get("tipo"),
                datos.get("monto"),
                datos.get("fecha"),
                datos.get("descripcion", ""),
                datos.get("categoria", ""),
                datos.get("moneda", "PEN"),
                datos.get("meta_id"),
            )
            return JsonResponse(
                {
                    "id": movimiento.pk,
                    "tipo": movimiento.tipo,
                    "monto": str(movimiento.monto),
                    "fecha": movimiento.fecha.isoformat(),
                    "descripcion": movimiento.descripcion,
                    "categoria": movimiento.categoria,
                    "moneda": movimiento.moneda,
                    "meta_id": movimiento.meta_id,
                    "meta_nombre": movimiento.meta.nombre if movimiento.meta_id else None,
                    "comprobante_url": movimiento.comprobante.url if movimiento.comprobante else None,
                },
                status=200,
            )
        except TokenInvalidoException as error:
            return JsonResponse({'error': str(error)}, status = 401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "El contenido enviado no es válido."}, status=400)
        except MovimientoNoEncontradoException as error:
            return JsonResponse({"error": str(error)}, status=404)
        except (MontoInvalidoException, DatosMovimientoInvalidosException, ValueError) as error:
            return JsonResponse({"error": str(error)}, status=400)

    def options(self, peticion, movimiento_id=None):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta
