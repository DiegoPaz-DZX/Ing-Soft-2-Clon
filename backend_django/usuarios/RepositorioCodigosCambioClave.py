from abc import ABC, abstractmethod


class RepositorioCodigosCambioClave(ABC):
    @abstractmethod
    def invalidar_activos(self, cuenta):
        pass

    @abstractmethod
    def crear(self, cuenta, codigo_hash, expira_en):
        pass

    @abstractmethod
    def obtener_pendiente(self, cuenta):
        pass

    @abstractmethod
    def guardar_intentos(self, solicitud):
        pass

    @abstractmethod
    def marcar_usado(self, solicitud):
        pass
