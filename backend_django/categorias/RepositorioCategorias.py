from abc import ABC, abstractmethod


class RepositorioCategorias(ABC):
    @abstractmethod
    def listar_todas(self):
        pass
