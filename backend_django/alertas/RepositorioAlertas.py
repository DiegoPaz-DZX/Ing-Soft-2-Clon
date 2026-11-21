from abc import ABC, abstractmethod

class RepositorioAlertas(ABC):
    @abstractmethod
    def guardar_alerta(self, alerta):
        pass
    
    @abstractmethod
    def obtener_alertas_usuario(self, usuario_id):
        pass