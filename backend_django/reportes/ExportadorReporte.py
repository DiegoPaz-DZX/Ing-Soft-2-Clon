from abc import ABC, abstractmethod


class ExportadorReporte(ABC):
    extension = ""
    tipo_contenido = ""

    @abstractmethod
    def exportar(self, reporte):
        pass
