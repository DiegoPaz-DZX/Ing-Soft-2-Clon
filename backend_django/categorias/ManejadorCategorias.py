from config.ConversorJson import ConversorJson
from config.ManejadorBase import ManejadorBase


class ManejadorCategorias(ManejadorBase):
    def obtener_datos(self):
        return ConversorJson.categorias_a_lista(self.servicio.obtener_todas())
