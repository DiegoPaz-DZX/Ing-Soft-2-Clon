from decimal import Decimal
from balance.TipoMovimiento import TipoMovimiento
from .ProyeccionGasto import ProyeccionGasto

# proyecta el gasto del mes para anticipar un sobregasto
class ServicioProyeccion:
    def __init__(self, repositorio, estrategia, detector):
        self._repositorio = repositorio
        self._estrategia = estrategia
        self._detector = detector

    def proyectar(self, hoy, cuenta):
        todos = self._repositorio.listar_movimientos(cuenta)
        historial_gastos = []
        for m in todos:
            if m.tipo == TipoMovimiento.GASTO:
                historial_gastos.append(m)

        gastos_recurrentes = []
        gasto_atipico = Decimal("0")
        ingresos_mes = Decimal("0")

        for m in todos:
            if m.fecha.year != hoy.year or m.fecha.month != hoy.month:
                continue
            if m.tipo == TipoMovimiento.INGRESO:
                ingresos_mes += m.monto
            elif self._detector.es_atipico(m, historial_gastos):
                # gasto unico: se suma tal cual, no se proyecta
                gasto_atipico += m.monto
            else:
                gastos_recurrentes.append(m)

        gasto_recurrente = Decimal("0")
        for m in gastos_recurrentes:
            gasto_recurrente += m.monto

        gasto_actual = gasto_recurrente + gasto_atipico
        gasto_proyectado = gasto_atipico + self._estrategia.proyectar(gastos_recurrentes, hoy)

        sugerencia = self._crear_sugerencia(gasto_actual, gasto_atipico, gasto_proyectado, ingresos_mes)
        return ProyeccionGasto(gasto_actual, gasto_atipico, gasto_proyectado, ingresos_mes, sugerencia)

    def _crear_sugerencia(self, gasto_actual, gasto_atipico, gasto_proyectado, ingresos_mes):
        if gasto_actual == 0:
            return "Aún no hay gastos este mes para proyectar."

        if gasto_proyectado > ingresos_mes:
            exceso = gasto_proyectado - ingresos_mes
            mensaje = (
                f"A este ritmo cerrarás el mes con S/{gasto_proyectado:.2f} en gastos, "
                f"S/{exceso:.2f} más que tus ingresos. "
                "Reduce tu gasto diario para evitar un desfalco."
            )
        else:
            mensaje = (
                f"Tu ritmo de gasto es sostenible: proyectas S/{gasto_proyectado:.2f} "
                f"frente a ingresos de S/{ingresos_mes:.2f}."
            )

        if gasto_atipico > 0:
            mensaje += f" No se proyectaron S/{gasto_atipico:.2f} por ser un gasto único (no recurrente)."
        return mensaje