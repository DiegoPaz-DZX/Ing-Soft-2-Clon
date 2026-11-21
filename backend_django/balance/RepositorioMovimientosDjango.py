from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from .Movimiento import Movimiento
from .RepositorioMovimientos import RepositorioMovimientos
from metas.models import MetaAhorro


class RepositorioMovimientosDjango(RepositorioMovimientos):
    tipo_cambio_usd_pen = Decimal("3.75")

    def agregar(self, movimiento):
        movimiento.save()

    def agregar_varios(self, movimientos):
        with transaction.atomic():
            for movimiento in movimientos:
                movimiento.save()

    def sumar_por_tipo(self, cuenta, tipo, moneda="PEN"):
        total = Movimiento.objects.filter(usuario = cuenta, tipo=tipo, moneda=moneda).aggregate(
            total=Sum("monto")
        )["total"]
        return total or Decimal("0")

    def sumar_gasto_categoria_mes(self, cuenta, categoria, anio, mes):
        movimientos = Movimiento.objects.filter(
            usuario = cuenta, tipo="GASTO", categoria=categoria, fecha__year=anio, fecha__month=mes
        )
        total = Decimal("0")
        for movimiento in movimientos:
            if movimiento.moneda == "USD":
                total += movimiento.monto * self.tipo_cambio_usd_pen
            else:
                total += movimiento.monto
        return total

    def listar_todos(self, cuenta):
        return list(Movimiento.objects.filter(usuario = cuenta).order_by('-fecha', '-id'))

    def eliminar(self, cuenta, movimiento_id):
        movimiento = Movimiento.objects.filter(pk=movimiento_id, usuario = cuenta).first()
        if movimiento is None:
            return False
        archivo = movimiento.comprobante
        movimiento.delete()
        if archivo:
            archivo.delete(save=False)
        return True

    def obtener_por_id(self, cuenta, movimiento_id):
        return Movimiento.objects.filter(pk=movimiento_id, usuario = cuenta).first()

    # NUEVO (HU18)
    def actualizar(self, movimiento):
        movimiento.save()
        return movimiento

    def obtener_meta(self, cuenta, meta_id):
        return MetaAhorro.objects.filter(pk=meta_id, usuario=cuenta).first()
