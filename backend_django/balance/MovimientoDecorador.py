from abc import ABC, abstractmethod

class MovimientoDecorador(ABC):
    """Clase abstracta que define el patrón Decorator para envolver Movimiento"""
    
    def __init__(self, movimiento):
        self._movimiento = movimiento
    
    @abstractmethod
    def validar(self):
        """Valida el movimiento. Las subclases implementan lógica específica"""
        pass
    
    def obtener_movimiento(self):
        """Devuelve el movimiento envuelto"""
        return self._movimiento