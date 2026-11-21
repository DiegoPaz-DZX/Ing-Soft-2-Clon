from decimal import Decimal

from .models import MetaAhorro


class RepositorioMetas:
    def listar(self, cuenta):
        return list(MetaAhorro.objects.filter(usuario=cuenta))

    def crear(self, cuenta, nombre, objetivo_pen):
        return MetaAhorro.objects.create(
            usuario=cuenta,
            nombre=nombre,
            objetivo_pen=Decimal(objetivo_pen),
        )

    def existe_nombre(self, cuenta, nombre):
        return MetaAhorro.objects.filter(usuario=cuenta, nombre__iexact=nombre).exists()

    def abonar(self, cuenta, meta_id, monto_pen):
        meta = MetaAhorro.objects.filter(pk=meta_id, usuario=cuenta).first()
        if meta is None:
            return None
        meta.total_abonado_pen += Decimal(monto_pen)
        meta.save(update_fields=["total_abonado_pen", "actualizada_en"])
        return meta

    def eliminar(self, cuenta, meta_id):
        eliminado, _ = MetaAhorro.objects.filter(pk=meta_id, usuario=cuenta).delete()
        return eliminado > 0

    def obtener(self, cuenta, meta_id):
        return MetaAhorro.objects.filter(pk=meta_id, usuario=cuenta).first()

    def actualizar_nombre(self, meta, nombre):
        meta.nombre = nombre
        meta.save(update_fields=["nombre", "actualizada_en"])
        return meta
