from abc import ABC, abstractmethod
from .Alerta import Alerta

class GeneradorAlerta(ABC):
    """Clase abstracta que define la interfaz de creación de alertas (Factory Method)"""
    
    @abstractmethod
    def crear_alerta(self, usuario_id, categoria, limite_mensual, monto_gastado):
        """Crea una alerta si es necesaria según los parámetros"""
        pass