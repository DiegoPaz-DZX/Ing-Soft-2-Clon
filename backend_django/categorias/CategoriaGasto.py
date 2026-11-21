from dataclasses import dataclass


@dataclass(frozen=True)
class CategoriaGasto:
    codigo: str
    nombre: str
