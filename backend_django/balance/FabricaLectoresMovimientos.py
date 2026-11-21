import os

from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException
from .LectorCsv import LectorCsv
from .LectorExcel import LectorExcel


class FabricaLectoresMovimientos:
    @staticmethod
    def crear(nombre_archivo):
        extension = os.path.splitext(nombre_archivo or "")[1].lower()
        if extension == ".csv":
            return LectorCsv()
        if extension in {".xls", ".xlsx"}:
            return LectorExcel()
        raise ArchivoImportacionInvalidoException("Solo se permiten archivos CSV, XLS o XLSX.")
