from datetime import date

from django.http import JsonResponse

from config.ConversorJson import ConversorJson
from config.ManejadorBase import ManejadorBase
from sesion.MixinSesion import MixinSesion
from usuarios.TokenInvalidoException import TokenInvalidoException

from .FiltroPorRangoFechas import FiltroPorRangoFechas
from .RangoFechasInvalidoException import RangoFechasInvalidoException


class ManejadorHistorial(MixinSesion, ManejadorBase):
    def get(self, peticion):
        try:
            return super().get(peticion)
        except TokenInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=401)
        except RangoFechasInvalidoException as error:
            return JsonResponse({"error": str(error)}, status=400)
        except ValueError:
            return JsonResponse({"error": "Formato de fecha inválido. Use AAAA-MM-DD."}, status=400)

    def obtener_datos(self):
        cuenta = self.cuenta_de_la_sesion(self.request)
        movimientos = self.servicio.obtener_movimientos(cuenta, self._crear_filtro())
        return ConversorJson.movimientos_a_lista(movimientos)

    def _crear_filtro(self):
        parametros = self.request.GET
        if "desde" not in parametros and "hasta" not in parametros:
            return None
        return FiltroPorRangoFechas(
            self._convertir_fecha(parametros.get("desde")),
            self._convertir_fecha(parametros.get("hasta")),
        )

    def _convertir_fecha(self, texto):
        if not texto:
            return None
        return date.fromisoformat(texto)
