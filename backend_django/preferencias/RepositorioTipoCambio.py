from abc import ABC, abstractmethod


class RepositorioTipoCambio(ABC):
    @abstractmethod
    def obtener_de_fecha(self, fecha):
        pass

    @abstractmethod
    def obtener_ultimo(self):
        pass

    @abstractmethod
    def guardar(self, fecha, soles_por_dolar, fuente):
        pass
