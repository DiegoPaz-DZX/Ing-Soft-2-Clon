from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException
from .DatosMovimientoInvalidosException import DatosMovimientoInvalidosException
from .FabricaLectoresMovimientos import FabricaLectoresMovimientos
from .MontoInvalidoException import MontoInvalidoException
from .TipoMovimiento import TipoMovimiento


class ServicioImportacionMovimientos:
    TAMANO_MAXIMO = 5 * 1024 * 1024
    MAXIMO_FILAS = 500

    def __init__(self, repositorio, servicio_movimientos):
        self._repositorio = repositorio
        self._servicio_movimientos = servicio_movimientos

    def importar(self, cuenta, archivo):
        if archivo is None:
            raise ArchivoImportacionInvalidoException("Selecciona un archivo para importar.")
        if archivo.size > self.TAMANO_MAXIMO:
            raise ArchivoImportacionInvalidoException("El archivo no puede superar los 5 MB.")

        lector = FabricaLectoresMovimientos.crear(archivo.name)
        filas = lector.leer(archivo)
        if not filas:
            raise ArchivoImportacionInvalidoException("El archivo no contiene movimientos.")
        if len(filas) > self.MAXIMO_FILAS:
            raise ArchivoImportacionInvalidoException(
                f"Solo se pueden importar {self.MAXIMO_FILAS} movimientos a la vez."
            )

        movimientos = []
        errores = []
        for numero, datos in filas:
            try:
                movimiento = self._servicio_movimientos.preparar_movimiento(
                    cuenta,
                    datos.get("tipo"),
                    datos.get("monto"),
                    datos.get("fecha"),
                    datos.get("descripcion", ""),
                    categoria=datos.get("categoria", ""),
                    moneda=datos.get("moneda", "PEN"),
                )
                if movimiento.tipo == TipoMovimiento.GASTO and not movimiento.categoria:
                    raise ValueError("Los gastos deben tener una categoría")
                movimientos.append(movimiento)
            except (DatosMovimientoInvalidosException, MontoInvalidoException, ValueError) as error:
                errores.append({"fila": numero, "error": str(error)})

        if errores:
            raise ArchivoImportacionInvalidoException(
                "Hay filas que deben corregirse antes de importar.", errores
            )

        self._repositorio.agregar_varios(movimientos)
        return movimientos
