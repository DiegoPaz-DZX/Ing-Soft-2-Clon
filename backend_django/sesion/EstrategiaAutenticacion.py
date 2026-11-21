from abc import ABC, abstractmethod


class EstrategiaAutenticacion(ABC):
    @abstractmethod
    def autenticar(self, correo, clave):
        pass
