import json

from .ConversorReporte import ConversorReporte
from .ExportadorReporte import ExportadorReporte


class ExportadorJson(ExportadorReporte):
    extension = "json"
    tipo_contenido = "application/json; charset=utf-8"

    def exportar(self, reporte):
        return json.dumps(ConversorReporte.a_dict(reporte), ensure_ascii=False, indent=2)
