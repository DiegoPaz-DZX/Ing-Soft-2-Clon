import csv
from io import StringIO

from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException
from .LectorMovimientos import LectorMovimientos


class LectorCsv(LectorMovimientos):
    def leer_filas(self, archivo):
        try:
            contenido = archivo.read().decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ArchivoImportacionInvalidoException(
                "El CSV debe estar guardado con codificación UTF-8."
            ) from error

        try:
            dialecto = csv.Sniffer().sniff(contenido[:2048], delimiters=",;")
        except csv.Error:
            dialecto = csv.excel
        return csv.reader(StringIO(contenido), dialect=dialecto)
