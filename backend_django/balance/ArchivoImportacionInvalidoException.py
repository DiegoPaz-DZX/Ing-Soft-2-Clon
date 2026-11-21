class ArchivoImportacionInvalidoException(Exception):
    def __init__(self, mensaje, errores=None):
        super().__init__(mensaje)
        self.errores = errores or []
