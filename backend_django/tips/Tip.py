from dataclasses import dataclass


@dataclass(frozen=True)
class Tip:
    numero: int
    titulo: str
    contenido: str
