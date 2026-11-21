from abc import ABC, abstractmethod


class ProveedorTipoCambio(ABC):
    nombre = ""

    @abstractmethod
    def obtener_soles_por_dolar(self):
        pass
