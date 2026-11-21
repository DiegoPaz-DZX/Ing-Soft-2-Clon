from abc import ABC, abstractmethod

class EstrategiaProyeccion(ABC):
    # devuelve cuanto se gastaria en todo el mes con los gastos recurrentes recibidos
    @abstractmethod
    def proyectar(self, gastos_recurrentes, hoy):
        pass