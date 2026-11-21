from abc import ABC, abstractmethod

class RepositorioLimites(ABC):
    @abstractmethod
    def guardar_limite(self, usuario_id, categoria, limite_mensual):
        pass
    
    @abstractmethod
    def obtener_limite(self, usuario_id, categoria):
        pass
    
    @abstractmethod
    def obtener_limites_usuario(self, usuario_id):
        pass