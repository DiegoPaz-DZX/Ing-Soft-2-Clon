from .CategoriaGasto import CategoriaGasto
from .RepositorioCategorias import RepositorioCategorias


class RepositorioCategoriasMemoria(RepositorioCategorias):
    def __init__(self):
        self._categorias = (
            CategoriaGasto("alimentacion", "Comida"),
            CategoriaGasto("transporte", "Transporte"),
            CategoriaGasto("servicios", "Servicios"),
            CategoriaGasto("entretenimiento", "Entretenimiento"),
            CategoriaGasto("salud", "Salud"),
            CategoriaGasto("educacion", "Educación"),
            CategoriaGasto("ahorro", "Ahorro"),
            CategoriaGasto("otros", "Otros"),
        )

    def listar_todas(self):
        return list(self._categorias)
