from abc import ABC, abstractmethod


class RepositorioPreferencias(ABC):
    @abstractmethod
    def existe_cuenta(self, cuenta_id):
        pass

    @abstractmethod
    def obtener_divisa(self, cuenta_id):
        pass

    @abstractmethod
    def guardar_divisa(self, cuenta_id, divisa):
        pass
