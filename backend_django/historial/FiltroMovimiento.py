from abc import ABC, abstractmethod


class FiltroMovimiento(ABC):
    @abstractmethod
    def cumple(self, movimiento):
        pass
