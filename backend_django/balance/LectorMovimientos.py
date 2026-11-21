from abc import ABC, abstractmethod
import unicodedata

from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException


class LectorMovimientos(ABC):
    COLUMNAS_REQUERIDAS = {"tipo", "monto", "fecha"}

    @abstractmethod
    def leer_filas(self, archivo):
        pass

    def leer(self, archivo):
        filas = list(self.leer_filas(archivo))
        if not filas:
            raise ArchivoImportacionInvalidoException("El archivo está vacío.")

        encabezados = [self._normalizar_encabezado(valor) for valor in filas[0]]
        faltantes = self.COLUMNAS_REQUERIDAS.difference(encabezados)
        if faltantes:
            columnas = ", ".join(sorted(faltantes))
            raise ArchivoImportacionInvalidoException(
                f"Faltan las columnas obligatorias: {columnas}."
            )

        movimientos = []
        for numero, valores in enumerate(filas[1:], start=2):
            if not any(valor not in (None, "") for valor in valores):
                continue
            fila = {
                encabezado: valores[indice] if indice < len(valores) else ""
                for indice, encabezado in enumerate(encabezados)
                if encabezado
            }
            movimientos.append((numero, fila))
        return movimientos

    def _normalizar_encabezado(self, valor):
        texto = str(valor or "").strip().lower().replace(" ", "_")
        return "".join(
            letra
            for letra in unicodedata.normalize("NFD", texto)
            if unicodedata.category(letra) != "Mn"
        )
