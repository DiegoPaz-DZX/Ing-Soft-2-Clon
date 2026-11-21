from decimal import Decimal
from .RepositorioLimites import RepositorioLimites
from .models import LimiteGasto

class RepositorioLimitesDjango(RepositorioLimites):
    def guardar_limite(self, usuario_id, categoria, limite_mensual):
        limite, _ = LimiteGasto.objects.update_or_create(
            usuario_id=usuario_id, categoria=categoria,
            defaults={'limite_mensual': Decimal(str(limite_mensual))}
        )
        return limite
    
    def obtener_limite(self, usuario_id, categoria):
        try:
            limite = LimiteGasto.objects.get(usuario_id=usuario_id, categoria=categoria, activo=True)
            return Decimal(str(limite.limite_mensual))
        except LimiteGasto.DoesNotExist:
            return None
    
    def obtener_limites_usuario(self, usuario_id):
        limites = LimiteGasto.objects.filter(usuario_id=usuario_id, activo=True)
        return {limite.categoria: Decimal(str(limite.limite_mensual)) for limite in limites}