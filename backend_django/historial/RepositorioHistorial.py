from abc import ABC, abstractmethod


class RepositorioHistorial(ABC):
    @abstractmethod
    def listar_movimientos(self, cuenta):
        pass
