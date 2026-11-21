from abc import ABC, abstractmethod


class ReglaAnalisis(ABC):
    @abstractmethod
    def evaluar(self, reporte, categorias, meses):
        pass
