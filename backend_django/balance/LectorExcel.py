from datetime import date, datetime
from io import BytesIO
import os
from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
import xlrd

from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException
from .LectorMovimientos import LectorMovimientos


class LectorExcel(LectorMovimientos):
    def leer_filas(self, archivo):
        extension = os.path.splitext(archivo.name)[1].lower()
        try:
            if extension == ".xls":
                libro = xlrd.open_workbook(file_contents=archivo.read())
                hoja = libro.sheet_by_index(0)
                filas = []
                for indice in range(hoja.nrows):
                    valores = []
                    for celda in hoja.row(indice):
                        if celda.ctype == xlrd.XL_CELL_DATE:
                            valor = xlrd.xldate_as_datetime(celda.value, libro.datemode).date()
                        else:
                            valor = celda.value
                        valores.append(valor)
                    filas.append(valores)
                return filas

            libro = load_workbook(BytesIO(archivo.read()), read_only=True, data_only=True)
            try:
                hoja = libro.active
                return [list(fila) for fila in hoja.iter_rows(values_only=True)]
            finally:
                libro.close()
        except (BadZipFile, InvalidFileException, ValueError, KeyError, OSError, xlrd.XLRDError) as error:
            raise ArchivoImportacionInvalidoException(
                "No se pudo leer el archivo de Excel."
            ) from error

    @staticmethod
    def preparar_valor(valor):
        if isinstance(valor, datetime):
            return valor.date().isoformat()
        if isinstance(valor, date):
            return valor.isoformat()
        return valor

    def leer(self, archivo):
        filas = super().leer(archivo)
        return [
            (numero, {columna: self.preparar_valor(valor) for columna, valor in datos.items()})
            for numero, datos in filas
        ]
