class ServicioTips:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def obtener_todos(self):
        return list(self._repositorio.listar_todos())
