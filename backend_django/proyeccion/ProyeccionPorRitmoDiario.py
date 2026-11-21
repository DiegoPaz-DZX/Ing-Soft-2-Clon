import calendar
from decimal import Decimal
from .EstrategiaProyeccion import EstrategiaProyeccion

# calcula cuanto se gasta por dia y lo multiplica por los dias del mes
class ProyeccionPorRitmoDiario(EstrategiaProyeccion):
    def proyectar(self, gastos_recurrentes, hoy):
        total = Decimal("0")
        for gasto in gastos_recurrentes:
            total += gasto.monto

        dias_transcurridos = hoy.day
        dias_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]

        ritmo_diario = total / dias_transcurridos
        return ritmo_diario * dias_del_mes