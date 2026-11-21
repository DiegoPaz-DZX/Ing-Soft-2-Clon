from abc import ABC, abstractmethod


class ConversorMoneda(ABC):
    codigo = ""
    nombre = ""
    simbolo = ""

    @abstractmethod
    def soles_por_unidad(self):
        pass

    @abstractmethod
    def convertir(self, monto_en_soles):
        pass
