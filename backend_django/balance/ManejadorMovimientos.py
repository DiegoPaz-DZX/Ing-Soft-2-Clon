import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from usuarios.TokenInvalidoException import TokenInvalidoException

from .DatosMovimientoInvalidosException import DatosMovimientoInvalidosException
from .MontoInvalidoException import MontoInvalidoException


class ManejadorMovimientos(View):
    http_method_names = ["post", "options"]
    servicio = None
    servicio_tokens = None

    def post(self, peticion):
        try:
            token = peticion.headers.get('Authorization', '')
            if not token.startswith('Bearer '):
                return JsonResponse({'error' : 'La sesion es obligatoria'}, status = 401)

            token = token.replace('Bearer ', '').strip()
            cuenta = self.servicio_tokens.obtener_cuenta(token)

            if peticion.content_type == "multipart/form-data":
                datos = peticion.POST
                comprobante = peticion.FILES.get("comprobante")
            else:
                datos = json.loads(peticion.body or b"{}")
                comprobante = None
                if not isinstance(datos, dict):
                    raise DatosMovimientoInvalidosException("El contenido enviado no es válido.")

            movimiento = self.servicio.registrar_movimiento(
                cuenta,
                datos.get("tipo"),
                datos.get("monto"),
                datos.get("fecha"),
                datos.get("descripcion", ""),
                comprobante,
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
                    "categoria": movimiento.categoria,
                    "moneda": movimiento.moneda,
                    "meta_id": movimiento.meta_id,
                    "meta_nombre": movimiento.meta.nombre if movimiento.meta_id else None,
                    "comprobante_url": movimiento.comprobante.url if movimiento.comprobante else None,
                },
                status=201,
            )
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "El contenido enviado no es válido."}, status=400)
        except (MontoInvalidoException, DatosMovimientoInvalidosException) as error:
            return JsonResponse({"error": str(error)}, status=400)

    def options(self, peticion):
        return HttpResponse(status=204)

    def dispatch(self, peticion, *args, **kwargs):
        respuesta = super().dispatch(peticion, *args, **kwargs)
        respuesta["Access-Control-Allow-Origin"] = "*"
        respuesta["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        respuesta["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return respuesta