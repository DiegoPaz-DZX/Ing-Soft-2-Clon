from .ConversorDolares import ConversorDolares
from .ConversorSoles import ConversorSoles
from .Divisa import Divisa
from .DivisaNoSoportadaException import DivisaNoSoportadaException


class FabricaConversores:
    @staticmethod
    def crear(codigo, soles_por_dolar):
        if codigo == Divisa.PEN:
            return ConversorSoles()
        if codigo == Divisa.USD:
            return ConversorDolares(soles_por_dolar)
        raise DivisaNoSoportadaException("La divisa debe ser Soles (PEN) o Dólares (USD).")

    @staticmethod
    def crear_todos(soles_por_dolar):
        return [FabricaConversores.crear(codigo, soles_por_dolar) for codigo in Divisa.values]
