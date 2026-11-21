from .RepositorioTips import RepositorioTips
from .Tip import Tip


class RepositorioTipsMemoria(RepositorioTips):
    def __init__(self):
        self._tips = (
            Tip(
                1,
                "Regla del 50/30/20 adaptada a ingresos variables",
                "Si tu ingreso de prácticas varía cada mes, no repartas porcentajes fijos: "
                "primero cubre lo esencial (50%), luego separa tu meta de ahorro (20%) "
                "antes de gastar en lo demás (30%).",
            ),
            Tip(
                2,
                "Registra el mismo día, no al final de mes",
                "Un gasto que no registras el mismo día es un gasto que vas a subestimar. "
                "Anota apenas pagues, no cuando ya se te olvidó cuánto fue.",
            ),
            Tip(
                3,
                "Antes de una tarjeta de crédito, ten un colchón",
                "No uses crédito para cubrir gastos fijos que ya sabes que van a llegar. "
                "El crédito es para imprevistos, no para tu presupuesto mensual.",
            ),
            Tip(
                4,
                "Divide tus gastos por categoría, no por monto total",
                "Ver 'gasté S/800 este mes' no dice nada. Ver 'S/300 en comida, S/200 en "
                "transporte' sí te dice dónde ajustar.",
            ),
            Tip(
                5,
                "Ahorra el ingreso extra, no lo gastes por default",
                "Si te llega un bono o un pago extra de práctica, transfiérelo directo a tu "
                "meta antes de que se mezcle con tu gasto normal.",
            ),
            Tip(
                6,
                "Revisa tu Monitor de Salud, no solo tu saldo",
                "Tener plata en la cuenta no significa estar bien financieramente. Revisa si "
                "tu ritmo de gasto es sostenible, no solo cuánto te queda hoy.",
            ),
            Tip(
                7,
                'Un gasto en dólares no es "gratis" solo porque no lo ves en soles',
                "Si trabajas con divisas mixtas, revisa siempre el equivalente en tu moneda "
                "base antes de gastar: el tipo de cambio cambia más rápido de lo que crees.",
            ),
            Tip(
                8,
                "Una meta sin fecha es solo un deseo",
                "Ponle plazo a tu ahorro. 'Ahorrar para mi laptop' no es una meta; "
                "'ahorrar S/2000 en 4 meses' sí lo es.",
            ),
        )

    def listar_todos(self):
        return list(self._tips)
