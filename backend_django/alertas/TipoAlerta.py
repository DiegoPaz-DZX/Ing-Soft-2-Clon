from enum import Enum

class TipoAlerta(Enum):
    ADVERTENCIA = "advertencia"
    CRITICA = "critica"
    
    def describe(self):
        if self == TipoAlerta.ADVERTENCIA:
            return "Advertencia: Has gastado entre 70-90% de tu límite"
        return "¡Crítico! Has superado el 90% de tu límite"