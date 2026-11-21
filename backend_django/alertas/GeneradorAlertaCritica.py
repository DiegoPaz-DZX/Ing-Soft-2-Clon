from decimal import Decimal
from .GeneradorAlerta import GeneradorAlerta
from .Alerta import Alerta
from .TipoAlerta import TipoAlerta

class GeneradorAlertaCritica(GeneradorAlerta):
    """Generador concreto que crea alertas de tipo CRÍTICA (>90%)"""
    
    def crear_alerta(self, usuario_id, categoria, limite_mensual, monto_gastado):
        limite = Decimal(str(limite_mensual))
        gastado = Decimal(str(monto_gastado))
        
        if gastado <= 0 or limite <= 0:
            return None
        
        porcentaje = (gastado / limite) * 100
        
        # Solo crea alerta si supera el 90%
        if porcentaje > 90:
            return Alerta(usuario_id, categoria, TipoAlerta.CRITICA, porcentaje, limite, gastado)
        return None