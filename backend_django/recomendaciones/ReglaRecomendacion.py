from abc import ABC, abstractmethod


class ReglaRecomendacion(ABC):
    @abstractmethod
    def evaluar(self, resumen):
        """Devuelve una lista de Recomendacion (vacía si la regla no aplica)."""