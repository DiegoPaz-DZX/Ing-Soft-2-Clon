from decimal import Decimal
from .GeneradorAlerta import GeneradorAlerta
from .Alerta import Alerta
from .TipoAlerta import TipoAlerta

class GeneradorAlertaAdvertencia(GeneradorAlerta):
    """Generador concreto que crea alertas de tipo ADVERTENCIA (70-90%)"""
    
    def crear_alerta(self, usuario_id, categoria, limite_mensual, monto_gastado):
        limite = Decimal(str(limite_mensual))
        gastado = Decimal(str(monto_gastado))
        
        if gastado <= 0 or limite <= 0:
            return None
        
        porcentaje = (gastado / limite) * 100
        
        # Solo crea alerta si está entre 70% y 90%
        if 70 <= porcentaje < 90:
            return Alerta(usuario_id, categoria, TipoAlerta.ADVERTENCIA, porcentaje, limite, gastado)
        return None