from abc import ABC, abstractmethod


class RepositorioTips(ABC):
    @abstractmethod
    def listar_todos(self):
        pass
