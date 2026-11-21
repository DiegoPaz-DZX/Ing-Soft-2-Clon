from dataclasses import dataclass


@dataclass(frozen=True)
class Recomendacion:
    id: str
    nivel: str
    titulo: str
    mensaje: str
    dato: str = ""