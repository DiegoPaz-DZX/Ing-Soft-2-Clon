from abc import ABC, abstractmethod


class RepositorioMovimientos(ABC):
    @abstractmethod
    def agregar(self, movimiento):
        pass

    @abstractmethod
    def sumar_por_tipo(self, cuenta, tipo, moneda="PEN"):
        pass

    @abstractmethod
    def sumar_gasto_categoria_mes(self, cuenta, categoria, anio, mes):
        pass

    @abstractmethod
    def eliminar(self, cuenta, movimiento_id):
        pass

    @abstractmethod
    def obtener_por_id(self, cuenta, movimiento_id):
        pass

    @abstractmethod
    def actualizar(self, movimiento):
        pass

    def agregar_varios(self, movimientos):
        for movimiento in movimientos:
            self.agregar(movimiento)
