from .ExportadorCsv import ExportadorCsv
from .ExportadorJson import ExportadorJson
from .ExportadorPdfGraficos import ExportadorPdfGraficos
from .FormatoNoSoportadoException import FormatoNoSoportadoException


class FabricaExportadores:
    @staticmethod
    def crear(formato):
        exportadores = {"csv": ExportadorCsv, "json": ExportadorJson, "pdf": ExportadorPdfGraficos}
        clase = exportadores.get(str(formato or "").lower())
        if clase is None:
            raise FormatoNoSoportadoException("El formato debe ser csv, json o pdf.")
        return clase()
