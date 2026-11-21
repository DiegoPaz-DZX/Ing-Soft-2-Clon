from dataclasses import dataclass


@dataclass(frozen=True)
class PreferenciaActual:
    divisa: object
    opciones: list
    tipo_cambio: object
