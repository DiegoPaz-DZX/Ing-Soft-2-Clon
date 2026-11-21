from abc import ABC, abstractmethod


class RepositorioTokensRevocados(ABC):
    @abstractmethod
    def revocar(self, huella, expira_en):
        pass

    @abstractmethod
    def esta_revocado(self, huella, ahora):
        pass

    @abstractmethod
    def eliminar_expirados(self, ahora):
        pass
