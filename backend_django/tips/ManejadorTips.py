from config.ConversorJson import ConversorJson
from config.ManejadorBase import ManejadorBase


class ManejadorTips(ManejadorBase):
    def obtener_datos(self):
        return ConversorJson.tips_a_lista(self.servicio.obtener_todos())
