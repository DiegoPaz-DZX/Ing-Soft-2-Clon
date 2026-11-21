from historial.FiltroPorRangoFechas import FiltroPorRangoFechas

from .ConstructorReporte import ConstructorReporte


class ServicioReportes:
    def __init__(self, historial, servicio_categorias, servicio_tipo_cambio, reglas_analisis):
        self._historial = historial
        self._categorias = servicio_categorias
        self._tipo_cambio = servicio_tipo_cambio
        self._reglas = reglas_analisis

    def generar_reporte(
        self,
        desde=None,
        hasta=None,
        con_graficos=True,
        con_analisis=True,
        cuenta=None,
    ):
        filtro = None
        if desde is not None or hasta is not None:
            filtro = FiltroPorRangoFechas(desde, hasta)

        movimientos = self._historial.obtener_movimientos(cuenta, filtro)
        nombres = {c.codigo: c.nombre for c in self._categorias.obtener_todas()}
        constructor = ConstructorReporte(
            movimientos, nombres, desde, hasta, self._obtener_soles_por_dolar(movimientos)
        )
        if con_graficos:
            constructor.con_gastos_por_categoria().con_evolucion_mensual()
        if con_analisis:
            constructor.con_analisis(self._reglas)
        return constructor.con_movimientos().construir()

    def _obtener_soles_por_dolar(self, movimientos):
        hay_dolares = any(getattr(m, "moneda", "PEN") == "USD" for m in movimientos)
        if not hay_dolares:
            return None
        return self._tipo_cambio.obtener_del_dia().soles_por_dolar
