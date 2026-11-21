from decimal import Decimal

from .DesviacionMensual import DesviacionMensual

CERO = Decimal("0")
CIEN = Decimal("100")
DECIMA = Decimal("0.1")
UMBRAL_AHORRO_MINIMO = Decimal("20")
UMBRAL_DESVIACION_ATENCION = Decimal("10")
UMBRAL_DESVIACION_CRITICA = Decimal("25")


class MonitorSaludFacade:
    """Facade (patrón estructural): una sola operación evaluar() que oculta
    la obtención del reporte, el cálculo de desviaciones y la clasificación de estado."""

    def __init__(self, servicio_reportes):
        self._servicio_reportes = servicio_reportes

    def evaluar(self, cuenta=None):
        reporte = self._servicio_reportes.generar_reporte(
            con_graficos=True,
            con_analisis=False,
            cuenta=cuenta,
        )
        meses = self._calcular_desviaciones(reporte.evolucion_mensual)
        return {
            "meses": [mes.a_dict() for mes in meses],
            "estado_actual": meses[-1].a_dict() if meses else None,
            "resumen": {
                "saludables": sum(1 for m in meses if m.estado == "saludable"),
                "atencion": sum(1 for m in meses if m.estado == "atencion"),
                "criticos": sum(1 for m in meses if m.estado == "critico"),
            },
        }

    def _calcular_desviaciones(self, evolucion):
        resultado = []
        gastos_previos = []
        for periodo in evolucion:
            promedio_previo = (
                sum(gastos_previos) / len(gastos_previos) if gastos_previos else None
            )
            balance = periodo.ingresos - periodo.gastos
            tasa = self._tasa_ahorro(periodo.ingresos, balance)
            desviacion = self._desviacion(periodo.gastos, promedio_previo)
            resultado.append(
                DesviacionMensual(
                    periodo.periodo,
                    periodo.etiqueta,
                    periodo.ingresos,
                    periodo.gastos,
                    balance,
                    tasa,
                    desviacion,
                    self._clasificar(balance, tasa, desviacion),
                )
            )
            gastos_previos.append(periodo.gastos)
        return resultado

    def _desviacion(self, gasto, promedio_previo):
        if promedio_previo is None or promedio_previo == CERO:
            return None
        return ((gasto - promedio_previo) * CIEN / promedio_previo).quantize(DECIMA)

    def _tasa_ahorro(self, ingresos, balance):
        if ingresos <= CERO:
            return None
        return (balance * CIEN / ingresos).quantize(DECIMA)

    def _clasificar(self, balance, tasa, desviacion):
        # Crítico: gastas más de lo que ingresas
        if balance < CERO:
            return "critico"
        # Crítico: el gasto se disparó Y además el ahorro es insuficiente
        ahorro_insuficiente = tasa is not None and tasa < UMBRAL_AHORRO_MINIMO
        if desviacion is not None and desviacion > UMBRAL_DESVIACION_CRITICA and ahorro_insuficiente:
            return "critico"
        # Atención: ahorro bajo, o gasto elevado frente al promedio
        if ahorro_insuficiente or (
            desviacion is not None and desviacion > UMBRAL_DESVIACION_ATENCION
        ):
            return "atencion"
        return "saludable"