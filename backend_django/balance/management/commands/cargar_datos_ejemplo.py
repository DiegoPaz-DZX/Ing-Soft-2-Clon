from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from balance.Movimiento import Movimiento
from balance.RepositorioMovimientosDjango import RepositorioMovimientosDjango
from balance.TipoMovimiento import TipoMovimiento


class Command(BaseCommand):
    help = "Carga movimientos de ejemplo para probar el balance"

    def handle(self, *args, **opciones):
        Movimiento.objects.all().delete()
        repositorio = RepositorioMovimientosDjango()
        hoy = date.today()
        ejemplos = [
            (TipoMovimiento.INGRESO, "1500", hoy, "Pago practicas"),
            (TipoMovimiento.GASTO, "200", hoy, "Almuerzos"),
            (TipoMovimiento.GASTO, "350.50", hoy, "Transporte"),
            (TipoMovimiento.INGRESO, "3000", date(2026, 6, 1), "Salario del mes"),
            (TipoMovimiento.GASTO, "210", date(2026, 6, 5), "Luz y agua"),
            (TipoMovimiento.GASTO, "70", date(2026, 6, 12), "Gasolina de la semana"),
            (TipoMovimiento.GASTO, "170", date(2026, 7, 3), "Cursos cisco"),
        ]
        for tipo, monto, fecha, descripcion in ejemplos:
            repositorio.agregar(
                Movimiento(tipo=tipo, monto=Decimal(monto), fecha=fecha, descripcion=descripcion)
            )
        self.stdout.write(f"{len(ejemplos)} movimientos de ejemplo cargados")
