from abc import ABC, abstractmethod


class RepositorioCuentas(ABC):
    @abstractmethod
    def guardar(self, cuenta):
        pass

    @abstractmethod
    def buscar_por_correo(self, correo):
        pass

    @abstractmethod
    def buscar_por_id(self, cuenta_id):
        pass

    @abstractmethod
    def listar(self):
        pass
