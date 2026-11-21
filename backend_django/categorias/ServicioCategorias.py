class ServicioCategorias:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def obtener_todas(self):
        return self._repositorio.listar_todas()
